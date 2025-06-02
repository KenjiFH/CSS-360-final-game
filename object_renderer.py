import math
import pygame as pg
from settings import *
import os, sys

BASE_PATH = getattr(sys, '_MEIPASS', os.path.abspath("."))


class ObjectRenderer:
    """Handles drawing all objects (walls, enemies, player weapon) to the screen."""

    def __init__(self, game):
        self.game = game
        self.screen = game.screen
        self.wall_textures = self.load_wall_texures()
        self.sky_image = self.get_texture('resources/textures/sky.png', (WIDTH, HALF_HEIGHT))
        self.sky_offset = 0
        self.blood_screen = self.get_texture('resources/textures/blood_screen.png', (WIDTH, HEIGHT))

    def draw(self):
        self.draw_background()
        self.render_game_objects()
        self.draw_enemies()

    def player_damage(self):
        self.screen.blit(self.blood_screen, (0, 0))

    def draw_background(self):
        self.sky_offset = (self.sky_offset + 4.5 * self.game.player.rel) % WIDTH
        self.screen.blit(self.sky_image, (-self.sky_offset, 0))
        self.screen.blit(self.sky_image, (-self.sky_offset + WIDTH, 0))
        pg.draw.rect(self.screen, FLOOR_COLOR, (0, HALF_HEIGHT, WIDTH, HEIGHT))

    def render_game_objects(self):
        list_objects = self.game.raycasting.objects_to_render
        for depth, image, pos in list_objects:
            self.screen.blit(image, pos)

    def draw_enemies(self):
        player = self.game.player
        half_fov = math.pi / 6
        num_rays = getattr(self.game.raycasting, "num_rays", WIDTH)
        ray_casting_result = getattr(self.game.raycasting, "ray_casting_result", [])

        enemies = sorted(self.game.enemies, key=lambda e: -((e.x - player.x) ** 2 + (e.y - player.y) ** 2))
        for enemy in enemies:
            dx = enemy.x - player.x
            dy = enemy.y - player.y
            distance = math.hypot(dx, dy)
            angle = math.atan2(dy, dx) - player.angle

            while angle > math.pi:
                angle -= 2 * math.pi
            while angle < -math.pi:
                angle += 2 * math.pi

            if -half_fov < angle < half_fov:
                proj_height = min(self.game.screen.get_height(),
                                  int(HEIGHT / (distance * math.cos(angle) + 0.0001) * 1.8))
                sprite = pg.transform.scale(enemy.current_image, (proj_height, proj_height))
                screen_x = self.game.screen.get_width() // 2 + int(
                    math.tan(angle) * self.game.screen.get_width() // 2) - proj_height // 2
                screen_y = HALF_HEIGHT + proj_height // 2 - proj_height

                # --- OCCLUSION CHECK ---
                if ray_casting_result and num_rays:
                    ray_index = int((angle + half_fov) / (2 * half_fov) * num_rays)
                    ray_index = max(0, min(ray_index, num_rays - 1))
                    if 0 <= ray_index < len(ray_casting_result):
                        wall_dist = ray_casting_result[ray_index][0]
                        if distance < wall_dist:
                            self.game.screen.blit(sprite, (screen_x, screen_y))
                else:
                    self.game.screen.blit(sprite, (screen_x, screen_y))

                # Draw enemy health bar above the sprite
                # Removed since bar shows through walls
                """
                bar_width = proj_height
                bar_height = 7
                health_ratio = enemy.health / enemy.max_health
                bar_x = screen_x
                bar_y = screen_y - bar_height - 4
                pg.draw.rect(self.game.screen, (60, 60, 60), (bar_x, bar_y, bar_width, bar_height))
                pg.draw.rect(self.game.screen, (0, 200, 0), (bar_x, bar_y, int(bar_width * health_ratio), bar_height))
                """

    @staticmethod
    def get_texture(path, res=(TEXTURE_SIZE, TEXTURE_SIZE)):
        texture = pg.image.load(path).convert_alpha()
        return pg.transform.scale(texture, res)

    def load_wall_texures(self):
        return {
            1: self.get_texture('resources/textures/1.png'),
            2: self.get_texture('resources/textures/2.png'),
            3: self.get_texture('resources/textures/3.png'),
            4: self.get_texture('resources/textures/4.png'),
            5: self.get_texture('resources/textures/5.png')
        }