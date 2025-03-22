import pygame
from os.path import join 

from settings import *
from player import Player
from sprites import *
from groups import AllSprites
from random import randint
from pytmx.util_pygame import load_pygame

class Game(pygame.sprite.Sprite):
    def __init__(self, *groups):
        super().__init__(*groups)
        
        #setup
        pygame.init()   
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption('Vampires Arise')
        self.running = True
        self.clock = pygame.time.Clock()

        #groups
        self.all_sprites = AllSprites()
        self.collision_sprites = pygame.sprite.Group()

        self.setup()

    #loading maps and displaying them
    def setup(self): 
        map = load_pygame(join('data', 'maps', 'world.tmx'))
        for x, y, image in map.get_layer_by_name('Ground').tiles():
            Sprite((x * TILE_SIZE, y * TILE_SIZE), image, self.all_sprites)

        for obj in map.get_layer_by_name('Objects'):
            ColliisionSprite((obj.x, obj.y), obj.image, (self.all_sprites, self.collision_sprites))

        for obj in map.get_layer_by_name('Collisions'):
            ColliisionSprite((obj.x, obj.y), pygame.Surface((obj.width, obj.height)), (self.collision_sprites))

        for obj in map.get_layer_by_name('Entities'):
            if obj.name == 'Player':
                self.player = Player((obj.x,obj.y), self.all_sprites, collision_sprites=self.collision_sprites)

    def run(self):
        while self.running: 
            dt =  self.clock.tick() / 1000 #delta time in seconds

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            self.all_sprites.update(dt)
            
            #background
            self.display_surface.fill('#3a2e3f')
            self.all_sprites.draw(self.player.rect.center)

            pygame.display.flip()

        pygame.quit()

if __name__ == '__main__':
    game = Game()
    game.run()