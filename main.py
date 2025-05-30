import pygame as pg
import sys
from settings import *
from map import *
from player import *
from raycasting import *
from object_renderer import *
from weapon import *
from sound import *

class Game:
    #Start Screen
    def start_screen(self):
        font = pg.font.SysFont('Arial', 70)
        small_font = pg.font.SysFont('Arial', 50)
        title = font.render('Start Screen', True, (255, 255, 255))
        prompt = small_font.render('Press key or mouse to continue', True, (255, 255, 255))

        while True:
            self.screen.fill((0, 0, 0))
            self.screen.blit(title, (HALF_WIDTH - title.get_width() // 2, HALF_HEIGHT - 100))
            self.screen.blit(prompt, (HALF_WIDTH - prompt.get_width() // 2, HALF_HEIGHT + 50))

            pg.display.flip()
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()
                elif event.type == pg.MOUSEBUTTONDOWN or event.type == pg.KEYDOWN:
                    return

    def __init__(self):
        pg.init()
        pg.mouse.set_visible(False)
        self.screen = pg.display.set_mode(RES)
        self.clock = pg.time.Clock()
        self.delta_time = 1
        self.new_game()
    
    def new_game(self):
        self.map = Map(self)
        self.player = Player(self)
        
        self.object_renderer = ObjectRenderer(self)
        self.raycasting = RayCasting(self)


        self.weapon = Weapon(self)
        self.sound = Sound(self)

    def update(self):
        self.player.update()
        self.raycasting.update()

        self.weapon.update()

        pg.display.flip()
        self.delta_time = self.clock.tick(FPS)
        pg.display.set_caption(f'{self.clock.get_fps() :.1f}')

    def draw(self): 
        self.screen.fill('black')
        self.object_renderer.draw()
        self.weapon.draw()
        #self.map.draw()
        #self.player.draw()

    def check_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            self.player.single_fire_event(event)

    def run(self):
        self.start_screen()
        while True:
            self.check_events()
            self.update()
            self.draw()

if __name__ == '__main__':
    game = Game()
    game.run()
