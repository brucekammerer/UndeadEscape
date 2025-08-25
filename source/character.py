import sys

from paths import paths
from settings import *


class Character(pygame.sprite.Sprite):
    def __init__(self, pos, obstacles_group, *groups):
        super().__init__(*groups)
        self.obstacles_group = obstacles_group
        self.frames = {}
        self._load_images()
        self.image = self.frames["down"][0]
        self.rect = self.image.get_rect(center=pos)
        self.hitbox = self.rect.inflate(-60, -90)
        self.direction = pygame.Vector2(0, 0)
        self.velocity = 500
        self.sortable = True
        self.frame_rate = 5
        self.frame_index = 0
        self.state = "down"
        self.death_duration = 1000
        self.death_time = 0
        self.is_alive = True

    def update(self, delta):
        if self.is_alive:
            self._handle_input()
            self._move(delta)
            self._animate(delta)
        else:
            self._handle_destroy()

    def _animate(self, delta):
        match tuple(self.direction):
            case (_, y) if y > 0:
                self.state = "down"
            case (_, y) if y < 0:
                self.state = "up"
        match tuple(self.direction):
            case (x, _) if x > 0:
                self.state = "right"
            case (x, _) if x < 0:
                self.state = "left"
        frames = self.frames[self.state]
        if self.direction:
            self.frame_index += self.frame_rate * delta
            index = int(self.frame_index) % len(frames)
        else:
            index = 0
        self.image = frames[index]

    def _load_images(self):
        for direction in ("left", "right", "up", "down"):
            self.frames[direction] = []
            direction_dict = paths["images"]["player"][direction]
            for dict_key in sorted(direction_dict.keys(), key=int):
                path = direction_dict[dict_key]
                surf = pygame.image.load(path).convert_alpha()
                self.frames[direction].append(surf)

    def _handle_input(self):
        pressed_list = pygame.key.get_pressed()
        self.direction.x = int(pressed_list[pygame.K_d]) - int(pressed_list[pygame.K_a])
        self.direction.y = int(pressed_list[pygame.K_s]) - int(pressed_list[pygame.K_w])
        if self.direction:
            self.direction = self.direction.normalize()

    def _move(self, delta):
        self.hitbox.x += self.direction.x * self.velocity * delta
        self._handle_horizontal_collisions()
        self.hitbox.y += self.direction.y * self.velocity * delta
        self._handle_vertical_collisions()
        self.rect.center = self.hitbox.center

    def _handle_horizontal_collisions(self):
        for obstacle in self.obstacles_group:
            if self.hitbox.colliderect(obstacle.rect):
                if self.direction.x > 0:
                    self.hitbox.right = obstacle.rect.left
                elif self.direction.x < 0:
                    self.hitbox.left = obstacle.rect.right

    def _handle_vertical_collisions(self):
        for obstacle in self.obstacles_group:
            if self.hitbox.colliderect(obstacle.rect):
                if self.direction.y > 0:
                    self.hitbox.bottom = obstacle.rect.top
                elif self.direction.y < 0:
                    self.hitbox.top = obstacle.rect.bottom

    def destroy(self):
        self.death_time = pygame.time.get_ticks()
        self.is_alive = False
        mask_surf = pygame.mask.from_surface(self.frames["down"][0]).to_surface()
        mask_surf.set_colorkey("black")
        self.image = mask_surf

    def _handle_destroy(self):
        if pygame.time.get_ticks() - self.death_time > self.death_duration:
            pygame.quit()
            sys.exit()
