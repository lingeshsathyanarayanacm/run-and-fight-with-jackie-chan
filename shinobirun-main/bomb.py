import pygame
import os
import itemdrop


#grenade image
grenade_img = pygame.image.load("img/icons/rasengan.png")

GRAVITY = 0.75
SCREEN_WIDTH = 800
SCREEN_HEIGHT = int(SCREEN_WIDTH * 0.8)
ROWS = 16
COLS = 150
TILE_SIZE = SCREEN_HEIGHT // ROWS
level = 1

grenade_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()

class Grenade(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.timer = 100
        self.vel_y = -11
        self.speed = 7
        self.image = grenade_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)   
        self.direction = direction
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        # self.explosion_list = []
        # self.frame_index = 0
        # self.update_time = pygame.time.get_ticks()
        # for i in range(5):
        #     self.explode_img = pygame.image.load(f'img/explosion/exp{i+1}.png')
        #     self.explosion_list.append(self.explode_img)

    def update(self, player, enemy_group, obstacle_list, screen_scroll):
        self.vel_y += GRAVITY
        dx = self.direction * self.speed
        dy = self.vel_y

        #boundary check
        if self.rect.left + dx < 0 or self.rect.right + dx > SCREEN_WIDTH:
            self.direction *= -1
            dx = self.direction * self.speed

        #checking collision with tiles
        for tile in obstacle_list:
            if tile[1].colliderect(self.rect.x +dx, self.rect.y, self.width, self.height):
                self.direction *= -1
                dx = self.direction * self.speed

            #check for collision in the y direction
            if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                self.speed = 0
                #check if the below the ground , i.e. thrown up
                if self.vel_y < 0:
                    self.vel_y = 0
                    dy = tile[1].bottom - self.rect.top
                #check if above the ground, i.e. falling
                elif self.vel_y >= 0:
                    self.vel_y = 0
                    dy = tile[1].top - self.rect.bottom

        #update grenade position
        self.rect.x += dx + screen_scroll
        self.rect.y += dy

        #countdown
        self.timer -= 1
        if self.timer <= 0:
            self.kill()
            explosion = Explosion(self.rect.x, self.rect.y, 1.5)
            explosion_group.add(explosion)
            #DAMAGING CHARACTER
            if abs(self.rect.centerx - player.rect.centerx) < TILE_SIZE *2 and\
                abs(self.rect.centery - player.rect.centery) < TILE_SIZE *2:
                player.health -= 50
            for enemy in enemy_group:
                if abs(self.rect.centerx - enemy.rect.centerx) < TILE_SIZE *2 and\
                    abs(self.rect.centery - enemy.rect.centery) < TILE_SIZE *2:
                    enemy.health -= 50





#EXPLOSION ANIMATION
class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y, scale):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        for num in range(1, 6):
            img = pygame.image.load(f'img/explosion/exp{num}.png')
            img = pygame.transform.scale(img,(int(img.get_width()*scale), int(img.get_height()*scale)))
            self.images.append(img)
        self.frame_index = 0
        self.image = self.images[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)   
        self.counter = 0
    
    def update(self, screen_scroll):
        #scroll
        self.rect.x += screen_scroll
        EXPLOSION_SPEED = 4
        #UPDATE EXPLOSION ANIMATION
        self.counter += 1

        if self.counter >= EXPLOSION_SPEED:
            self.counter = 0
            self.frame_index += 1
            if self.frame_index >= len(self.images):
                self.kill()
            else:
                self.image = self.images[self.frame_index]