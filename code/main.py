import pygame
from os.path import join 

from settings import *
from player import Player
from sprites import *
from groups import AllSprites
from random import randint, choice
from pytmx.util_pygame import load_pygame

class Game(pygame.sprite.Sprite):
    def __init__(self, *groups):
        super().__init__(*groups)
        
        #setup
        pygame.mixer.pre_init()
        pygame.init()   
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption('Vampires Arise')
        self.running = True
        self.clock = pygame.time.Clock()
       
        #sounds
        self.impact_sound =  pygame.mixer.Sound(join('audio', 'impact.ogg'))
        self.shoot_sound =  pygame.mixer.Sound(join('audio', 'shoot.wav'))
        self.music_sound =  pygame.mixer.Sound(join('audio', 'music.wav'))
        self.music_sound.set_volume(0.2)
        self.music_sound.play(-1)
        
        #groups
        self.all_sprites = AllSprites()
        self.collision_sprites = pygame.sprite.Group()
        self.bullet_sprites = pygame.sprite.Group()
        self.enemy_sprites = pygame.sprite.Group()

        #gun timer
        self.can_shoot = True
        self.shoot_time = 0
        self.gun_cooldown = 200

        #enemy timer
        self.enemy_event = pygame.event.custom_type()
        pygame.time.set_timer(self.enemy_event, 500)
        self.spawn_positions = []

        self.load_images()
        self.setup()

    def load_images(self):
        self.bullet_surf = pygame.image.load(join('images', 'gun', 'bullet.png')).convert_alpha()

        folders = list(walk(join('images', 'enemies')))[0][1]
        self.enemy_frames = {}

        for folder in folders:
            for folder_path, _, file_names in walk(join('images', 'enemies', folder)):
                self.enemy_frames[folder] = []
                for file_name in sorted(file_names, key= lambda name: int(name.split('.')[0])):
                    full_path = join(folder_path, file_name)
                    surf = pygame.image.load(full_path).convert_alpha()
                    self.enemy_frames[folder].append(surf)
        
    def input(self):
        if pygame.mouse.get_pressed()[0] and self.can_shoot:
            pos = self.gun.rect.center + self.gun.player_direction * 50
            Bullet(self.bullet_surf, pos, self.gun.player_direction, (self.all_sprites, self.bullet_sprites))
            self.shoot_sound.play()
            self.can_shoot = False
            self.shoot_time = pygame.time.get_ticks()

    def gun_timer(self):
        if not self.can_shoot:
            current_time = pygame.time.get_ticks()
            if current_time - self.shoot_time >= self.gun_cooldown:
                self.can_shoot = True

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
                self.gun = Gun(self.player, self.all_sprites)
            else:
                self.spawn_positions.append((obj.x, obj.y)) #Enemy spawn points
    
    def kill_monster_collisions(self):
        if self.bullet_sprites:
            for bullet in self.bullet_sprites:
                collided_sprites = pygame.sprite.spritecollide(bullet, self.enemy_sprites, False, pygame.sprite.collide_mask)
                if collided_sprites:
                    for sprite in collided_sprites:
                        sprite.destroy()
                        self.impact_sound.play()
                    bullet.kill()    

    def player_collision(self):
        if pygame.sprite.spritecollide(self.player, self.enemy_sprites, False, pygame.sprite.collide_mask):
            self.running = False

    def run(self):
        while self.running: 
            dt =  self.clock.tick() / 1000 #delta time in seconds

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == self.enemy_event:
                    Enemy(choice(self.spawn_positions), choice(list(self.enemy_frames.values())), self.player, self.collision_sprites, (self.all_sprites, self.enemy_sprites))
              
            self.gun_timer()
            self.input()
        
            self.all_sprites.update(dt)
            self.kill_monster_collisions()
            self.player_collision()
            
            #background
            self.display_surface.fill('#3a2e3f')
            self.all_sprites.draw(self.player.rect.center)

            pygame.display.flip()

        pygame.quit()

if __name__ == '__main__':
    game = Game()
    game.run()