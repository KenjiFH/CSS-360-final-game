import pygame as pg
from collections import deque
from settings import *
from sound import *

class Weapon:
    """Handles weapon state, animation, and sound."""
    def __init__(self, game, path='resources/sprites/shotgun', scale=3.0, animation_time=90):
        self.game = game
        self.images = deque()
        # Load all images in the weapon folder
        for i in range(1, 7):  
            img = pg.image.load(f'{path}/{i}.png').convert_alpha()
            w, h = img.get_width(), img.get_height()
            img = pg.transform.smoothscale(img, (int(w * scale), int(h * scale)))
            self.images.append(img)
        self.weapon_pos = (HALF_WIDTH - self.images[0].get_width() // 2, HEIGHT - self.images[0].get_height())
        self.reloading = False
        self.num_images = len(self.images)
        self.frame_counter = 0
        self.idle_image = self.images[-1]
        self.image = self.idle_image
        self.damage = 25
        self.animation_time = animation_time
        self.animation_time_prev = pg.time.get_ticks()
        self.animation_trigger = False
        ## self.shot_sound = pg.mixer.Sound('resources/sound/shotgun.wav')  # MOVED TO sound.py

    def check_animation_time(self):
        """Check if it's time to advance the weapon animation."""
        self.animation_trigger = False
        time_now = pg.time.get_ticks()
        if time_now - self.animation_time_prev > self.animation_time:
            self.animation_time_prev = time_now
            self.animation_trigger = True

    def animate_shot(self):
        """Animate the weapon firing sequence."""
        if self.reloading:
            if self.animation_trigger:
                self.image = self.images[self.frame_counter]
                self.frame_counter += 1
                if self.frame_counter == self.num_images:
                    self.reloading = False
                    self.frame_counter = 0
                    self.image = self.idle_image

    def draw(self):
        """Draw the weapon on the screen."""
        self.game.screen.blit(self.image, self.weapon_pos)

    def update(self):
        """Update weapon animation and play sound if firing."""
        self.check_animation_time()
        if self.reloading and self.frame_counter == 0 and self.animation_trigger:
            self.game.sound.shotgun.play()
        self.animate_shot()