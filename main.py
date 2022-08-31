import pygame
import sprite_animation
# from goomba import Goomba
from pygame import mixer

pygame.init()
pygame.display.init()
pygame.font.init()
mixer.init()

JUMP_TURN = 1
JUMP_SPEED = 3
F_SECOND = 1
SCREEN_WIDTH,SCREEN_HEIGHT = 800,600
FONT = pygame.font.SysFont("arial",16)
WHITE = (255,255,255)
BLACK = (0,0,0)
fps = 30
fall_speed = round(90/fps,1)

background_channel =mixer.Channel(0)
charactor_channel = mixer.Channel(1)
block_channel = mixer.Channel(2)
run_about = mixer.Sound("Running_About.mp3")
jump_sound = mixer.Sound("jump-small.wav")
bump_sound = mixer.Sound("bump.wav")
mario_dead_sound = mixer.Sound("mario_die.wav")
stage_clear_sound = mixer.Sound("stage_clear.wav")

background_channel.play(run_about)
sprite_sheet = pygame.image.load("sprite_sheet.gif")
tiles_sheet = pygame.image.load("tiles.png")
castle_image = pygame.image.load("castle.png")

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.check_point = check_point.check_point1
        self.state = "right_stand"
        self.right_side = ["right_stand","right_run","right_jump"]
        self.left_side = ["left_stand","left_run","left_jump"]

        self.animation  =  sprite_animation.MarioAnimation(sprite_sheet)
        mario = self.animation.update(self.state,0)
        self.image = mario
        self.rect = self.image.get_rect()
        self.rect.x = self.check_point[0]
        self.rect.y = self.check_point[1]
        self.width = self.rect.width
        self.height = self.rect.height

        self.is_jumping = False
        self.is_falling = False

        self.jump_count = 10
        self.jump_turns = 0
        self.f_sec = F_SECOND

        self.speed = 300 / fps
        self.life = 10

    def update(self):
        global camera
        if self.life > 0:
            if self.state != "dead":
                check_point.check()
                if self.state in self.right_side:
                    self.state = "right_stand"
                if self.state in self.left_side:
                    self.state = "left_stand"
                keys = pygame.key.get_pressed()
                now_x_y = (self.rect.x,self.rect.y)
                if keys[pygame.K_d]:
                    self.move_right()
                if keys[pygame.K_a]:
                    self.move_left()
                if keys[pygame.K_w]:
                    self.is_jumping = True
                    self.jump_turns -= 1
                self.jump()
                self.fall()
                self.move_camera()

                mario = self.animation.update(self.state, 3)
                self.image = mario
            else:
                self.image = self.animation.update(self.state,0)
                print(self.image==self.animation.mario_dead)
                self.death_animation()
        else:
            pygame.quit()
            print("game_over")




        # self.rect = self.image.get_rect()

    def jump(self):
        global jump_sound

        if self.jump_count <= 0:
            self.is_jumping = False
        elif self.is_falling:
            self.is_jumping = False

        self.next_y = self.jump_count*JUMP_SPEED
        self.collide_block = []

        if self.is_jumping:
            if not charactor_channel.get_busy():
                charactor_channel.play(jump_sound)
            if self.state in self.right_side:
                self.state = "right_jump"
            elif self.state in self.left_side:
                self.state = "left_jump"

            for block in blocks:
                if block.rect.y + block.height > self.rect.y - self.next_y and self.rect.x > block.rect.x - self.width and self.rect.x < block.rect.x + block.width and self.rect.y > block.rect.y:
                    self.collide_block.append(block)
            if len(self.collide_block)==0:
                self.rect.y -= self.next_y
                self.jump_count -= 1
            elif len(self.collide_block)>=0:
                self.rect.y = self.collide_block[0].rect.y+self.width
                self.is_jumping = False
                self.jump_count = 10
                for block in self.collide_block:
                    f_block = 10000
                    if abs(block.rect.x - self.rect.x)<f_block:
                        f_block = abs(block.rect.x - self.rect.x)
                        self.collide_block = block
                if self.collide_block.type == "special":
                        self.collide_block.is_bump = True
        else:
            self.jump_count = 10

    def fall(self):
        if self.rect.y >800:
            self.lose_life()
        self.next_y = self.f_sec * fall_speed
        self.stump_monster = []
        self.collide_block = []
        if self.is_jumping == False:
            self.is_falling = True
        else:
            self.is_falling = False
        if self.is_falling == True:
            for block in blocks:#detect collision with blocks
                if block.rect.y < self.rect.y + self.next_y+self.height and self.rect.x > block.rect.x - self.width and self.rect.x < block.rect.x + block.width and self.rect.y<block.rect.y:
                    self.is_falling = False
                    self.jump_turns = JUMP_TURN
                    self.f_sec = F_SECOND
                    self.collide_block.append(block)
            for goomba in goombas:#detect if stamp monster
                if goomba.rect.y < self.rect.y + self.next_y+goomba.height and self.rect.x > goomba.rect.x - self.width and self.rect.x < goomba.rect.x + goomba.width and self.rect.y<goomba.rect.y:
                    # self.jump_turns = JUMP_TURN
                    self.stump_monster.append(goomba)
                    self.jump_count = 5
                    self.is_jumping = True
            for koopa in koopas:
                if koopa.rect.y < self.rect.y + self.next_y+koopa.height and self.rect.x > koopa.rect.x - self.width and self.rect.x < koopa.rect.x + koopa.width and self.rect.y<koopa.rect.y:
                    # self.jump_turns = JUMP_TURN
                    self.stump_monster.append(koopa)
                    self.jump_count = 5
                    self.is_jumping = True

            if len(self.stump_monster)>0:
                self.collide_mos = ""
                f_mons = 100000
                for mons in self.stump_monster:
                    if mons in koopas:
                        if mons.is_spinning and mons.shell_time <=0:
                            self.lose_life()

                    if abs(mons.rect.x - self.rect.x)<f_mons:
                        f_mons = abs(mons.rect.x - self.rect.x)
                        self.collide_mons = mons
                if self.collide_mons.life>0:
                    if self.collide_mons in koopas:
                        self.collide_mons.spin()
                        self.collide_mons.lose_life()
                    else:
                        self.collide_mons.lose_life()
                        self.collide_mons.state = "crushed"

            if len(self.collide_block)==0 and len(self.stump_monster)==0:
                self.rect.y += self.next_y
                self.f_sec += 1

            elif len(self.collide_block)>0 and len(self.stump_monster)==0:
                f_block = 100000
                for d_block in self.collide_block:
                    if d_block.rect.y < f_block:
                        f_block = d_block.rect.y
                self.rect.y = d_block.rect.y-self.width
                # self.rect.y = self.collide_block[0].rect.y - 40

        else:
            self.f_sec = F_SECOND
    def move_camera(self):
        global camera
        if self.rect.x + camera[0] > 300:
            camera = ((camera[0]-(self.rect.x+camera[0]-300)),0)
    def move_right(self):
        self.detect_col = False
        for block in blocks:
            if self.rect.y > block.rect.y - self.height and self.rect.y < block.rect.y + self.height and self.rect.x + self.width + self.speed > block.rect.x and self.rect.x < block.rect.x:
                self.detect_col = True
                break
        if self.detect_col == False:
            self.rect.x += self.speed
            self.state = "right_run"
        else:
            self.rect.x = block.rect.x - self.width

    def move_left(self):
        global camera

        self.detect_col = False
        for block in blocks:
            if self.rect.y > block.rect.y - self.height and self.rect.y < block.rect.y + self.height and self.rect.x - self.speed < block.rect.x + block.width and self.rect.x > block.rect.x:
                self.detect_col = True
                break
        if self.detect_col == False:
            if self.rect.x - self.speed >= -camera[0]:
                self.rect.x -= self.speed
                self.state = "left_run"
        else:
            if block.rect.x + 40 >= -camera[0]:
                self.rect.x = block.rect.x + block.width


    def lose_life(self):
        global camera
        self.state = "dead"
        self.life -= 1
        self.jump_count = 10
        self.is_jumping =True
        self.f_sec = 0
        self.wait_count = 10
        charactor_channel.play(mario_dead_sound)

    def death_animation(self):
        global goombas ,koopas
        global camera
        background_channel.pause()
        if self.wait_count <= 0:
            if self.is_jumping:
                if self.jump_count > 0:
                    self.rect.y -= self.jump_count*2
                    self.jump_count-=1
                else:
                    self.is_jumping = False
            else:
                if self.f_sec <=30:
                    self.f_sec += 1
                    self.rect.y += self.f_sec*2
                else:
                    self.state = "right_stand"
                    self.rect.x = self.check_point[0]
                    self.rect.y = self.check_point[1]
                    camera=pygame.Vector2(-self.check_point[0],0)
                    background_channel.unpause()
                    goombas = pygame.sprite.Group()
                    koopas = pygame.sprite.Group()
                    create_monsters()

        else:
            self.wait_count-=1




