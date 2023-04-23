import pygame
from soldier import Soldier
import ammo
import bomb
import itemdrop
import csv
import button
import menu
import time

pygame.init()

GRAVITY = 0.75
SCREEN_WIDTH = 800
SCREEN_HEIGHT = int(SCREEN_WIDTH * 0.8)
ROWS = 16
COLS = 150
TILE_SIZE = SCREEN_HEIGHT // ROWS
TILE_TYPES = 21
SCROLL_THRESHOLD = 200
screen_scroll = 0 
bg_scroll = 0
level = 1
MAX_LEVELS = 3

#sound
sound  = pygame.mixer.Sound("menu.mp3")
sound.play()
t = 30
end = time.time() + t

#PLAYER MOVEMENT
moving_left = False
moving_right = False
shoot = False
throw = False
grenade_thrown = False

#LOAD TILE IMAGES
img_list = []
for x in range(TILE_TYPES):
    img = pygame.image.load(f'img/tile/{x}.png')
    img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
    img_list.append(img)

#LOAD BACKGROUND IMAGE
bgimg = pygame.image.load('img/Background/ourbg1.jpg')

#SCREEN
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Shinobi Run")

enemy_group = pygame.sprite.Group()
decoration_group = pygame.sprite.Group()
water_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()

#main menu
start_game = False
bg = pygame.image.load("back.jpg")
bg = pygame.transform.scale(bg, (SCREEN_WIDTH, SCREEN_HEIGHT))
start_img = pygame.image.load("start.png").convert_alpha()
start_img = pygame.transform.scale(start_img, (int(start_img.get_width() * 0.8), int(start_img.get_height() * 0.8)))
exit_img = pygame.image.load("exit.png").convert_alpha()
exit_img = pygame.transform.scale(exit_img, (int(exit_img.get_width() * 0.8), int(exit_img.get_height() * 0.8)))
restart_img = pygame.image.load("restart_btn.png").convert_alpha()
over_img = pygame.image.load("home-page.png").convert_alpha()
over = pygame.image.load("game-over.png").convert_alpha()
over = pygame.transform.scale(over, (int(over.get_width() * 0.5), int(over.get_height() * 0.5)))

start_button = button.Button(500, 250, start_img, 1)
exit_button = button.Button(500, 450, exit_img, 1)
restart_button = button.Button(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 50 , restart_img, 2.5 )
over_button = button.Button(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 50 , over_img, 0.5)
#set frame rate
clock = pygame.time.Clock()
FPS =60

BG = (144, 201, 120)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 100)
BLACK = (0, 0, 0)
ORCHRE = (204, 119, 34)

#defined font
font = pygame.font.SysFont('Futura', 30)

def draw_bg():
    screen.fill(BG)
    width = bgimg.get_width()
    for x in range(3):
	    screen.blit(bgimg, ((x * width) - bg_scroll * 0.5, 0))

def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x,y))

#function to reset level
def reset_level():
    enemy_group.empty()
    ammo.bullet_group.empty()
    bomb.grenade_group.empty()
    bomb.explosion_group.empty()
    itemdrop.item_box_group.empty()
    decoration_group.empty()
    water_group.empty()
    exit_group.empty()

    #empty list
    data = []
    for row in range(ROWS):
        r = [-1] * COLS
        data.append(r)
    
    return data


#CLASS FOR DRAWING HEALTHBAR
class HealthBar():
    def __init__(self, x, y, health, max_health):
        self.x = x
        self.y = y
        self.health = health
        self.max_health = max_health

    def draw(self, health):
        self.health = health
        ratio = self.health/self.max_health
        pygame.draw.rect(screen, BLACK, (self.x -2, self.y-2, 154, 24))
        pygame.draw.rect(screen, RED, (self.x, self.y, 150, 20))
        pygame.draw.rect(screen, GREEN, (self.x, self.y, 150* ratio, 20))

