from sprite_object import *

class ObjectHandler:
    def __init__(self, game):
        self.game = game
        self.sprite_list = []
        self.static_sprite_path = 'resources/sprites/static_sprites/'
        self.animated_sprite_path = 'resources/sprites/animated_sprites'
        add_sprite = self.add_sprite

        # A sprite map will allow us to display layers of sprites on a grid
        # thus we will use 1 big image as opposed to 100s of small images
        add_sprite(SpriteObject(game))
        add_sprite(AnimatedSprite(game))

    def update(self):
        [sprite.update() for sprite in self.sprite_list]

    def add_sprite(self, sprite):
        self.sprite_list.append(sprite)
