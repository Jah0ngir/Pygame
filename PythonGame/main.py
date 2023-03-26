import os 
import random
import math
import pygame
from os import listdir
from os.path import isfile, join
pygame.init()

pygame.display.set_caption('Platformer')


# BACKGROUND_COLOR = (255, 255, 255)  # background color (white) (we don't need later)
WIDTH, HEIGHT = 1000, 800  # width and height of the game screen
FRAMESPERSECOND = 60

PLAYER_VELOCITY = 5  # Player's speed

# We need to set up pygame window
window = pygame.display.set_mode((WIDTH, HEIGHT)) # mode will be changed as WIDTH AND HEIGHT 

def flip(sprites):
    return [pygame.transform.flip(sprite, True, False) for sprite in sprites]

def load_sprite_sheets(dir1, dir2, width, height, direction=False):
    path = join('PythonGame', dir1, dir2)
    images = [f for f in listdir(path) if isfile(join(path, f))] # load every single file inside of this directory  

    all_sprites = {}

    for image in images:
        sprite_sheet = pygame.image.load(join(path, image)).convert_alpha()

        sprites = []
        for i in range(sprite_sheet.get_width() // width):
            surface = pygame.Surface((width, height), pygame.SRCALPHA, 32)
            rect = pygame.Rect(i * width, 0, width, height)
            surface.blit(sprite_sheet, (0, 0), rect) # blit means draw
            sprites.append(pygame.transform.scale2x(surface))
        
        if direction:
            all_sprites[image.replace(".png", "") + "_right"] = sprites
            all_sprites[image.replace(".png", "") + "_left"] = flip(sprites)
        else:
            all_sprites[image.replace(".png", "")] = sprites

    return all_sprites

def get_block(size):
    path = join('PythonGame', 'Terrain', 'Terrain.png')
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((size, size), pygame.SRCALPHA, 32)
    rect = pygame.Rect(96, 0, size, size)
    surface.blit(image, (0, 0), rect)
    return pygame.transform.scale2x(surface)


class Player:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.vel = 5
        self.is_jump = False
        self.jump_count = 10
        self.direction = 'right'
        self.animation_count = 0
        self.SPRITES = {
            'right': [pygame.image.load(os.path.join('MainCharacters','MaskDude', 'double_jump.png')), 
                      pygame.image.load(os.path.join( 'MainCharacters', 'MaskDude','double_jump.png')),
                      pygame.image.load(os.path.join( 'MainCharacters','MaskDude', 'double_jump.png')),
                      pygame.image.load(os.path.join( 'MainCharacters','MaskDude', 'double_jump.png')),
                      pygame.image.load(os.path.join('MainCharacters', 'MaskDude','double_jump.png')),
                      pygame.image.load(os.path.join('MainCharacters','MaskDude', 'double_jump.png')),
                      pygame.image.load(os.path.join('MainCharacters','MaskDude', 'double_jump.png')),
                      pygame.image.load(os.path.join('MainCharacters', 'MaskDude','double_jump.png')),
                      pygame.image.load(os.path.join( 'MainCharacters','MaskDude', 'double_jump.png'))],
            'left': [pygame.image.load(os.path.join( 'MainCharacters','MaskDude', 'double_jump.png')), 
                     pygame.image.load(os.path.join('MainCharacters','MaskDude', 'double_jump.png')),
                     pygame.image.load(os.path.join('MainCharacters','MaskDude', 'double_jump.png')),
                     pygame.image.load(os.path.join('MainCharacters','MaskDude', 'double_jump.png')),
                     pygame.image.load(os.path.join('MainCharacters','MaskDude', 'double_jump.png')),
                     pygame.image.load(os.path.join('MainCharacters','MaskDude', 'double_jump.png')),
                     pygame.image.load(os.path.join( 'MainCharacters','MaskDude', 'double_jump.png')),
                     pygame.image.load(os.path.join( 'MainCharacters','MaskDude', 'double_jump.png')),
                     pygame.image.load(os.path.join( 'MainCharacters','MaskDude', 'double_jump.png'))]
        }
    
    def update(self, keys_pressed):
        if keys_pressed[pygame.K_LEFT] and self.x > 0:
            self.x -= self.vel
            self.direction = 'left'
            self.animation_count += 1
        elif keys_pressed[pygame.K_RIGHT] and self.x < 500 - self.width:
            self.x += self.vel
            self.direction = 'right'
            self.animation_count += 1

        if self.animation_count >= len(self.SPRITES[self.direction]):
            self.animation_count = 0
        
        self.draw()

    def draw(self):
        WIN.blit(self.SPRITES[self.direction][self.animation_count], (self.x, self.y))


class Block(pygame.sprite.Sprite):
    def __init__(self, x, y, size):
        super().__init__()
        self.image = get_block(size)
        self.rect = pygame.Rect(x, y, size, size)

    def draw(self, surface):
        surface.blit(self.image, (self.rect.x, self.rect.y))

# Creating a level by drawing blocks on the screen
blocks = pygame.sprite.Group()
for i in range(0, WIDTH, 64):
    for j in range(0, HEIGHT, 64):
        if i == 0 or j == 0 or i == WIDTH-64 or j == HEIGHT-64:
            blocks.add(Block(i, j, 64))
        elif random.randint(0, 100) < 20:
            blocks.add(Block(i, j, 64))

player = Player(50, 50, 32, 32)
player_group = pygame.sprite.Group(player)

# Game Loop
clock = pygame.time.Clock()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys_pressed = pygame.key.get_pressed()

    window.fill((0, 0, 0))

    for block in blocks:
        block.draw(window)

    player.update(keys_pressed)
    player.draw(window)

    pygame.display.update()

    clock.tick(FRAMESPERSECOND)

pygame.quit()

