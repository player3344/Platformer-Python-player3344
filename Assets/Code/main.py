## Imports

import pygame
import random
import math
import os
from os import listdir
from os.path import isfile, join

## Global variables

GLOBAnimationDelay = 4



## Initial Setup

pygame.init()

pygame.display.set_caption("Platformer")
DisplayHeight, DisplayWidth = 800, 720
FPS = 60
PlayerSpeed = 10

Display = pygame.display.set_mode((DisplayWidth, DisplayHeight), pygame.RESIZABLE)

def flip(sprites):
    return [pygame.transform.flip(sprite, True, False) for sprite in sprites]

def loadSpriteSheets(dir1, dir2, width, height, direction=False):
    path = join("Assets", dir1, dir2)
    images = [f for f in listdir(path) if isfile(join(path, f))]

    all_sprites = {}

    for image in images:
        sprite_sheet = pygame.image.load(join(path, image)).convert_alpha()

        sprites = []

        for i in range(sprite_sheet.get_width() // width):
            surface = pygame.Surface((width, height), pygame.SRCALPHA, 32)
            rect = pygame.Rect(i * width, 0, width, height)
            surface.blit(sprite_sheet, (0, 0), rect)
            sprites.append(pygame.transform.scale2x(surface))
        
        if direction:
            all_sprites[image.replace(".png", "") + "_right"] = sprites
            all_sprites[image.replace(".png", "") + "_left"] = flip(sprites)
        else:
            all_sprites[image.replace(".png", "")] = sprites

    return all_sprites

def getBlock(size):
    path = join("Assets", "Images", "Terrain.png")
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((size, size), pygame.SRCALPHA, 32)
    rect = pygame.Rect(96, 0, size, size)
    surface.blit(image, (0, 0), rect)
    return pygame.transform.scale2x(surface)

class Player(pygame.sprite.Sprite):   
    Color = (255, 0, 0)
    Gravity = 1
    Sprites = loadSpriteSheets("Images", "MaskDude", 32, 32, True)
    AnimationDelay = GLOBAnimationDelay

    def __init__(self, x, y, width, height):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.x_speed = 0
        self.y_speed = 0
        self.mask = None
        self.direction = "left"
        self.animation_count = 0
        self.fall_count = 0
        self.jump_count = 0
        
    def jump(self):
        self.y_speed = -self.Gravity * 8
        self.animation_count = 0
        self.jump_count += 1
        
        if self.jump_count == 1:
            self.fall_count = 0
    
    def Move(self, dx , dy):
        self.rect.x += dx
        self.rect.y += dy

    def moveLeft(self, speed):
        self.x_speed = -speed

        if self.direction != "left":
            self.direction = "left"
            self.animation_count = 0
    
    def moveRight(self, speed):
        self.x_speed = speed

        if self.direction != "right":
            self.direction = "right"
            self.animation_count = 0

    def loop(self, fps):
        self.y_speed += min(1, (self.fall_count / fps) * self.Gravity) # This controls Gravity
        self.Move(self.x_speed, self.y_speed)

        self.fall_count += 1
    
        self.updateSprite()
    
    def landed(self):
        self.fall_count = 0
        self.y_speed = 0
        self.jump_count = 0

    def hitHead(self):
        self.count = 0
        self.y_speed*= -1

    def updateSprite(self):
        sprite_sheet = "idle"
        if self.y_speed  != 0:
            if self.jump_count == 1:
                sprite_sheet = "jump"
            elif self.jump_count == 2:
                sprite_sheet = "double_jump"
        elif self.y_speed > self.Gravity * 2:
            sprite_sheet = "fall"
        elif self.x_speed != 0:
            sprite_sheet = "run"

        sprite_sheet_name = sprite_sheet + "_" + self.direction
        sprites = self.Sprites[sprite_sheet_name]
        sprite_index = self.animation_count // self.AnimationDelay % len(sprites)
        self.sprite = sprites[sprite_index]
        self.animation_count += 1
        self.update()

    def update(self):
        self.rect = self.sprite.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.sprite)

    def draw(self, Display, offset_x):
        Display.blit(self.sprite, (self.rect.x - offset_x, self.rect.y))


class Object(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, name=None):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.width = width
        self.height = height
        self.name = name
        
    def draw(self, Display, offset_x):
        Display.blit(self.image, (self.rect.x - offset_x, self.rect.y))


class Block(Object):
    def __init__(self, x, y, size):
        super().__init__(x, y, size, size)
        block = getBlock(size)
        self.image.blit(block, (0,0))
        self.mask = pygame.mask.from_surface(self.image)

# A function that returns the tile positions and the tile image itself

def GetBackground(name):
    image = pygame.image.load(join("Assets", "Images", name))
    _, _, width, height = image.get_rect()

    tiles = []
    for i in range (DisplayWidth // width + 1):
        for j in range (DisplayHeight // height + 1):
            pos = (i * width, j * height)
            tiles.append(pos)
    
    return tiles, image

def draw(Display, background, BGImage, player, objects, offset_x):
    for tile in background:
        Display.blit(BGImage, tile)
    
    for obj in objects:
        obj.draw(Display, offset_x)

    player.draw(Display, offset_x)
    
    pygame.display.update()

def handleVerticalCollision(player, objects, dy):
    collided_objects = []
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            if dy > 0:
                player.rect.bottom = obj.rect.top
                player.landed()
            elif dy < 0:
                player.rect.top = obj.rect.bottom
                player.hitHead()
        
        collided_objects.append(obj)
        
    return collided_objects

def handleMove(player, objects):
    keys = pygame.key.get_pressed()

    player.x_speed = 0
    if keys[pygame.K_a]:
        player.moveLeft(PlayerSpeed)
    if keys[pygame.K_d]:
        player.moveRight(PlayerSpeed)
    
    handleVerticalCollision(player, objects , player.y_speed)

def main(Display):
    clock = pygame.time.Clock() # Make a clock to regulate fps and more
    Background, BGImage = GetBackground("Blue.png")

    block_size = 96

    player = Player(100, 100, 50, 50)

    floor =[Block(i * block_size, DisplayHeight - block_size, block_size) 
            for i in range(-DisplayWidth // block_size, DisplayWidth * 2 // block_size)]
    
    offset_x = 0
    scroll_area_width = 200

    run = True # The main game run variable

    while run:
        clock.tick(FPS) # Set FPS

        # Main Event loop

        for event in pygame.event.get():
            # Handling Quit events

            if event.type == pygame.QUIT:
                run = False
                break
                
            elif event.type == pygame.VIDEORESIZE:
                Display = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                break
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and player.jump_count < 2:
                    player.jump()

        player.loop(FPS)

        handleMove(player, floor)
        
        draw(Display, Background, BGImage, player, floor, offset_x)

        if (player.rect.right - offset_x >= DisplayWidth - scroll_area_width and player.x_speed > 0) or (
            (player.rect.left - offset_x <= scroll_area_width) and player.x_speed < 0):
                
                offset_x += player.x_speed
    
    pygame.quit()
    quit()

if __name__ == "__main__":
    main(Display)