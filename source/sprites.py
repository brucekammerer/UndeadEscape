from math import atan2, degrees

from paths import paths
from settings import *


class CollidableSprite(pygame.sprite.Sprite):
    def __init__(self, pos, image, *groups):
        super().__init__(*groups)
        self.image = image
        self.rect = self.image.get_frect(topleft=pos)
        self.sortable = True

    @classmethod
    def create_collision_box(cls, pos, size, *groups):
        image = pygame.Surface(size, flags=pygame.SRCALPHA)
        image.fill((0, 0, 0, 0))
        return cls(pos, image, *groups)


class Sprite(pygame.sprite.Sprite):
    def __init__(self, pos, image, *groups):
        super().__init__(*groups)
        self.image = image
        self.rect = self.image.get_frect(topleft=pos)
        self.sortable = False


class Gun(pygame.sprite.Sprite):
    def __init__(self, character, distance, bullets_group, *groups):
        super().__init__(*groups)
        self.bullets_group = bullets_group
        self.groups = groups
        self.distance = distance
        self.pivot = pygame.Vector2(WIDTH / 2, HEIGHT / 2)
        self.character = character
        self.original_image = pygame.image.load(
            paths["images"]["gun"]["gun"]
        ).convert_alpha()
        self.image = self.original_image
        self.direction = pygame.Vector2(1, 0)
        self.rect = self.image.get_rect(
            center=self.character.rect.center + self.direction * self.distance
        )
        self.can_shoot = True
        self.shot_at = 0
        self.cooldown_duration = 100
        self.sortable = True  # to think about
        self.shoot_sound = pygame.mixer.Sound(paths["audio"]["shoot"])

    def update(self, _):
        if self.character.is_alive:
            self._set_direction()
            angle = -self._get_angle()
            self._transform(angle)
            self._set_position()
            self._handle_shooting(angle, distance=222)

    def _handle_shooting(self, angle, distance):
        if self.can_shoot:
            mouse_left_pressed = pygame.mouse.get_pressed()[0]
            if mouse_left_pressed:
                self.can_shoot = False
                self.shot_at = pygame.time.get_ticks()
                self._shoot(angle, distance)
        else:
            if pygame.time.get_ticks() - self.shot_at > self.cooldown_duration:
                self.can_shoot = True

    def _shoot(self, angle, distance):
        self.shoot_sound.play()
        Bullet(
            self.character.rect.center,
            self.direction,
            angle,
            distance,
            self.bullets_group,
            *self.groups,
        )

    def _set_direction(self):
        direction = pygame.Vector2(pygame.mouse.get_pos()) - self.pivot
        self.direction = direction.normalize() if direction else direction

    def _transform(self, angle):
        self.image = pygame.transform.rotozoom(self.original_image, angle, 1)
        if self.direction.x < 0:
            self.image = pygame.transform.flip(self.image, True, False)

    def _get_angle(self):
        angle = degrees(atan2(self.direction.y, self.direction.x))
        return -180 - angle if self.direction.x < 0 else angle

    def _set_position(self):
        pos = self.character.rect.center + self.direction * self.distance
        self.rect = self.image.get_rect(center=pos)


class Bullet(pygame.sprite.Sprite):
    def __init__(self, center, direction, angle, distance, *groups):
        super().__init__(*groups)
        self.image = pygame.image.load(
            paths["images"]["gun"]["bullet2"]
        ).convert_alpha()
        self.direction = direction
        self._transform(angle)
        self._set_rect(center, distance)
        self.velocity = 800
        self.sortable = True  # to think about
        self.created_at = pygame.time.get_ticks()
        self.lifetime = 1000

    def update(self, delta):
        self._handle_kill()
        self.rect.center += self.direction * self.velocity * delta

    def _transform(self, angle):
        self.image = pygame.transform.rotozoom(self.image, angle, 1)
        if self.direction.x < 0:
            self.image = pygame.transform.flip(self.image, True, False)

    def _set_rect(self, center, distance):
        pos = center + self.direction * distance
        self.rect = self.image.get_rect(center=pos)

    def _handle_kill(self):
        if pygame.time.get_ticks() - self.created_at > self.lifetime:
            self.kill()


class Enemy(pygame.sprite.Sprite):
    def __init__(self, enemy_type, pos, character, obstacles_group, *groups):
        super().__init__(*groups)
        self.type = enemy_type
        self.character = character
        self.obstacles_group = obstacles_group
        self.frames = []
        self._load_frames()
        self.image = self.frames[0]
        self.rect = self.image.get_frect(topleft=pos)
        self.hitbox = self.rect.inflate(-20, -40)
        self.sortable = True
        self.frame_rate = 10
        self.frame_index = 0
        self.velocity = 200
        self.death_duration = 200
        self.death_time = 0
        self.is_alive = True

    def _load_frames(self):
        paths_dict = paths["images"]["enemies"][self.type]
        for index in sorted(paths_dict.keys(), key=int):
            self.frames.append(pygame.image.load(paths_dict[index]).convert_alpha())

    def update(self, delta):
        if self.is_alive:
            self._move(delta)
            self._animate(delta)
        else:
            self._handle_destroy()

    def _move(self, delta):
        direction = pygame.Vector2(self.character.rect.center) - pygame.Vector2(
            self.hitbox.center
        )
        if direction:
            direction = direction.normalize()
            self.hitbox.x += direction.x * self.velocity * delta
            self._handle_horizontal_collisions(direction)
            self.hitbox.y += direction.y * self.velocity * delta
            self._handle_vertical_collisions(direction)
            self.rect.center = self.hitbox.center

    def _handle_horizontal_collisions(self, direction):
        for obstacle in self.obstacles_group:
            if self.hitbox.colliderect(obstacle.rect):
                if direction.x > 0:
                    self.hitbox.right = obstacle.rect.left
                elif direction.x < 0:
                    self.hitbox.left = obstacle.rect.right

    def _handle_vertical_collisions(self, direction):
        for obstacle in self.obstacles_group:
            if self.hitbox.colliderect(obstacle.rect):
                if direction.y > 0:
                    self.hitbox.bottom = obstacle.rect.top
                elif direction.y < 0:
                    self.hitbox.top = obstacle.rect.bottom

    def _animate(self, delta):
        self.frame_index += self.frame_rate * delta
        index = int(self.frame_index) % len(self.frames)
        self.image = self.frames[index]

    def destroy(self):
        self.death_time = pygame.time.get_ticks()
        mask_surf = pygame.mask.from_surface(self.frames[0]).to_surface()
        mask_surf.set_colorkey("black")
        self.image = mask_surf
        self.is_alive = False

    def _handle_destroy(self):
        if pygame.time.get_ticks() - self.death_time > self.death_duration:
            self.kill()
