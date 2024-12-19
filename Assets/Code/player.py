from main import loadSpriteSheets
import pygame


class Player(pygame.sprite.Sprite):   
    Color = (255, 0, 0)
    Gravity = 1
    Sprites = loadSpriteSheets("", "MaskDude", 32, 32, True)
    AnimationDelay = 3

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
        self.hit = False
        self.hit_count = 0
        
    def jump(self):
        self.y_speed = -self.Gravity * 8
        self.animation_count = 0
        self.jump_count += 1
        
        if self.jump_count == 1:
            self.fall_count = 0
    
    def Move(self, dx , dy):
        self.rect.x += dx
        self.rect.y += dy

    def makeHit(self):
        self.hit = True
        self.hit_count = 0

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

        if self.hit:
            self.hit_count += 1
        if self.hit_count > fps * 2:
            self.hit = False
            self.hit_count = 0

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

        if self.hit:
            sprite_sheet = "hit"
        if self.y_speed < 0:
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
