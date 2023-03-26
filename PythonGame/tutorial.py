import os 
import random
import math
import pygame
from os import listdir
from os.path import isfile, join
pygame.init()

pygame.display.set_caption('Platformer')


# BACKGROUND_COLOR = (255, 255, 255)  # background color (white) (we don't need later)
WIDTH, HEIGHT = 1500, 800  # width and height of the game screen
FRAMESPERSECOND = 60

PLAYER_VELOCITY = 5  # Player's speed

# We need to set up pygame window
window = pygame.display.set_mode((WIDTH, HEIGHT)) # mode will be changed as WIDTH AND HEIGHT 

def flip(sprites):
    return [pygame.transform.flip(sprite, True, False) for sprite in sprites]

def load_sprite_sheets(dir1, dir2, width, height, direction=False):
    path = join('PythonGame', dir1, dir2)
    images = [f for f in listdir(path) if isfile(join(path, f))]  # load every single file inside of this directory

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


class Player(pygame.sprite.Sprite):
    COLOR = (255, 0, 0) # color for player
    GRAVITY = 1
    SPRITES = load_sprite_sheets("MainCharacters", "MaskDude", 32, 32, True)
    ANIMATION_DELAY = 4

    def __init__(self, x, y, width, height):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height) # putting all of them in once rahter than individually
        # Rect is a tuple storing 4 values
        self.x_velocity = 0
        self.y_velocity = 0
        # x, y velocities determine how fast we are moving player every single frame in both directions
        self.mask = None
        self.direction = "left"
        self.animation_count = 0
        self.fall_count = 0
        self.jump_count = 0
        self.hit = False
        self.hit_count = 0

    def jump(self):
        self.y_velocity = -self.GRAVITY * 8
        self.animation_count = 0
        self.jump_count += 1
        if self.jump_count == 1:
            self.fall_count = 0
        
    def move(self, dx, dy): # function for moving up and down
        self.rect.x += dx
        self.rect.y += dy
    
    def make_hit(self):
        self.hit = True
        self.hit_count = 0
    
    def move_left(self, velocity):
        self.x_velocity = -velocity
        if self.direction != "left":
            self.direction = "left"
            self.animation_count = 0
            
    def move_right(self, velocity):
        self.x_velocity = velocity
        if self.direction != "right":
            self.direction = "right"
            self.animation_count = 0
    
    def loop(self, fps):
        self.y_velocity += min(1, (self.fall_count / fps) * self.GRAVITY)
        self.move(self.x_velocity, self.y_velocity)

        if self.hit:
            self.hit_count += 1
        if self.hit_count > fps * 2:
            self.hit = False
            self.hit_count = 0

        self.fall_count += 1
        self.update_sprite()

    def landed(self):
        self.fall_count = 0
        self.y_velocity = 0
        self.jump_count = 0

    def hithead(self):
        self.count = 0
        self.y_velocity *= -1

    
    def update_sprite(self):
        sprite_sheet = "idle" # default sprite_sheet if we are not moving
        if self.hit:
            sprite_sheet = "hit"
        elif self.y_velocity != 0:
            if self.jump_count == 1:
                sprite_sheet = "jump"
            elif self.jump_count == 2:
                sprite_sheet = "double_jump"
        elif self.y_velocity > self.GRAVITY * 2:
            sprite_sheet = "fall"
        elif self.x_velocity != 0:
            sprite_sheet = "run"
        
        sprite_sheet_name = sprite_sheet + "_" + self.direction
        sprites = self.SPRITES[sprite_sheet_name]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.sprite = sprites[sprite_index]
        self.animation_count += 1
        self.update()

    def update(self):
        self.rect = self.sprite.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.sprite)


    def draw(self, win, offset_x):
        #pygame.draw.rect(win, self.COLOR, self.rect)
        win.blit(self.sprite, (self.rect.x - offset_x, self.rect.y))


class Object(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, name=None):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.width = width
        self.height = height  
        self.name = name
    
    def draw(self, win, offset_x):
        win.blit(self.image, (self.rect.x - offset_x, self.rect.y))


class Block(Object):
    def __init__(self, x, y, size):
        super().__init__(x, y, size, size)
        block = get_block(size)
        self.image.blit(block, (0, 0))
        self.mask = pygame.mask.from_surface(self.image)


