import pygame as pg
import math
import os
import heapq
import random

class Enemy:
    """Enemy logic, movement, shooting, and animation."""
    def __init__(self, game, x, y):
        self.game = game
        self.x = x
        self.y = y
        self.max_health = 50
        self.health = 50
        self.speed = 0.002
        self.walk_frames = []
        walk_folder = 'resources/textures/enemy_walk'
        for fname in sorted(os.listdir(walk_folder)):
            if fname.endswith('.png'):
                img = pg.image.load(os.path.join(walk_folder, fname)).convert_alpha()
                self.walk_frames.append(img)
        self.current_frame = 0
        self.animation_time = 120
        self.last_anim_time = pg.time.get_ticks()
        self.path = []
        self.gun_accuracy = 0.5 # ideal % of shots that will hit the player for damage
        self.shoot_cooldown = 1000
        self.last_shot_time = 0
        self.damage = 5
        self.shot_sound = pg.mixer.Sound('resources/sound/shotgun.wav')
        self.muzzle_flash_time = 150
        self.muzzle_flash_timer = 0
        self.muzzle_flash_active = False
        self.image_idle = pg.image.load('resources/sprites/enemy_idle.png').convert_alpha()
        self.image_shoot = pg.image.load('resources/sprites/enemy_shoot.png').convert_alpha()
        self.current_image = self.image_idle

    @property
    def pos(self):
        return (self.x, self.y)

    def heuristic(self, a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def astar(self, start, goal):
        """A* pathfinding for enemy movement."""
        neighbors = [(0,1),(1,0),(0,-1),(-1,0)]
        close_set = set()
        came_from = {}
        gscore = {start:0}
        fscore = {start:self.heuristic(start, goal)}
        oheap = []
        heapq.heappush(oheap, (fscore[start], start))
        world_map = self.game.map.world_map

        while oheap:
            current = heapq.heappop(oheap)[1]
            if current == goal:
                data = []
                while current in came_from:
                    data.append(current)
                    current = came_from[current]
                return data[::-1]
            close_set.add(current)
            for i, j in neighbors:
                neighbor = current[0] + i, current[1] + j
                tentative_g_score = gscore[current] + 1
                if 0 <= neighbor[0] < self.game.map.cols and 0 <= neighbor[1] < self.game.map.rows:
                    if neighbor in world_map:
                        continue
                else:
                    continue
                if neighbor in close_set and tentative_g_score >= gscore.get(neighbor, 0):
                    continue
                if tentative_g_score < gscore.get(neighbor, 0) or neighbor not in [i[1] for i in oheap]:
                    came_from[neighbor] = current
                    gscore[neighbor] = tentative_g_score
                    fscore[neighbor] = tentative_g_score + self.heuristic(neighbor, goal)
                    heapq.heappush(oheap, (fscore[neighbor], neighbor))
        return []

    def update(self):
        """Update enemy movement, animation, and shooting."""
        now = pg.time.get_ticks()
        if not self.muzzle_flash_active:
            if now - self.last_anim_time > self.animation_time:
                self.current_frame = (self.current_frame + 1) % len(self.walk_frames)
                self.last_anim_time = now
            self.current_image = self.walk_frames[self.current_frame]
        else:
            self.current_image = self.image_shoot
            if now - self.muzzle_flash_timer > self.muzzle_flash_time:
                self.muzzle_flash_active = False
                self.current_image = self.walk_frames[self.current_frame]

        player_cell = (int(self.game.player.x), int(self.game.player.y))
        my_cell = (int(self.x), int(self.y))
        if not self.path or self.path[-1] != player_cell:
            self.path = self.astar(my_cell, player_cell)
        if self.path:
            target = self.path[0]
            dx = target[0] + 0.5 - self.x
            dy = target[1] + 0.5 - self.y
            dist = math.hypot(dx, dy)
            if dist > 0.05:
                move_dist = min(self.speed * self.game.delta_time, dist)
                self.x += (dx / dist) * move_dist
                self.y += (dy / dist) * move_dist
            else:
                self.x, self.y = target
                self.path.pop(0)

        self.try_shoot_player()

    def try_shoot_player(self):
        """Enemy attempts to shoot at the player if conditions are met."""
        now = pg.time.get_ticks()
        if now - self.last_shot_time > self.shoot_cooldown:
            dx = self.game.player.x - self.x
            dy = self.game.player.y - self.y
            distance = math.hypot(dx, dy)
            angle_to_player = math.atan2(dy, dx)
            enemy_facing_angle = angle_to_player + random.uniform(-0.3, 0.3)
            player_angle = math.atan2(self.game.player.y - self.y, self.game.player.x - self.x)
            angle_diff = abs((enemy_facing_angle - player_angle + math.pi) % (2 * math.pi) - math.pi)
            if angle_diff < 0.2 and distance < 10 and self.has_line_of_sight():
                self.shot_sound.play()
                self.muzzle_flash_active = True
                self.muzzle_flash_timer = now
                
                if random.random() < self.gun_accuracy: # Enemy should have a successful hit on 50% of their shots
                    self.game.player.take_damage(self.damage)
                if self.game.player.health < 0:
                    self.game.player.health = 0
            self.last_shot_time = now

    def take_damage(self, amount):
        """Reduce enemy health by the given amount."""
        self.game.sound.enemy_hurt.play()
        self.health -= amount
        if self.health < 0:
            self.health = 0

    def has_line_of_sight(self):
        """Check if there is a clear path to the player (no walls in between)."""
        x0, y0 = int(self.x), int(self.y)
        x1, y1 = int(self.game.player.x), int(self.game.player.y)
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        x, y = x0, y0
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        if dx > dy:
            err = dx / 2.0
            while x != x1:
                if (x, y) in self.game.map.world_map and (x, y) != (x0, y0) and (x, y) != (x1, y1):
                    return False
                err -= dy
                if err < 0:
                    y += sy
                    err += dx
                x += sx
        else:
            err = dy / 2.0
            while y != y1:
                if (x, y) in self.game.map.world_map and (x, y) != (x0, y0) and (x, y) != (x1, y1):
                    return False
                err -= dx
                if err < 0:
                    x += sx
                    err += dy
                y += sy
        return True