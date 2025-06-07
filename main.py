import pygame as pg
import sys
from settings import *
from map import *
from player import *
from raycasting import *
from object_renderer import *
from enemy import Enemy
from weapon import Weapon
from sound import *
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
        self.sound = Sound(self)
        pg.mixer.music.play(-1)
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
        """Draw the main menu screen or pause menu."""
        self.screen.fill((0, 0, 0))
        font = pg.font.SysFont('Arial', 80)
        title = font.render("Doom: Lion's Arena", True, (255, 255, 0))
        # title at the top
        self.screen.blit(title, (self.screen.get_width() // 2 - title.get_width() // 2, 60))
        # Info for top left
        info_font = pg.font.SysFont('Arial', 40)
        wave_text = info_font.render(f"Wave: {getattr(self, 'wave', 1)}", True, (255, 255, 255))
        enemies_text = info_font.render(f"Enemies: {getattr(self, 'enemies_remaining', 0)}", True, (255, 255, 255))
        self.screen.blit(wave_text, (20, 20))
        self.screen.blit(enemies_text, (20, 60))
        # Instructions for top right
        instr_font = pg.font.SysFont('Arial', 32)
        instr_r = instr_font.render("Press R to Restart Current Wave", True, (200, 200, 0))
        instr_enter = instr_font.render("Press ENTER to Resume", True, (200, 200, 0))
        instr_q = instr_font.render("Press Q to Quit", True, (200, 200, 0))
        instr_esc = instr_font.render("Press ESC anytime to pause", True, (200, 200, 0))
        screen_w = self.screen.get_width()
        self.screen.blit(instr_r, (screen_w - instr_r.get_width() - 20, 20))
        self.screen.blit(instr_enter, (screen_w - instr_enter.get_width() - 20, 60))
        self.screen.blit(instr_q, (screen_w - instr_q.get_width() - 20, 100))
        self.screen.blit(instr_esc, (screen_w - instr_esc.get_width() - 20, 140))
        # Game instructions 
        desc_font = pg.font.SysFont('Arial', 32)
        desc1 = desc_font.render("The goal is to eliminate enemies and advance waves.", True, (180, 180, 180))
        desc2 = desc_font.render("The waves will get harder each time. Good luck!", True, (180, 180, 180))
        self.screen.blit(desc1, (self.screen.get_width() // 2 - desc1.get_width() // 2, 200))
        self.screen.blit(desc2, (self.screen.get_width() // 2 - desc2.get_width() // 2, 240))
        pg.display.flip()

    def check_events(self):
        """Handle all user input and system events."""
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            if event.type == pg.KEYDOWN:
                if self.state == "menu":
                    pass  
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
        # Get all reachable tiles from player start
        player_tile = (int(self.player.x), int(self.player.y))
        reachable = self.get_reachable_tiles(*player_tile)
        possible_spawns = [(x + 0.5, y + 0.5) for (x, y) in reachable if (x, y) != player_tile]
        random.shuffle(possible_spawns)
        num_to_spawn = min(self.wave * 2, len(possible_spawns))
        for i in range(num_to_spawn):
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
        # Make user not move during intermission/potential fix for the weird map glitch
        pg.event.clear()  

    def reset_player(self):
        """Reset player position and health to the starting location."""
        if hasattr(self.player, 'start_x') and hasattr(self.player, 'start_y'):
            self.player.x = self.player.start_x
            self.player.y = self.player.start_y
        else:
            # Default to center or a known good spawn
            self.player.x = 1.5
            self.player.y = 1.5
        self.player.angle = 0
        self.player.health = PLAYER_MAX_HEALTH

    def menu_loop(self):
        """Display and handle the main menu loop or pause menu."""
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
                        self.state = "game"
                    if event.key == pg.K_r:
                        self.reset_player()      # Reset player position/health
                        self.spawn_wave()        # Respawn enemies for current wave
                        self.menu_active = False
                        self.state = "game"
                    if event.key == pg.K_q:
                        pg.quit()
                        sys.exit()
            self.clock.tick(60)

    def run(self):
        """Main game loop."""
        self.menu_loop()
        pg.event.clear()
        while True:
            self.check_events()
            self.update()
            self.draw()

    def get_reachable_tiles(self, start_x, start_y):
        """Return a set of all empty tiles reachable from (start_x, start_y)."""
        from collections import deque
        visited = set()
        queue = deque()
        sx, sy = int(start_x), int(start_y)
        queue.append((sx, sy))
        visited.add((sx, sy))
        map_rows = self.map.rows
        map_cols = self.map.cols

        while queue:
            x, y = queue.popleft()
            for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
                nx, ny = x+dx, y+dy
                if (0 <= nx < map_cols and 0 <= ny < map_rows and
                    (nx, ny) not in self.map.world_map and
                    (nx, ny) not in visited):
                    visited.add((nx, ny))
                    queue.append((nx, ny))
        return visited

if __name__ == '__main__':
    game = Game()
    game.run()