class Fire(Object):
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "fire")
        self.fire = load_sprite_sheets("Traps", "Fire", width, height)
        self.image = self.fire["off"][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0  
        self.animation_name = "off"
    
    def on(self):
        self.animation_name = "on"

    def off(self):
        self.animation_name = "off"

    def loop(self):
        sprites = self.fire[self.animation_name]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.image = sprites[sprite_index]
        self.animation_count += 1

        self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.image)

        if self.animation_count // self.ANIMATION_DELAY > len(sprites):
            self.animation_count = 0

def get_background(name): # function for getting background image
    image = pygame.image.load(join('PythonGame', 'Background', name))
    _, _, width, height = image.get_rect() # _, _, - x, y direction
    tiles = []

    for i in range(WIDTH // width + 1): # we need this it will tell us how many tiles we need in width
        for j in range(HEIGHT // height + 1): # how many tiles we need in height
            pos = (i * width, j * height) # position of top left hand corner of the current tile that we are adding to tiles list
            tiles.append(pos)

    return tiles, image # returning image can help what image we need to use when drawing these tiles 

# set up function to draw background
def draw(window, background, bg_image, player, objects, offset_x):
    for tile in background: # looping through every tile 
        window.blit(bg_image, tile) # draw at (tile) position

    for object in objects:
        object.draw(window, offset_x)

    player.draw(window, offset_x)
    pygame.display.update() # update the display

def handle_vertical_collision(player, objects, dy):
    collided_objects = []
    for object in objects:
        if pygame.sprite.collide_mask(player, object):
            if dy > 0:
                player.rect.bottom = object.rect.top
                player.landed()
            elif dy < 0:
                player.rect.top = object.rect.bottom
                player.hit_head()
        
            collided_objects.append(object)
    
    return collided_objects

def collide(player, objects, dx):
    player.move(dx, 0)
    player.update()
    collided_object = None
    for object in objects:
        if pygame.sprite.collide_mask(player, object):
            collided_object = object 
            break
    
    player.move(-dx, 0)
    player.update()
    return collided_object

def handle_movement(player, objects):
    keys = pygame.key.get_pressed()

    player.x_velocity = 0
    collide_left = collide(player, objects, -PLAYER_VELOCITY * 2)
    collide_right = collide(player, objects, PLAYER_VELOCITY * 2)


    if keys[pygame.K_LEFT] and not collide_left:
        player.move_left(PLAYER_VELOCITY)
    if keys[pygame.K_RIGHT] and not collide_right:
        player.move_right(PLAYER_VELOCITY)
    
    vertical_collide = handle_vertical_collision(player, objects, player.y_velocity)
    to_check = [collide_left, collide_right, *vertical_collide]
    for object in to_check:
        if object and object.name == "fire":
            player.make_hit()

# create a main function for starting the game
def main(window):
    # we need to set up few things
    clock = pygame.time.Clock()
    background, bg_image = get_background('Blue.png')
    block_size = 96

    player = Player(100, 100, 50, 50)
    fire = Fire(100, HEIGHT -block_size - 64, 16, 32)
    fire.on()
    floor = [Block(i * block_size, HEIGHT - block_size, block_size) for i in range(-WIDTH // block_size, (WIDTH * 2) // block_size)]
    # blocks = [Block(0, HEIGHT - block_size, block_size)]
    objects = [*floor, Block(0, HEIGHT - block_size * 2, block_size), Block(block_size * 3, HEIGHT - block_size * 4, block_size), fire]

    offset_x = 0
    scroll_area_width = 200

    run = True
    while run:
        clock.tick(FRAMESPERSECOND)  # no more than 60 frames per second

        for event in pygame.event.get():
            if event.type == pygame.QUIT: # checking if user press 'x' the game will stop
                run = False
                break
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and player.jump_count < 2:
                    player.jump()
        
        player.loop(FRAMESPERSECOND)
        fire.loop()
        handle_movement(player, objects)
        draw(window, background, bg_image, player, objects, offset_x)

        if ((player.rect.right - offset_x >= WIDTH - scroll_area_width) and player.x_velocity > 0) or ((player.rect.left - offset_x <= scroll_area_width) and player.x_velocity < 0):
            offset_x += player.x_velocity

    pygame.quit()
    quit() # quit python program

if __name__ == '__main__':
    main(window)
