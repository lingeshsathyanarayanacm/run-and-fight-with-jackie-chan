import pygame
import os
import ammo
import bomb
import itemdrop
import random

#GENERAL SOLIDER
GRAVITY = 0.75 #effect of gravity ingame
SCREEN_WIDTH = 800
SCREEN_HEIGHT = int(SCREEN_WIDTH * 0.8)
ROWS = 16
COLS = 150
TILE_SIZE = SCREEN_HEIGHT // ROWS
TILE_TYPES = 21
SCROLL_THRESHOLD = 200
screen_scroll = 0 
water_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()
bg_scroll = 0
level = 1
RED = (255, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 100)
BLACK = (0, 0, 0)


class Soldier(pygame.sprite.Sprite):
    def __init__(self, char_type,  x, y, scale, speed, screen, magazine, grenades):
        pygame.sprite.Sprite.__init__(self)
        self.screen = screen #screen variable
        self.alive = True #dead or alive status
        self.char_type = char_type #determines enemy or player
        self.speed = speed #speed of the player
        self.mag = magazine #ammunation the character has
        self.start_mag = magazine
        self.shoot_cooldown = 0 # cooldown for bullets solves from having too many bullets on screen
        self.grenades = grenades #nmbr of greandes a character has
        self.health = 100
        self.max_health = self.health
        self.direction = 1 #initial direction face right checks for change in direction
        self.jump = False #jump check initial doesnot jump 
        self.in_air =True #checks if player is airbourne or not 
        self.vel_y = 0 # velocity of player when it jumps
        self.flip = False #again direction check
        self.animation_list = [] #frames of animation get stored in here
        self.frame_index = 0 #tells which frame to load
        self.action = 0 #tells which action the player is doing
        self.update_time = pygame.time.get_ticks() 

        #enemy specific variables
        self.ai_direction = random.choice([-1, 1])
        self.move_counter = 0
        self.idling = False
        self.idling_counter = 0
        self.vision = pygame.Rect(0, 0, 150, 20)

        #load all animation types
        animation_types = ['Idle', 'Run', 'Jump', 'Death']
        for animation_type in animation_types:
            #reset temp list
            temp_list = []
            #number of files in a folder
            num_of_frames = len(os.listdir(f'img/{self.char_type}/{animation_type}'))
            for i in range(num_of_frames):
                img = pygame.image.load(f'img/{self.char_type}/{animation_type}/{i}.png')
                #scaling of the image
                img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height()*scale)))
                temp_list.append(img)
            self.animation_list.append(temp_list)

        self.soldierImg = self.animation_list[self.action][self.frame_index]
        #rect draws a boundary box around the image which will be used to detect collisions
        #it draws the boundary box w.r.t the img size
        self.rect = self.soldierImg.get_rect()
        self.rect.center = (x, y)
        self.width = self.soldierImg.get_width()
        self.height = self.soldierImg.get_height()

    def update(self):#for updating all the things
        self.update_animation()
        #update cooldown
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
        
        #alive check
        self.check_alive()

        

    #movement function for the player
    def move(self, moving_left, moving_right, obstacle_list, bg_scroll, level_length, water_group, exit_group):
        #reset movement variables
        screen_scroll =0
        dx = 0
        dy = 1

        #Assign the movement speed to the player
        if moving_left:
            dx = -self.speed
            self.direction = -1
            self.flip = True
        if moving_right:
            dx = self.speed
            self.direction = 1
            self.flip = False

        #jump
        if self.jump == True and self.in_air == False:
            self.vel_y = -14
            self.jump = False
            self.in_air = True
        
        #apply gravity
        self.vel_y += GRAVITY
        if self.vel_y > 10:
            self.vel_y = 10
        dy += self.vel_y

        #CHECK COLLISION
        for tile in obstacle_list:
            #check collision in the x direction
            if tile[1].colliderect(self.rect.x +dx, self.rect.y, self.width, self.height):
                dx = 0
                #check for ai if the enemy collides with the walls
                if self.char_type == "enemy":
                    self.ai_direction *= -1
                    self.move_counter = 0
            #check for collision in the y direction
            if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                #check if the below the ground , i.e. jumping
                if self.vel_y < 0:
                    self.vel_y = 0
                    dy = tile[1].bottom - self.rect.top
                #check if above the ground, i.e. falling
                elif self.vel_y >= 0:
                    self.vel_y = 0
                    dy = tile[1].top - self.rect.bottom
                    self.in_air = False

        #check for collision with water
        if pygame.sprite.spritecollide(self, water_group, False):
            self.health = 0

        #check if fallen off the map
        if self.rect.bottom > SCREEN_HEIGHT:
            self.health = 0

        #check for collision with exit
        level_complete = False
        if pygame.sprite.spritecollide(self, exit_group, False):
            level_complete = True

        #check if going off the edges of the screen
        if self.char_type == "player":
            if self.rect.x + dx > SCREEN_WIDTH or self.rect.x + dx < 0:
                dx = 0

        #update player rect
        self.rect.x += dx
        self.rect.y += dy 

        #update scroll on player postion
        if self.char_type == "player":
            if (self.rect.right > SCREEN_WIDTH - SCROLL_THRESHOLD and bg_scroll < (level_length * TILE_SIZE) - SCREEN_WIDTH)\
				or (self.rect.left < SCROLL_THRESHOLD and bg_scroll > abs(dx)):
                self.rect.x -= dx
                screen_scroll = -dx
        
        return screen_scroll, level_complete



    #Metod to control to the enemy movement 
    def ai(self, player, obstacle_list, screen_scroll, bg_scroll, level_length):
        if self.alive and player.alive:
            #idling the enemy a bit
            if self.idling == False and random.randint(1, 200) == 1:
                self.update_action(0)#0 : idle
                self.idling = True
                self.idling_counter = 50

            #check for player in sight to shoot it
            if self.vision.colliderect(player.rect):
                #stop running
                self.update_action(0)
                #start shooting
                self.shoot()
            #if the enemy doesnot see the player it shall continue moving
            else:
                if self.idling == False:
                    if self.ai_direction == 1:
                        ai_moving_right =True
                    else:
                        ai_moving_right = False
                    ai_moving_left = not ai_moving_right
                    self.move(ai_moving_left, ai_moving_right, obstacle_list, bg_scroll, level_length, water_group, exit_group)
                    self.update_action(1)#1: run
                    self.move_counter += 2
                    #update ai vision
                    self.vision.center = (self.rect.centerx + 75*self.ai_direction, self.rect.centery)

                    if self.move_counter > TILE_SIZE:
                        self.ai_direction *= -1
                        self.move_counter *= -1
                else:
                    self.idling_counter -= 1
                    if self.idling_counter == 0:
                        self.idling = False

        #scroll
        self.rect.x += screen_scroll

    #SHOOTING BULLETS
    def shoot(self):
        if self.shoot_cooldown == 0 and self.mag > 0:
            self.shoot_cooldown = 20
            bullet = ammo.Bullet(self.rect.centerx + (0.75 * self.rect.size[0] * self.direction),\
                                  self.rect.centery, self.direction, 0.05, self.flip)
            ammo.bullet_group.add(bullet)
            self.mag -= 1

    #changes the frame in a given time period when the player performs an action
    def update_animation(self):
        #update animation
        ANIMATION = 100
        self.soldierImg = self.animation_list[self.action][self.frame_index]
        #check time passed from the last update
        if pygame.time.get_ticks() - self.update_time > ANIMATION:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
        if self.frame_index >= len(self.animation_list[self.action]):
            if self.action == 3:
                self.frame_index = len(self.animation_list[self.action]) - 1
            else:
                self.frame_index = 0

    
    #checks for any change in action
    def update_action(self, new_action):
        if new_action != self.action: 
            self.action = new_action
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    #check the alive of character
    def check_alive(self):
        if self.health <=0:
            self.health = 0
            self.speed = 0
            self.alive = False
            self.update_action(3)

    #draws the player on the screen
    def draw(self):
        self.screen.blit(pygame.transform.flip(self.soldierImg, self.flip, False), self.rect)