class World():
    def __init__(self):
        self.obstacle_list = []

    def process_data(self, data):
        self.level_length = len(data[0])
        #iterate through each value in level data file
        for y, row in enumerate(data):
            for x, tile in enumerate(row):
                if tile >= 0:
                    img = img_list[tile]
                    img_rect = img.get_rect()
                    img_rect.x = x * TILE_SIZE
                    img_rect.y = y * TILE_SIZE
                    tile_data = (img, img_rect)
                    if tile >= 0 and tile <= 8:
                        self.obstacle_list.append(tile_data)
                    elif tile >= 9 and tile <= 10: #water
                        water = Water(img, x * TILE_SIZE, y * TILE_SIZE)
                        water_group.add(water)
                    elif tile >= 11 and tile <= 14: #decoration
                        decoration = Decoration(img, x * TILE_SIZE, y * TILE_SIZE)
                        decoration_group.add(decoration)
                    elif tile == 15:#create player
                        player = Soldier("player", x * TILE_SIZE, y * TILE_SIZE, 0.7, 6, screen, 15, 5)
                        health_bar = HealthBar(10, 10, player.health, player.max_health)
                    elif tile == 16:#create enemy
                        enemy = Soldier("enemy", x * TILE_SIZE, y * TILE_SIZE, 1.65, 2, screen, 30, 0)
                        enemy_group.add(enemy)
                    elif tile == 17:#create ammo box
                        item_box = itemdrop.ItemDrop("Ammo", x * TILE_SIZE, y * TILE_SIZE)
                        itemdrop.item_box_group.add(item_box)
                    elif tile == 18:#create grenade box
                        item_box = itemdrop.ItemDrop("Grenade", x * TILE_SIZE, y * TILE_SIZE)
                        itemdrop.item_box_group.add(item_box)
                    elif tile == 19:#create Health box
                        item_box = itemdrop.ItemDrop("Health", x * TILE_SIZE, y * TILE_SIZE)
                        itemdrop.item_box_group.add(item_box)
                    elif tile == 20:#exit level
                        exit = Exit(img, x * TILE_SIZE, y * TILE_SIZE)
                        exit_group.add(exit)
                    
        return player, health_bar
    
    def draw(self):
        for tile in self.obstacle_list:
            tile[1][0] += screen_scroll
            screen.blit(tile[0], tile[1])