class Block(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        brick_image = pygame.image.load("brick.png")
        bigger_brick = pygame.transform.scale(brick_image,(40,40))

        self.image = pygame.transform.scale(sprite_animation.take_image(tiles_sheet,0,0,16,16),(40,40))
        self.rect = self.image.get_rect()
        self.rect.x = 0
        self.rect.y = 0
        self.type = "block"
        self.width = self.rect.width
        self.height = self.rect.height
        self.bump_animation_count = 5
        self.is_bump = False
    def bump(self):
        if self.is_bump:
            self.bump_animation()
            if not charactor_channel.get_busy():
                charactor_channel.play(bump_sound)
    def bump_animation(self):
        if self.bump_animation_count >= -5:
            self.rect.y += 3
            self.rect.y -= self.bump_animation_count*1
        else:
            self.bump_animation_count=5
            self.is_bump = False
    def update(self):
        self.bump()
class Coin(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        coin_image = pygame.image.load("coin.png")
        smaller_coin = pygame.transform.scale(coin_image,(20,20))
        self.image = smaller_coin
        self.rect = self.image.get_rect()
        self.rect.x = 0
        self.rect.y = 0
        self.type = "coin"
        self.width = self.rect.width
        self.height = self.rect.height

        self.jump_count = 20
        self.is_jump = False
    def jump_animation(self):
        global coin_number,coins
        if self.jump_count <= 0:
            coins.remove(self)
            coin_number += 1
        if self.is_jump:
            self.rect.y -= 0.5*self.jump_count
            self.jump_count -= 1
    def update(self):
        self.jump_animation()
class SpecialBLock(Block):
    def __init__(self):
        super().__init__()
        special_block_image = pygame.image.load("special_block.png")
        smaller_special_block_image = pygame.transform.scale(special_block_image,(40,40))
        self.image = smaller_special_block_image
        self.type = "special"
        self.has_coin = True
        self.width = self.rect.width
        self.height = self.rect.height
        self.bump_animation_count = 5
        self.is_bump = False
    def bump(self):
        if self.is_bump:
            if self.has_coin:
                coin = Coin()
                coin.rect.x = self.rect.x+15
                coin.rect.y = self.rect.y+10
                coins.add(coin)
                coin.is_jump = True
                self.has_coin = False
                bumped_special = pygame.image.load("bumped_special.png")
                smaller_special = pygame.transform.scale(bumped_special,(40,40))
                self.image = smaller_special
            self.bump_animation()
            if not charactor_channel.get_busy():
                charactor_channel.play(bump_sound)

    def bump_animation(self):
        if self.bump_animation_count >= -5:
            self.rect.y -= self.bump_animation_count*1
            self.bump_animation_count -= 1
        else:
            self.bump_animation_count=5
            self.is_bump = False
    def update(self):
        self.bump()
class Goomba(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.state = "sleep"
        self.animation = sprite_animation.GoombaAnimation(sprite_sheet)
        self.image = self.animation.update(self.state,0)

        self.rect = self.image.get_rect()
        self.rect.x = 0
        self.rect.y = 0
        self.speed = 100 / fps
        self.life = 1
        self.death_animation_count = 10
        self.width = self.rect.width
        self.height = self.rect.height
        self.f_sec = 1
    def fall(self):
        self.next_y = self.f_sec *3
        for block in blocks:  # detect collision with blocks
            if block.rect.y < self.rect.y + self.next_y + self.height and self.rect.x > block.rect.x - self.width and self.rect.x < block.rect.x + block.width and self.rect.y < block.rect.y:
                self.rect.y = block.rect.y-40
                self.f_sec = 1
                return
        self.rect.y += self.next_y
        self.f_sec +=1

    def wake(self):
        if player.rect.x + 600 > self.rect.x and self.state == "sleep":
            self.state = "left"
    def move(self):
        self.detect = False
        if self.state == "left":
            for block in blocks:
                if block.rect.y - self.height < self.rect.y < block.rect.y + self.height and self.rect.x-block.width-self.speed < block.rect.x and self.rect.x>block.rect.x:
                    self.detect = True
                    self.state = "right"
                    break
            if self.detect:
                self.rect.x = block.rect.x +block.width
            else:
                self.rect.x -= self.speed
        elif self.state == "right":
            for block in blocks:
                if block.rect.y - self.height < self.rect.y < block.rect.y +self.height and self.rect.x+self.width+self.speed > block.rect.x and self.rect.x<block.rect.x:
                    self.detect = True
                    self.state = "left"
                    break
            if self.detect:
                self.rect.x = block.rect.x - self.width
            else:
                self.rect.x += self.speed
    def is_alive(self):
        if self.life <= 0 :
            if self.state == "crushed":
                crushed_goomba_image = sprite_animation.take_image(sprite_sheet, 277, 195, 16, 8)
                crushed_goomba_image = pygame.transform.scale(crushed_goomba_image, (40, 20))
                self.width = self.rect.width
                self.height = self.rect.height
                self.image = crushed_goomba_image
                self.rect = self.image.get_rect()
                self.rect.x = self.x_before
                self.rect.y = self.y_before+20
        if self.rect.y>=800:
            self.lose_life()
            print(0)

    def collide_player(self):
        if self.rect.colliderect(player.rect):
            player.lose_life()

    def update(self):
        self.is_alive()
        if self.life>0:
            self.wake()
            if player.state != "dead":
                self.move()
                self.collide_player()
                goomba = self.animation.update(self.state, 2)
                self.image = goomba
            self.fall()
        elif self.death_animation_count>=0:
            self.death_animation_count -= 1
        else:
            goombas.remove(self)
    def lose_life(self):
        self.life -= 1
        self.x_before = self.rect.x
        self.y_before = self.rect.y
class TubeBody(Block):
    def __init__(self):
        super().__init__()
        tube_body_image = pygame.image.load("tube_body.png").convert()
        smaller_tube_body = pygame.transform.scale(tube_body_image,(80,40))
        self.image = smaller_tube_body
        self.rect = self.image.get_rect()
        self.rect.x = 0
        self.rect.y = 0
        self.width = 80
        self.height = 40
class TubeEntrance(Block):
    def __init__(self):
        super().__init__()
        self.width = 80
        self.height = 40
        tube_entrance_image = pygame.image.load("tube_entrance.png").convert()
        smaller_entrance = pygame.transform.scale(tube_entrance_image,(80,40))
        self.image = smaller_entrance
        self.rect = self.image.get_rect()
        self.rect.x = 0
        self.rect.y = 0
        self.width = 80
        self.height = 40
class CheckPoint():
    def __init__(self):
        self.check_point1 = [40,400]
        self.check_point2 = [37*40,400]
        self.check_point3 = [67 * 40, 400]
        self.check_point4 = [79 * 40, 400]
        self.check_point5 = [92 * 40, 400]
        self.check_point6 = [128 * 40, 400]
        self.check_point7 = [147 * 40, 400]
        self.check_point8 = [164 * 40, 400]


    def check(self):
        if player.rect.x>=self.check_point1[0]:
            player.check_point=self.check_point1
        if player.rect.x >=self.check_point2[0]:
            player.check_point = self.check_point2
        if player.rect.x >=self.check_point3[0]:
            player.check_point = self.check_point3
        if player.rect.x >=self.check_point4[0]:
            player.check_point = self.check_point4
        if player.rect.x >=self.check_point5[0]:
            player.check_point = self.check_point5
        if player.rect.x >=self.check_point6[0]:
            player.check_point = self.check_point6
        if player.rect.x >=self.check_point7[0]:
            player.check_point = self.check_point7
        if player.rect.x >=self.check_point8[0]:
            player.check_point = self.check_point8
class Castle(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.width = 240
        self.height = 280
        self.type = "castle"
        self.image = sprite_animation.take_image(pygame.transform.scale(castle_image,(610,339)),185,30,240,280)
        self.image.set_colorkey(self.image.get_at((0,0)))
        self.rect = self.image.get_rect()
        self.rect.x = 0
        self.rect.y = 0
class Koopa(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.type = "koopas"
        self.width = 40
        self.height = 60
        self.speed = 100/fps
        self.state = "sleep"
        self.animation = sprite_animation.KoopaAnimation(sprite_sheet)
        self.life = 1
        self.image = self.animation.koopa_left1
        self.rect = self.image.get_rect()
        self.is_spinning = False
        self.rect.x = 0
        self.rect.y = 0
        self.shell_time = 20
        self.f_sec = 0
    def fall(self):
        self.next_y = self.f_sec *3
        for block in blocks:  # detect collision with blocks
            if block.rect.y < self.rect.y + self.next_y + self.height and self.rect.x > block.rect.x - self.width and self.rect.x < block.rect.x + block.width and self.rect.y < block.rect.y:
                self.rect.y = block.rect.y-40
                self.f_sec = 1
                return
        self.rect.y += self.next_y
        self.f_sec +=1
    def update(self):
        if self.life>0:
            if player.state != "dead":
                self.wake()
                self.move()
                self.collide_player()
        elif self.life <= 0 and self.state == "shell":
            self.spin()
        elif self.life <= 0 and self.is_spinning and self.shell_time>=-40:
            self.shell_time -= 1
            if player.state != "dead":
                self.spinning()
                self.collide_all()
        else:
            koopas.remove(self)
        koopa = self.animation.update(self.state,3)
        self.image = koopa
    def wake(self):
        if player.rect.x + 600 > self.rect.x and self.state == "sleep":
            self.state = "left"
    def move(self):
        self.detect = False
        if self.state == "left":
            for block in blocks:
                if block.rect.y - self.height < self.rect.y < block.rect.y + self.height and self.rect.x - block.width - self.speed < block.rect.x and self.rect.x > block.rect.x:
                    self.detect = True
                    self.state = "right"
                    break
            if self.detect:
                self.rect.x = block.rect.x + block.width
            else:
                self.rect.x -= self.speed
        elif self.state == "right":
            for block in blocks:
                if block.rect.y - self.height < self.rect.y < block.rect.y + self.height and self.rect.x + self.width + self.speed > block.rect.x and self.rect.x < block.rect.x:
                    self.detect = True
                    self.state = "left"
                    break
            if self.detect:
                self.rect.x = block.rect.x - self.width
            else:
                self.rect.x += self.speed
    def collide_player(self):
        if self.rect.colliderect(player.rect):
            player.lose_life()
    def lose_life(self):
        self.life -=1
        self.state = "shell"
        self.image = self.animation.update("shell_left",0)
        self.speed = 400/fps
        self.x_y=[self.rect.x,self.rect.y]
        self.rect= self.image.get_rect()
        self.rect.x = self.x_y[0]
        self.rect.y = self.x_y[1]+20
        self.height = 40
        self.width = 40
    def spinning(self):
        self.detect = False
        if self.state == "shell_left":
            for block in blocks:
                if block.rect.y - self.height < self.rect.y < block.rect.y + self.height and self.rect.x - block.width - self.speed < block.rect.x and self.rect.x > block.rect.x:
                    self.detect = True
                    self.state = "shell_right"
                    break
            if self.detect:
                self.rect.x = block.rect.x + block.width
            else:
                self.rect.x -= self.speed
        elif self.state == "shell_right":
            for block in blocks:
                if block.rect.y - self.height < self.rect.y < block.rect.y + self.height and self.rect.x + self.width + self.speed > block.rect.x and self.rect.x < block.rect.x:
                    self.detect = True
                    self.state = "shell_left"
                    break
            if self.detect:
                self.rect.x = block.rect.x - self.width
            else:

                self.rect.x += self.speed
    def spin(self):

        if player.rect.x+20 <= self.rect.x +20 and self.state == "shell" and self.rect.colliderect(player.rect):
            self.state = "shell_left"
            self.is_spinning = True
        else:
            self.state = "shell_right"
            self.is_spinning = True
        # self.state = "shell_left"
        # self.is_spinning = True
    def collide_all(self):
        for goomba in goombas:
            if goomba.rect.colliderect(self.rect):
                goomba.lose_life()
                goomba.state = "dead"
        if self.rect.colliderect(player.rect):
            player.lose_life()
class Iron_block(Block):
    def __init__(self):
        super().__init__()
        self.image=pygame.transform.scale(sprite_animation.take_image(tiles_sheet,0,16,16,16),(40,40))
        
class Brick(Block):
    def __init__(self):
        super(Brick, self).__init__()
        self.image = pygame.transform.scale(sprite_animation.take_image(tiles_sheet,16,0,16,16),(40,40))
    def bump(self):
        super(Brick, self).bump()
    def bump_animation(self):
        super(Brick, self).bump_animation()
class Flag():
    def __init__(self):
        self.image = pygame.image.load("flag.png")
        self.image = sprite_animation.take_image(self.image,0,0,337,947)
        self.image = pygame.transform.scale(self.image,(60,500))
        self.rect = self.image.get_rect()
        self.rect.x = 0
        self.rect.y = 0
        self.is_finish = False
    def check_is_end(self):
        global is_end
        if player.rect.colliderect(self) and not is_end:
            is_end = True
            player.rect.x = self.rect.x+20
    def animation(self):
        if player.rect.y+40<self.rect.y+500 and self.is_finish == False:
            player.rect.y += 5
            player.image = player.animation.mario_climb
        else:
            self.is_finish = True
            player.rect.y = self.rect.y+500-player.height
    def go_animation(self):
        if self.is_finish and player.rect.x<200*40:
            player.image = player.animation.update("right_run",4)
            player.rect.x+=10
        elif self.is_finish:
            player.image=pygame.Surface((40,40))
            player.image.fill(WHITE)
            player.image.set_colorkey(WHITE)
        else:
            pass










def create_block(x,y):
    block = Block()
    block.rect.x = x
    block.rect.y = y
    blocks.add(block)

def update_whole():
    global coin,stage_clear_num
    back = pygame.Surface((10000,3000))
    background = pygame.Surface((10000, 600))
    background.fill(WHITE)
    if True:
        flag.check_is_end()
        background.blit(flag.image, (flag.rect.x, flag.rect.y))
        for block in blocks:
            if -camera[0]-100<block.rect.x<-camera[0]+800+100:
                background.blit(block.image, (block.rect.x, block.rect.y))
                block.update()
        if not is_end:
            player.update()
            for coin in coins:
                coin.update()
                background.blit(coin.image,(coin.rect.x,coin.rect.y))
            background.blit(player.image, (player.rect.x, player.rect.y))
            if True:
                goombas.update()
                for goomba in goombas:
                        background.blit(goomba.image,(goomba.rect.x,goomba.rect.y))
                koopas.update()
                for koopa in koopas:
                    background.blit(koopa.image,(koopa.rect.x,koopa.rect.y))
            window.blit(back,(-500,-500))
    if is_end:
        if stage_clear_num > 0:
            print(0)
            background_channel.stop()
            background_channel.play(stage_clear_sound)
            stage_clear_num -= 1

        flag.animation()
        flag.go_animation()

        background.blit(flag.image, (flag.rect.x, flag.rect.y))
        background.blit(player.image, (player.rect.x, player.rect.y))

    window.blit(background, camera)

    coin_text = FONT.render(f"coin:{coin_number}", True, BLACK)
    window.blit(coin_text,(200,50))
    coins.update()
def create_iron_block(x,y):
    block = Iron_block()
    block.rect.x = x
    block.rect.y = y
    blocks.add(block)
def create_brick(x,y):
    block = Brick()
    block.rect.x = x
    block.rect.y = y
    blocks.add(block)
def create_special_block(x,y):
    special_block  = SpecialBLock()
    special_block.rect.x = x
    special_block.rect.y = y
    blocks.add(special_block)
def create_goomba(x, y):
    goomba = Goomba()
    goomba.rect.x = x
    goomba.rect.y = y
    goombas.add(goomba)
def create_tube(length,x,y):
    for a in range(length-1):
        tube_body = TubeBody()
        tube_body.rect.x = x
        tube_body.rect.y = y-a*40
        blocks.add(tube_body)
    tube_entrance = TubeEntrance()
    tube_entrance.rect.x = x
    tube_entrance.rect.y = y-(a+1)*40
    blocks.add(tube_entrance)
def create_castle(x,y):
    castle = Castle()
    castle.rect.x = x
    castle.rect.y = y
    blocks.add(castle)
    print(castle)
def create_koopa(x,y):
    koopa = Koopa()
    koopa.rect.x = x
    koopa.rect.y = y
    koopas.add(koopa)
def create_steps_right(length,x,y):
    b = 0
    for c in range(length):
        for a in range(length-b):
            create_iron_block(x+length*40-a*40,y-b*40)
        b+=1
def create_steps_left(length,x,y):
    b = 0
    for c in range(length):
        for a in range(length - b):
            create_iron_block(x + a * 40, y - b * 40)
        b += 1
def create_monsters():
    create_goomba(22 * 40, 480)
    create_goomba(44 * 40, 480)
    create_goomba(54 * 40, 480)
    create_goomba(55 * 40, 480)
    create_goomba(79 * 40, 320)
    create_goomba(81 * 40, 320)
    create_goomba(100 * 40, 480)
    create_goomba(101 * 40, 480)
    create_koopa(105 * 40, 460)
    create_goomba(116 * 40, 480)
    create_goomba(118 * 40 - 20, 480)
    create_goomba(124 * 40, 480)
    create_goomba(126 * 40 - 20, 480)
    create_goomba(132 * 40, 480)
    create_goomba(134 * 40 - 20, 480)
    create_goomba(173 * 40, 480)
    create_goomba(174 * 40, 480)



window = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
coin_number = 0

clock = pygame.time.Clock()
camera = pygame.math.Vector2()
blocks = pygame.sprite.Group()
coins = pygame.sprite.Group()
goombas = pygame.sprite.Group()
koopas = pygame.sprite.Group()

check_point = CheckPoint()
player = Player()
stage_clear_num = 1
# build the background blocks
# def build_first_stage_map():
for a in range(2):
    for b in range(220):
        if b == 68 or b == 69 or b == 86 or b == 87 or b == 88 or b == 149 or b == 150:
            pass
        else:
            create_block(b*40,600-(a+1)*40)
for a in range(220):
    if a == 16 or a == 21 or a == 23 or a == 76 or a == 106 or a == 109 or a == 112 or a == 166:
        create_special_block(a*40,360)
    if a == 22 or a == 94 or a == 109 or a == 129 or a == 130:
        create_special_block(a*40,200)
    if a == 20 or a == 22 or a == 24 or a == 76 or a == 78 or a == 94 or a == 100 or a == 101 or a == 118 or a == 129 or a == 130 or a == 164 or a == 165 or a == 167:
        create_brick(a*40,360)
    if a == 128 or a == 131 or 81<=a<=87 or 91<=a<=93 or 121<=a<=123:
        create_brick(a*40,200)
create_tube(2,28*40,480)
create_tube(3, 38 * 40, 480)
create_tube(4, 45 * 40, 480)
create_tube(4, 56 * 40, 480)
create_tube(2, 159 * 40, 480)
create_tube(2, 175 * 40, 480)
create_monsters()

create_steps_right(4,134*40,480)
create_steps_left(4,140*40,480)
create_steps_right(4,144*40,480)
create_iron_block(148*40,480)
create_iron_block(148*40,440)
create_iron_block(148*40,400)
create_iron_block(148*40,360)
create_steps_left(4,151*40,480)
create_steps_right(8,177*40,480)
for a in range(7):
    create_iron_block(185*40,480-a*40)
flag = Flag()
flag.rect.x = 194*40
# flag.rect.x = 200
flag.rect.y = 20
create_castle(198*40,240)
create_iron_block(194*40+20,480)



is_end = False
# build_first_stage_map()
while (1):
    fps = round(clock.get_fps())
    try:
        fall_speed = round(90/fps,1)
    except ZeroDivisionError:
        fall_speed = 3
    print(fps)
    clock.tick(30)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
    update_whole()
    pygame.display.update()







