import random

from pytmx.util_pygame import load_pygame

from character import Character
from groups import AllSprites
from paths import paths
from settings import *
from sprites import CollidableSprite, Enemy, Gun, Sprite


class Game:
    def __init__(self):
        self._setup()
        self.all_sprites = AllSprites()
        self.obstacles_group = pygame.sprite.Group()
        self.bullets_group = pygame.sprite.Group()
        self.enemies_group = pygame.sprite.Group()
        self.enemy_locations = []
        self._render_tiled_layers()
        self.bg_music = pygame.mixer.Sound(paths["audio"]["music"])
        self.bg_music.set_volume(0.5)
        self.bg_music.play(loops=-1)
        self.impact_sound = pygame.mixer.Sound(paths["audio"]["impact"])

    def gamelooop(self):
        enemy_types = ("bat", "blob", "skeleton")
        ENEMY_CREATED_EVENT = pygame.event.custom_type()
        pygame.time.set_timer(ENEMY_CREATED_EVENT, 600)
        self.bg_music.play()
        while self.is_running:
            delta = self.clock.tick(self.fps) / 1000
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.is_running = False
                if event.type == ENEMY_CREATED_EVENT:
                    Enemy(
                        random.choice(enemy_types),
                        random.choice(self.enemy_locations),
                        self.character,
                        self.obstacles_group,
                        self.enemies_group,
                        self.all_sprites,
                    )

            self.all_sprites.update(delta)

            self._handle_bullets_collisions()
            if self.character.is_alive:
                self._handle_character_collisions()

            self.screen.fill((225, 225, 255))
            self.all_sprites.draw(self.character.rect)
            pygame.display.update()

        pygame.quit()

    def _render_tiled_layers(self):
        tiled_map = load_pygame(paths["data"]["maps"]["world"])
        for x, y, image in tiled_map.get_layer_by_name("Ground").tiles():
            Sprite((x * TILE_SIZE, y * TILE_SIZE), image, self.all_sprites)
        for object in sorted(
            tiled_map.get_layer_by_name("Objects"),
            key=lambda object: object.y + object.height,
        ):
            CollidableSprite(
                (object.x, object.y),
                object.image,
                self.all_sprites,
                self.obstacles_group,
            )
        for object in tiled_map.get_layer_by_name("Collisions"):
            CollidableSprite.create_collision_box(
                (object.x, object.y),
                (object.width, object.height),
                self.all_sprites,
                self.obstacles_group,
            )
        for object in tiled_map.get_layer_by_name("Entities"):
            match object.name:
                case "Player":
                    self.character = Character(
                        (object.x, object.y), self.obstacles_group, self.all_sprites
                    )
                    self.all_sprites.top_sprites.append(
                        Gun(self.character, 140, self.bullets_group, self.all_sprites)
                    )
                case "Enemy":
                    self.enemy_locations.append((object.x, object.y))

    def _setup(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self._set_caption("Vampire Survivor")
        self.fps = 60
        self.clock = pygame.time.Clock()
        self.is_running = True

    def _set_caption(self, caption):
        pygame.display.set_caption(caption)

    def _handle_bullets_collisions(self):
        for bullet in self.bullets_group:
            collided_list = pygame.sprite.spritecollide(
                bullet,
                self.enemies_group,
                False,
                collided=pygame.sprite.collide_mask,
            )
            for enemy in collided_list:
                enemy.destroy()
            if collided_list:
                self.impact_sound.play()
                bullet.kill()

    def _handle_character_collisions(self):
        collided_list = pygame.sprite.spritecollide(
            self.character,
            self.enemies_group,
            False,
            collided=pygame.sprite.collide_mask,
        )
        if collided_list:
            self.character.destroy()


if __name__ == "__main__":
    game = Game()
    game.gamelooop()