class Decoration(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll

class Water(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll

class Exit(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll

class Screenfade():
    def __init__(self, direction, color, speed):
        self.direction = direction
        self.color = color
        self.speed = speed
        self.fade_counter = 0
    
    def fade(self):
        self.fade_counter += self.speed
        pygame.draw.rect(screen, self.color, (0, 0, SCREEN_WIDTH, 0 + self.fade_counter))

#create empty tile list
world_data = []
for row in range(ROWS):
    r = [-1] * COLS
    world_data.append(r)
#load in level data data and create world
with open(f'level{level}_data.csv', newline = '') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    for x, row in enumerate(reader):
        for y, tile in enumerate(row):
            world_data[x][y] = int(tile)
world = World()
player, health_bar = world.process_data(world_data)

#menu setup
mc = menu.Menu(250, 330, 1.3)
exit_fade = Screenfade(2, ORCHRE, 4)

run = True
while run:

    clock.tick(FPS)

    if time.time() >= end:
        sound.stop()
        sound.play()
        end = time.time() + t

    if start_game==False:
        pass
        screen.blit(bg, (0, 0))
        mc.drawc(screen)
        if start_button.draw(screen):
            start_game = True
        if exit_button.draw(screen):
            run = False
    else:

        #UPDATE BACKGROUND
        draw_bg()
        #DRAW WORLD
        world.draw()
        #HEALTH DISPLAY
        health_bar.draw(player.health)
        #AMMO DISPLAY
        draw_text(f"AMMO: ", font, WHITE, 10, 35)
        for x in range(player.mag):
            image = pygame.transform.scale(ammo.bullet_img,  (int(ammo.bullet_img.get_width() * 0.05), int(ammo.bullet_img.get_height()*0.05)))
            screen.blit(image, ((90 + (x * 20)), 30))
        #GRENADE DISPLAY
        draw_text(f"GRENADES: ", font, WHITE, 10, 60)
        for x in range(player.grenades):
            screen.blit(bomb.grenade_img, ((135 + (x * 30)), 60))
        player.update()
        player.draw()

        for enemy in enemy_group:
            enemy.ai(player, world.obstacle_list,screen_scroll,  bg_scroll, world.level_length)
            enemy.update()
            enemy.draw()

        #update and draw groups
        ammo.bullet_group.update(player, enemy_group, world.obstacle_list, screen_scroll)
        ammo.bullet_group.draw(screen)

        itemdrop.item_box_group.update(player, screen_scroll)
        itemdrop.item_box_group.draw(screen)

        bomb.grenade_group.update(player, enemy_group, world.obstacle_list, screen_scroll)
        bomb.grenade_group.draw(screen)

        bomb.explosion_group.update(screen_scroll)
        bomb.explosion_group.draw(screen)

        decoration_group.update()
        decoration_group.draw(screen)

        water_group.update()
        water_group.draw(screen)

        exit_group.update()
        exit_group.draw(screen)

        #player State
        if player.alive:
            if shoot:
                player.shoot()
            elif throw and grenade_thrown == False and player.grenades > 0:
                grenade = bomb.Grenade(player.rect.centerx + (0.6 * player.rect.size[0] * player.direction),\
                                        player.rect.top, player.direction)
                bomb.grenade_group.add(grenade)
                player.grenades -= 1
                grenade_thrown = True
            if player.in_air:
                player.update_action(2)#2: jump
            elif moving_left or moving_right:
                player.update_action(1)#1: run
            else:
                player.update_action(0)#0: idle
            screen_scroll, level_complete = player.move(moving_left, moving_right, world.obstacle_list, bg_scroll, world.level_length, water_group, exit_group)  
            bg_scroll -= screen_scroll
            if level_complete:
                level += 1
                if level <= MAX_LEVELS:
                    bg_scroll = 0
                    world_data = reset_level()
                    with open(f'level{level}_data.csv', newline = '') as csvfile:
                        reader = csv.reader(csvfile, delimiter=',')
                        for x, row in enumerate(reader):
                            for y, tile in enumerate(row):
                                world_data[x][y] = int(tile)
                    world = World()
                    player, health_bar = world.process_data(world_data)
                else:
                    screen_scroll = 0
                    exit_fade.fade()
                    screen.blit(over, (300, 40))
                    if over_button.draw(screen):
                        start_game = False

        else:
            screen_scroll = 0
            if restart_button.draw(screen):
                bg_scroll = 0
                world_data = reset_level()
                with open(f'level{level}_data.csv', newline = '') as csvfile:
                    reader = csv.reader(csvfile, delimiter=',')
                    for x, row in enumerate(reader):
                        for y, tile in enumerate(row):
                            world_data[x][y] = int(tile)
                world = World()
                player, health_bar = world.process_data(world_data)

    for event in pygame.event.get():
        #quit game
        if event.type == pygame.QUIT:
            run = False
        
        #keyboard presses
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                moving_left = True
            if event.key == pygame.K_d:
                moving_right = True
            if event.key == pygame.K_SPACE:
                shoot = True
            if event.key == pygame.K_q:
                throw = True
            if event.key == pygame.K_ESCAPE:
                run = False
            if event.key == pygame.K_w and player.alive:
                player.jump = True

        #keyboard key releases
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                moving_left = False
            if event.key == pygame.K_d:
                moving_right = False
            if event.key == pygame.K_SPACE:
                shoot = False
            if event.key == pygame.K_q:
                throw = False
                grenade_thrown = False

        

    pygame.display.update()

pygame.quit()
