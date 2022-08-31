import pygame
from main import fps,goombas,player_pos,player_health

class Goomba(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.width = 40
        self.height =40
        gomba_image = pygame.image.load("mushroom_monster.png")
        smaller_gomba = pygame.transform.scale(gomba_image, (self.width, self.height))
        self.image = smaller_gomba
        self.rect = self.image.get_rect()
        self.rect.x = 0
        self.rect.y = 0
        self.speed = 100 / fps
        self.life = 1
        self.is_wake = False
        self.state = "left"
        self.death_animation_count = 30
    def wake(self):
        if player_pos[0] > self.rect.x:
            self.is_wake = True
    def move(self):
        self.detect = False
        if self.state == "left" and self.is_wake == True:
            for block in blocks:
                if block.rect.y - 40 < self.rect.y < block.rect.y +40 and self.rect.x-40-self.speed < block.rect.x and self.rect.x>block.rect.x:
                    self.detect = True
                    self.state = "right"
                    break
            if self.detect:
                self.rect.x = block.rect.x +40
            else:
                self.rect.x -= self.speed
        elif self.state == "right" and self.is_wake == True:
            for block in blocks:
                if block.rect.y - 40 < self.rect.y < block.rect.y +40 and self.rect.x+40+self.speed > block.rect.x and self.rect.x<block.rect.x:
                    self.detect = True
                    self.state = "left"
                    break
            if self.detect:
                self.rect.x = block.rect.x - 40
            else:
                self.rect.x += self.speed
    def is_alive(self):
        if self.life <= 0 :
            crushed_gomba = pygame.transform.scale(self.image,(40,20))
            # crushed_gomba = pygame.transform.scale(pygame.image.load("crushed_mush.png"),(40,20))
            self.image = crushed_gomba
            self.rect = self.image.get_rect()
            self.rect.x = self.x_before
            self.rect.y = self.y_before+20
    def collide_player(self):
        if self.rect.colliderect(player.rect):
            player.lose_life()

    def update(self):
        self.is_alive()
        if self.life>0:
            self.wake()
            self.move()
            self.collide_player()
        elif self.death_animation_count>=0:
            self.death_animation_count -= 1
        else:
            goombas.remove(self)
    def lose_life(self):
        self.life -= 1
        self.x_before = self.rect.x
        self.y_before = self.rect.y