import itertools

import pygame

from settings import *


class AllSprites(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.screen = pygame.display.get_surface()
        self.offset = pygame.Vector2()
        self.top_sprites = []

    def draw(self, target):
        self.offset.x = HALF_WIDTH - target.center[0]
        self.offset.y = HEIGHT / 2 - target.center[1]
        for sprite in itertools.chain(
            (sprite for sprite in self if not sprite.sortable),
            (sprite for sprite in self if sprite.sortable),
            self.top_sprites,
        ):
            self.screen.blit(sprite.image, sprite.rect.topleft + self.offset)
