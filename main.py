import pygame as pg
import sys
from settings import *
from map import *
from player import *
from raycasting import *
from object_renderer import *
from enemy import Enemy
from weapon import Weapon
import math
import random

pg.mixer.init()

class Game:
    """Main game class handling state, updates, and rendering."""
    def __init__(self):
        pg.init()
        pg.mouse.set_visible(False)
        self.screen = pg.display.set_mode(RES)
        self.clock = pg.time.Clock()
        self.delta_time = 1
        self.state = "menu"
        self.new_game()
    
    def new_game(self):
        """Initialize or reset all game objects and state."""
        self.map = Map(self)
        self.player = Player(self)
        self.object_renderer = ObjectRenderer(self)
        self.raycasting = RayCasting(self)
        self.weapon = Weapon(self)
        self.wave = 1
        self.spawn_wave()

    def update(self):
        """Update all game logic for the current frame."""
        if self.state == "game":
            if self.player.health <= 0:
                self.intermission("Game Over! Restarting from Wave 1...")
                self.wave = 1
                self.player.health = PLAYER_MAX_HEALTH
                self.spawn_wave()
                return

            self.player.update()
            self.weapon.update()
            if self.player.shot and not self.weapon.reloading:
                self.handle_shot()
                self.player.shot = False
            for enemy in self.enemies:
                enemy.update()
            self.enemies = [enemy for enemy in self.enemies if enemy.health > 0]
            self.enemies_remaining = len(self.enemies)
            if self.enemies_remaining == 0:
                self.intermission("Next Wave!")
                self.wave += 1
                self.spawn_wave()
            self.raycasting.update()
            pg.display.flip()
            self.delta_time = self.clock.tick(FPS)
            pg.display.set_caption(f'{self.clock.get_fps() :.1f}')

    def handle_shot(self):
        """Handle logic for when the player fires their weapon."""
        min_angle = 0.2
        min_distance = float('inf')
        target_enemy = None
        px, py = self.player.x, self.player.y
        pa = self.player.angle
        num_rays = getattr(self.raycasting, "num_rays", self.screen.get_width())
        ray_casting_result = getattr(self.raycasting, "ray_casting_result", [])

        for enemy in self.enemies:
            dx = enemy.x - px
            dy = enemy.y - py
            distance = (dx ** 2 + dy ** 2) ** 0.5
            angle = abs((math.atan2(dy, dx) - pa + math.pi) % (2 * math.pi) - math.pi)
            if angle < min_angle and distance < min_distance and enemy.health > 0:
                half_fov = math.pi / 6
                if ray_casting_result and num_rays:
                    rel_angle = math.atan2(dy, dx) - pa
                    while rel_angle > math.pi:
                        rel_angle -= 2 * math.pi
                    while rel_angle < -math.pi:
                        rel_angle += 2 * math.pi
                    ray_index = int((rel_angle + half_fov) / (2 * half_fov) * num_rays)
                    ray_index = max(0, min(ray_index, num_rays - 1))
                    if 0 <= ray_index < len(ray_casting_result):
                        wall_dist = ray_casting_result[ray_index][0]
                        if distance < wall_dist:
                            min_distance = distance
                            target_enemy = enemy
                else:
                    min_distance = distance
                    target_enemy = enemy

        if target_enemy:
            target_enemy.take_damage(self.weapon.damage)
        self.player.shot = False

    def draw(self): 
        """Draw all game elements to the screen."""
        if self.state == "game":
            self.screen.fill('black')
            self.object_renderer.draw()
            self.weapon.draw()
            # Draw player health bar
            bar_width = 200
            bar_height = 20
            health_ratio = self.player.health / PLAYER_MAX_HEALTH
            pg.draw.rect(self.screen, (60, 60, 60), (20, 20, bar_width, bar_height))
            pg.draw.rect(self.screen, (200, 0, 0), (20, 20, int(bar_width * health_ratio), bar_height))
            # Draw wave and enemies remaining
            font = pg.font.SysFont('Arial', 30)
            wave_text = font.render(f"Wave: {self.wave}", True, (255, 255, 255))
            enemies_text = font.render(f"Enemies: {self.enemies_remaining}", True, (255, 255, 255))
            self.screen.blit(wave_text, (20, 50))
            self.screen.blit(enemies_text, (20, 80))
        elif self.state == "menu":
            self.draw_menu()

    def draw_menu(self):
        """Draw the main menu screen."""
        self.screen.fill((0, 0, 0))
        font = pg.font.SysFont('Arial', 80)
        title = font.render("Doom: Lion's Arena", True, (255, 255, 0))
        start_font = pg.font.SysFont('Arial', 50)
        start = start_font.render("Press ENTER to Start", True, (255, 255, 255))
        quit_ = start_font.render("Press Q to Quit", True, (255, 255, 255))
        self.screen.blit(title, (self.screen.get_width() // 2 - title.get_width() // 2, 200))
        self.screen.blit(start, (self.screen.get_width() // 2 - start.get_width() // 2, 400))
        self.screen.blit(quit_, (self.screen.get_width() // 2 - quit_.get_width() // 2, 500))
        pg.display.flip()

    def check_events(self):
        """Handle all user input and system events."""
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            if event.type == pg.KEYDOWN:
                if self.state == "menu":
                    if event.key == pg.K_RETURN:
                        self.state = "game"
                    elif event.key == pg.K_q:
                        pg.quit()
                        sys.exit()
                elif self.state == "game":
                    if event.key == pg.K_ESCAPE:
                        self.menu_loop()
                    if event.key == pg.K_SPACE or event.type == pg.MOUSEBUTTONDOWN:
                        self.player.shot = True
                        self.weapon.reloading = True
            if event.type == pg.MOUSEBUTTONDOWN:
                self.player.shot = True
                self.weapon.reloading = True

    def spawn_wave(self):
        """Spawn a new wave of enemies and reset player health."""
        self.enemies = []
        map_rows = self.map.rows
        map_cols = self.map.cols
        possible_spawns = []
        for y in range(map_rows // 2, map_rows - 2):
            for x in range(map_cols // 2, map_cols - 2):
                if (x, y) not in self.map.world_map:
                    possible_spawns.append((x + 0.5, y + 0.5))
        random.shuffle(possible_spawns)
        for i in range(self.wave * 2):
            if possible_spawns:
                x, y = possible_spawns.pop()
                self.enemies.append(Enemy(self, x, y))
        self.enemies_remaining = len(self.enemies)
        self.player.health = PLAYER_MAX_HEALTH

    def intermission(self, message):
        """Display a message between waves or on game over."""
        font = pg.font.SysFont('Arial', 60)
        text = font.render(message, True, (255, 255, 0))
        rect = text.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2))
        self.screen.fill((0, 0, 0))
        self.screen.blit(text, rect)
        pg.display.flip()
        pg.time.delay(3000)

    def menu_loop(self):
        """Display and handle the main menu loop."""
        self.menu_active = True
        while self.menu_active:
            self.draw_menu()
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_RETURN:
                        self.menu_active = False
                    if event.key == pg.K_q:
                        pg.quit()
                        sys.exit()
            self.clock.tick(60)

    def run(self):
        """Main game loop."""
        self.menu_loop()
        while True:
            self.check_events()
            self.update()
            self.draw()

if __name__ == '__main__':
    game = Game()
    game.run()
