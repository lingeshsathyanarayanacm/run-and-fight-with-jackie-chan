import pygame
import os
import itemdrop

SCREEN_WIDTH = 800
SCREEN_WIDTH = 800
SCREEN_HEIGHT = int(SCREEN_WIDTH * 0.8)
ROWS = 16
COLS = 150
TILE_SIZE = SCREEN_HEIGHT // ROWS
level = 1
#buller_img
bullet_img = pygame.image.load("img/icons/kunai.png")

#Create Sprite groups: this comes with an prewritten draw and update method
bullet_group = pygame.sprite.Group()


# class for bullets
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction, scale, flip):
        pygame.sprite.Sprite.__init__(self)
        self.speed = 10
        self.flip = flip
        img = pygame.transform.scale(bullet_img,  (int(bullet_img.get_width() * scale), int(bullet_img.get_height()*scale)))
        if flip:
            self.image = pygame.transform.rotate(img, -45)
        else:
            self.image = pygame.transform.rotate(img, 135)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)   
        self.direction = direction
    
    def update(self, player, enemy_group,obstacle_list, screen_scroll):
        #move bullet
        self.rect.x += (self.direction * self.speed) + screen_scroll
        #check for going of screen
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
            self.kill()

        #check for collision with tile
        for tile in obstacle_list:
            if tile[1].colliderect(self.rect):
                self.kill()

        #check collision with characters
        if pygame.sprite.spritecollide(player, bullet_group, False):
            if player.alive:
                player.health -= 5
                self.kill()
        for enemy in enemy_group:
            if pygame.sprite.spritecollide(enemy, bullet_group, False):
                if enemy.alive:
                    enemy.health -= 34
                    self.kill()

