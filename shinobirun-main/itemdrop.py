import pygame
import os

SCREEN_WIDTH = 800
SCREEN_HEIGHT = int(SCREEN_WIDTH * 0.8)
ROWS = 16
COLS = 150
TILE_SIZE = SCREEN_HEIGHT // ROWS
level = 1

health_box = pygame.image.load("img/icons/health_box.png")
grenade_box = pygame.image.load("img/icons/grenade_box.png")
magazine_re = pygame.image.load("img/icons/ammo_box.png")
item_boxes ={
    'Health' :health_box,
    'Ammo' :magazine_re,
    'Grenade' :grenade_box
}

item_box_group = pygame.sprite.Group()

#droping items 
class ItemDrop(pygame.sprite.Sprite):
    def __init__(self, item_type, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.item_type = item_type
        self.image = item_boxes[self.item_type]
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE//2, y + (TILE_SIZE - self.image.get_height()))

    def update(self, player, screen_scroll):

        self.rect.x += screen_scroll

        #checking if the player has collected the item box or not
        if pygame.sprite.collide_rect(self, player):
            #check box type
            if self.item_type == 'Health':
                player.health += 25
                if player.health >= player.max_health:
                    player.health = player.max_health
            elif self.item_type == 'Ammo':
                player.mag += 15
            elif self.item_type == 'Grenade':
                player.grenades += 3
            #DELETING ITEM BOX
            self.kill()