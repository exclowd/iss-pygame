import pygame
import time
import random
import config

from pygame.locals import *
from config import *

CLOCK = pygame.time.Clock()

SCREEN_WIDTH = 512
SCREEN_HEIGHT = 840
FPS = 44
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT + 120))

# sprite sheet class for handling my sprites effectively


class SpriteSheet(object):

    def __init__(self, file_name):
        self.sprite_sheet = pygame.image.load(file_name).convert()

    def get_image_e(self, x, y, width, height, color_key):
        image = pygame.Surface([width, height]).convert()
        image.set_colorkey(color_key)
        image.blit(self.sprite_sheet, (0, 0), (x, y, width, height))
        return image

    def get_image(self, x, y, width, height):
        image = pygame.Surface([width, height]).convert()
        image.set_colorkey((153, 51, 204))
        image.blit(self.sprite_sheet, (0, 0), (x, y, width, height))
        return image

    def get_img(self, x, y, width, height):
        image = pygame.Surface([width, height], pygame.SRCALPHA)
        image.set_colorkey((0, 136, 255))
        image.blit(self.sprite_sheet, (0, 0), (x, y, width, height))
        return image

# enemy class for handling all the enemy; also has the resposibility of
# loading sprites of enemies


class Enemy(pygame.sprite.Sprite):

    def __init__(self, y_pos, base_speed, animation_cycle):
        super(Enemy, self).__init__()
        self.surf = pygame.Surface((32, 24))
        self.sheet = SpriteSheet(enemy_image)
        self.rect = self.surf.get_rect()
        self.rect.y = y_pos
        self.rect.x = random.randint(0, 13) * 32
        self.surf.fill((0, 255, 0))
        self.surf.set_colorkey((0, 255, 0))
        self.curr = 0
        self.cycle = [5, 37]
        self.orientation = 0
        self.side = [47, 103]
        self.base_speed = base_speed
        self.speed = base_speed + random.random() * 2.5
        self.ani = animation_cycle
        self.hitbox = pygame.Surface((22, 16))
        self.hitrect = self.hitbox.get_rect()

    def update(self):
        if self.orientation == 1:
            self.movr()
        else:
            self.movl()
        self.hitrect.x = self.rect.x + 5
        self.hitrect.y = self.rect.y + 8

    def movl(self):
        self.rect.move_ip(-self.speed, 0)
        self.curr = (self.curr + 1) % 24
        if self.rect.left < 0:
            self.rect.left = 0
            self.orientation = 1
            self.curr = 0
            self.speed = self.base_speed + random.random() * 2.5
            self.update()

    def movr(self):
        self.rect.move_ip(self.speed, 0)
        self.curr = (self.curr + 1) % 24
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
            self.orientation = 0
            self.curr = 0
            self.speed = self.base_speed + random.random() * 2.5
            self.update()

    def play(self):
        self.update()
        screen.blit(self.surf, self.rect)
        self.image = self.sheet.get_image_e(
            self.cycle[(self.curr // self.ani) % 2],
            self.side[self.orientation], 24, 18, (0, 255, 0))
        self.image = pygame.transform.scale(self.image, (32, 24))
        screen.blit(self.image, self)

# Trees in this game are obstacles but if you dash into one the turn ends
# Trees were meant to curb the always dashers and are loaded sequentially so as
# to give the illusion of a 3d game


class Tree(pygame.sprite.Sprite):
    def __init__(self):
        super(Tree, self).__init__()
        self.surf = pygame.Surface((64, 96))
        self.sheet = SpriteSheet(tree_image)
        self.rect = self.surf.get_rect()
        self.rect.x = random.randint(0, 7) * 64
        self.rect.y = random.randint(1, 7) * 96
        self.hitbox = pygame.Rect(
            (self.rect.x + 1, self.rect.y + 72), (64, 24))
        self.surf.fill((153, 51, 204))
        self.surf.set_colorkey((153, 51, 204))

    def play(self):
        screen.blit(self.surf, self.rect)
        self.image = self.sheet.get_image(96, 33, 30, 45)
        self.image = pygame.transform.scale(self.image, (64, 96))
        screen.blit(self.image, self)


# main player class a subclass of sprite class all movement and sprite control
# goes through it. Handles most of the collison detection

class Player(pygame.sprite.Sprite):

    def __init__(self):
        super(Player, self).__init__()
        self.surf = pygame.Surface((32, 48))
        self.rect = self.surf.get_rect()
        self.img = None
        self.speed = 2
        self.dash = 60
        self.dashing = False
        self.curr = 0
        self.score = 0
        self.cycle = [0, 30, 0, 150]
        self.orientation = 0
        self.surf.fill((0, 136, 255))
        self.surf.set_colorkey((0, 136, 255))
        self.hitbox = pygame.Surface((24, 22))
        self.hitrect = self.hitbox.get_rect()
        self.hitrect.left = self.rect.left + 4
        self.hitrect.bottom = self.rect.bottom - 2
        self.playicon = pygame.Surface((120, 120))
        self.playicon_rect = self.playicon.get_rect()
        self.playicon_rect.y = SCREEN_HEIGHT

    def play(self):
        self.dash = self.dash - 2 if self.dashing else min(self.dash + 1, 60)
        if self.dash <= 0:
            self.slow()
            self.dashing = False
        screen.blit(self.surf, self.rect)
        self.img = self.sheet.get_img(
            self.orientation * 30, self.cycle[self.curr // ani], 16, 24)
        self.img = pygame.transform.scale2x(self.img)
        screen.blit(self.img, self)

    def score_reset(self):
        self.score = 0

    def fast(self):
        self.speed = 4
        self.cycle = [90, 60, 90, 120]

    def slow(self):
        self.speed = 2
        self.cycle = [0, 30, 0, 150]

    def movr(self):
        if self.orientation != 3:
            self.orientation = 3
            self.curr = 0
        else:
            self.rect.move_ip(self.speed, 0)
            self.hitrect.move_ip(self.speed, 0)
            self.curr = (self.curr + 1) % 24
            if self.rect.right > SCREEN_WIDTH:
                self.rect.right = SCREEN_WIDTH

            for obs in game.tree_list:
                if self.hitrect.colliderect(obs.hitbox):
                    if self.dashing:
                        game.player_death(2)
                        return
                    self.hitrect.right = obs.hitbox.left
        self.rect.right = min(self.hitrect.right + 4, SCREEN_WIDTH)
        self.hitrect.right = self.rect.right - 4

    def movl(self):
        if self.orientation != 1:
            self.orientation = 1
            self.curr = 0
        else:
            self.rect.move_ip(-self.speed, 0)
            self.hitrect.move_ip(-self.speed, 0)
            self.curr = (self.curr + 1) % 24
            if self.rect.left < 0:
                self.rect.left = 0
            for obs in game.tree_list:
                if self.hitrect.colliderect(obs.hitbox):
                    if self.dashing:
                        game.player_death(2)
                        return
                    self.hitrect.left = obs.hitbox.right
        self.rect.left = max(self.hitrect.left - 4, 0)
        self.hitrect.left = self.rect.left + 4

    def movu(self):
        if self.orientation != 2:
            self.orientation = 2
            self.curr = 0
        else:
            self.rect.move_ip(0, -self.speed)
            self.hitrect.move_ip(0, -self.speed)
            self.curr = (self.curr + 1) % 24
            if self.rect.top <= 0:
                self.rect.top = 0
            for obs in game.tree_list:
                if self.hitrect.colliderect(obs.hitbox):
                    if self.dashing:
                        game.player_death(2)
                        return
                    self.hitrect.top = obs.hitbox.bottom
        self.rect.top = max(self.hitrect.top - 24, 0)
        self.hitrect.top = self.rect.top + 24

    def movd(self):
        if self.orientation != 0:
            self.orientation = 0
            self.curr = 0
        else:
            self.rect.move_ip(0, self.speed)
            self.hitrect.move_ip(0, self.speed)
            self.curr = (self.curr + 1) % 24
            if self.rect.bottom >= SCREEN_HEIGHT:
                self.rect.bottom = SCREEN_HEIGHT
            for obs in game.tree_list:
                if self.hitrect.colliderect(obs.hitbox):
                    if self.dashing:
                        game.player_death(2)
                        return
                    self.hitrect.bottom = obs.hitbox.top
        self.rect.bottom = min(self.hitrect.bottom + 2, SCREEN_HEIGHT)
        self.hitrect.bottom = self.rect.bottom - 2

    def update_time(self):
        self.time_bonus -= 1
        if self.time_bonus <= 0:
            game.player_death(3)

    def get_score(self):
        return self.score + game.backtimer() * 20


# two Player classes for handling the operations that differ between players

class Player1(Player):
    def __init__(self):
        super(Player1, self).__init__()
        self.sheet = SpriteSheet(player_one_image)
        self.score = 0
        self.time_bonus = FPS * 30

    def update(self, pressed_keys):
        if pressed_keys[K_UP]:
            self.movu()
        elif pressed_keys[K_DOWN]:
            self.movd()
        elif pressed_keys[K_LEFT]:
            self.movl()
        elif pressed_keys[K_RIGHT]:
            self.movr()
        else:
            self.curr = 0
        self.update_score()
        self.update_time()

    def update_score(self):
        self.score = max((840 - self.hitrect.y) // 96 * 100, self.score)
        if self.score == 700:
            game.player_win()

    def reset(self):
        self.rect.x = self.hitrect.x = SCREEN_WIDTH // 2 + 2
        self.rect.y = SCREEN_HEIGHT - 48
        self.hitrect.y = SCREEN_HEIGHT - 24
        self.orientation = 2
        self.curr = 0
        self.dash = 60
        self.time_bonus = FPS * 30


class Player2(Player):
    def __init__(self):
        super(Player2, self).__init__()
        self.sheet = SpriteSheet(player_two_image)
        self.score = 0
        self.time_bonus = FPS * 30

    def update(self, pressed_keys):
        if pressed_keys[K_w]:
            self.movu()
        elif pressed_keys[K_s]:
            self.movd()
        elif pressed_keys[K_a]:
            self.movl()
        elif pressed_keys[K_d]:
            self.movr()
        else:
            self.curr = 0
        self.update_score()
        self.update_time()

    def update_score(self):
        self.score = max((self.hitrect.bottom - 96) // 96 * 100, self.score)
        if self.score == 700:
            game.player_win()

    def reset(self):
        self.rect.x = self.hitrect.x = SCREEN_WIDTH // 2
        self.rect.y = 48
        self.hitrect.y = 48 + 24
        self.orientation = 0
        self.curr = 0
        self.dash = 60
        self.time_bonus = FPS * 30


# main game class handles most of the blitting and text updation
# levels and worlds are also handled through it

class Game():
    def __init__(self, player, other):
        self.player_pointer = 0
        self.players = [player, other]
        self.round_score = [0, 0]
        self.totol_score = [0, 0]
        self.player_name = [player_one_name, player_two_name]
        self.currentPlayer = self.players[self.player_pointer]
        self.currentWorld = 0
        self.font = pygame.font.Font(base_font, 24)
        self.next_world()
        self.time = pygame.Surface((32, 32))
        self.timrect = self.time.get_rect()

    def create_game(self):
        self.spawn_player()
        self.make_trees()
        self.create_enemies()

    def spawn_player(self):
        for person in self.players:
            person.reset()
        self.currentPlayer = self.players[self.player_pointer]

    def make_trees(self):
        self.diff = int(self.currentWorld * 1.225 + 4)
        self.tree_list = pygame.sprite.Group()
        for rep in range(self.diff):
            for i in range(10):
                new_tree = Tree()
                uniq = True
                for tree in self.tree_list:
                    if tree.rect.left == new_tree.rect.left \
                            and tree.rect.top == new_tree.rect.top:
                        uniq = False
                        break
                if uniq:
                    self.tree_list.add(new_tree)
        for y in range(1, 8):
            cnt = 0
            for trees in self.tree_list:
                if trees.rect.top == y * 96:
                    cnt += 1
            if cnt > 7:
                x = random.randint(0, 7) * 64
                for trees in self.tree_list:
                    if trees.rect.y == y * 96 and trees.rect.x == x:
                        self.tree_list.remove(trees)

    def create_enemies(self):
        self.enemy_list = pygame.sprite.Group()
        begin = 1 if self.currentWorld == 1 else 0
        end = 3 if self.currentWorld >= 3 else 2
        base_speed = min(self.currentWorld * 1.35, 4)
        animation_cycle = 6 if self.currentWorld <= 3 else 4
        for i in range(2, 8):
            for rep in range(begin, end):
                new_enemy = Enemy(
                    (4 * i + rep) * 24,
                    base_speed,
                    animation_cycle)
                self.enemy_list.add(new_enemy)

    def local_box(self):
        self.currentPlayer.playicon.fill((0, 136, 255))
        self.currentPlayer.playicon.set_colorkey((0, 136, 255))
        self.currentPlayer.playicon_image = self.currentPlayer.sheet.get_img(
            178, 178, 54, 54)
        self.currentPlayer.playicon_image = pygame.transform.scale(
            self.currentPlayer.playicon_image, (120, 120))
        self.currentPlayer.playicon.blit(
            self.currentPlayer.playicon_image, (0, 0))
        screen.blit(self.currentPlayer.playicon,
                    self.currentPlayer.playicon_rect)
        self.display_message_at_pos("Time: " + str(self.backtimer()),
                                    SCREEN_WIDTH, SCREEN_HEIGHT, text_color)
        self.display_message_cent("Score: " +
                                  str(self.currentPlayer.get_score()),
                                  (SCREEN_WIDTH // 2, SCREEN_HEIGHT + 16),
                                  text_color)
        if self.totol_score[1] > self.totol_score[0]:
            message = self.player_name[1] + " leads by " + \
                str(self.totol_score[1] - self.totol_score[0]) + " points"
        elif self.totol_score[0] > self.totol_score[1]:
            message = self.player_name[0] + " leads by " + \
                str(self.totol_score[0] - self.totol_score[1]) + " points"
        else:
            message = no_lead_message
        self.display_message_at_pos(
            message, SCREEN_WIDTH, SCREEN_HEIGHT + 70, text_color)

    def display_message_cent(self, message, position, color):
        self.to_say = self.font.render(message, True, color)
        self.font_rect = self.to_say.get_rect()
        self.font_rect.center = position
        screen.blit(self.to_say, self.font_rect)

    def display_message_at_pos(self, message, x, y, color):
        self.to_say = self.font.render(message, True, color)
        self.font_rect = self.to_say.get_rect()
        self.font_rect.x = x - self.to_say.get_width() - 3
        self.font_rect.y = y + 4
        screen.blit(self.to_say, self.font_rect)

    def player_death(self, type):
        time.sleep(0.3)
        self.currentPlayer.score = 0
        self.currentPlayer.time_bonus = 0
        if type == 1:
            message = enemy_kill_message + \
                self.player_name[self.player_pointer] + "."
        elif type == 2:
            message = self.player_name[self.player_pointer] + \
                tree_kill_message
        else:
            message = self.player_name[self.player_pointer] + \
                time_kill_message
        self.player_pointer = self.player_pointer ^ 1
        screen.fill(background_color)
        self.display_message_cent(
            message, (SCREEN_WIDTH // 2, (SCREEN_HEIGHT + 120) // 2),
            heading_color)
        pygame.display.flip()
        self.spawn_player()
        self.create_enemies()
        time.sleep(0.9)
        if self.player_pointer == 0:
            self.next_world()
        else:
            self.player_announcement()

    def next_world(self):
        for i in range(0, 2):
            self.totol_score[i] += self.round_score[i]
        self.currentWorld += 1
        self.round_score = [0, 0]
        for play in self.players:
            play.score = 0
        message = "World: " + str(self.currentWorld)
        screen.fill(background_color)
        self.display_message_cent(
            message, (SCREEN_WIDTH // 2, (SCREEN_HEIGHT + 120) // 2),
            heading_color)
        pygame.display.flip()
        self.create_game()
        time.sleep(0.8)
        self.player_announcement()

    def player_announcement(self):
        message = self.player_name[self.player_pointer] + "'s Turn"
        screen.fill(background_color)
        self.display_message_cent(
            message, (SCREEN_WIDTH // 2, (SCREEN_HEIGHT + 120) // 2),
            heading_color)
        pygame.display.flip()
        time.sleep(1.1)

    def player_win(self):
        self.round_score[self.player_pointer] = self.currentPlayer.get_score(
        ) + (self.currentWorld - 1) * 200
        message = self.player_name[self.player_pointer] + \
            " got: " + str((self.currentWorld) * 200) + " round bonus"
        message2 = "Total: " + \
            str(self.round_score[self.player_pointer]) + " points"
        self.player_pointer ^= 1
        time.sleep(0.3)
        screen.fill(background_color)
        self.display_message_cent(
            message, (SCREEN_WIDTH // 2, (SCREEN_HEIGHT) // 2),
            heading_color)
        self.display_message_cent(
            message2, (SCREEN_WIDTH // 2, (SCREEN_HEIGHT + 120) // 2),
            heading_color)
        pygame.display.flip()
        time.sleep(0.9)
        if self.player_pointer == 0:
            self.next_world()
            return
        self.spawn_player()
        self.create_enemies()
        self.player_announcement()

    def declare_winner(self):
        screen.fill(background_color)
        if self.totol_score[1] > self.totol_score[0]:
            message = self.player_name[1] + " won by " + \
                str(self.totol_score[1] - self.totol_score[0]) + " points"
        elif self.totol_score[0] > self.totol_score[1]:
            message = self.player_name[0] + " won by " + \
                str(self.totol_score[0] - self.totol_score[1]) + " points"
        else:
            message = tie_message
        self.display_message_cent(
            message, (SCREEN_WIDTH // 2, (SCREEN_HEIGHT) // 2),
            heading_color)
        pygame.display.flip()
        time.sleep(0.9)

    def backtimer(self):
        return (self.currentPlayer.time_bonus + FPS - 1) // FPS


pygame.init()
ani = 6
player = Player1()
other = Player2()
game = Game(player, other)
bc = pygame.image.load(background_image)
running = True

# main game loop

while running:
    CLOCK.tick(FPS)

    #key commands and inputs
    
    for event in pygame.event.get():
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                game.declare_winner()
                running = False
            if event.key == K_SPACE and game.currentPlayer == player:
                if player.dash > 10:
                    player.fast()
                    player.dashing = True
            if event.key == K_v and game.currentPlayer == other:
                if other.dash > 10:
                    other.fast()
                    other.dashing = True
            if event.key == K_BACKSPACE:
                pause = True
                screen.fill(background_color)
                message = pause_message
                game.display_message_cent(
                    message, (SCREEN_WIDTH // 2, (SCREEN_HEIGHT) // 2),
                             heading_color)
                while pause:
                    pygame.display.update()
                    CLOCK.tick(FPS)
                    for event in pygame.event.get():
                        if event.type == KEYDOWN:
                            if event.key == K_BACKSPACE:
                                pause = False
                                break

        elif event.type == QUIT:
            game.declare_winner()
            running = False
        elif event.type == KEYUP:
            if event.key == K_SPACE and game.currentPlayer == player:
                player.slow()
                player.dashing = False
            if event.key == K_v and game.currentPlayer == other:
                other.slow()
                other.dashing = False
    
    # giving inputs to player

    pressed_keys = pygame.key.get_pressed()
    game.currentPlayer.update(pressed_keys)
    screen.blit(bc, (0, 0))
    
    # ckecking for collision with enemies
    
    for enemieses in game.enemy_list:
        enemieses.play()
        if game.currentPlayer.hitrect.colliderect(enemieses.hitrect):
            game.player_death(1)
    
    # sequential loading of trees
    
    for obj in game.tree_list:
        if obj.rect.y + 96 <= game.currentPlayer.hitrect.y:
            obj.play()
    for person in game.players:
        person.play()
    for obj in game.tree_list:
        if obj.rect.y + 96 > game.currentPlayer.hitrect.y:
            obj.play()
    
    #update statistics using this function
    
    game.local_box()

    #update global timer
    
    game.backtimer()
    pygame.display.flip()
