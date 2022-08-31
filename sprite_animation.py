import pygame

def take_image(sheet,x,y,width,height):
    image_rect = pygame.Rect((x,y),(width,height))
    image = pygame.Surface(image_rect.size)
    image.fill((90,93,42))
    color_key = image.get_at((0, 0))
    image.set_colorkey(color_key)
    image.blit(sheet,(0,0),image_rect)

    image = image.convert()

    return image

class MarioAnimation():
    def __init__(self,sheet):
        self.frame_per_sec = 0
        self.index = 0
        self.mario_standing_right = take_image(sheet, 276, 44, 16, 16)
        self.mario_standing_right = pygame.transform.scale(self.mario_standing_right, (40, 40))

        self.mario_running1_right = take_image(sheet, 290, 44, 16, 16)
        self.mario_running1_right = pygame.transform.scale(self.mario_running1_right, (40, 40))

        self.mario_running2_right = take_image(sheet, 304, 44, 16, 16)
        self.mario_running2_right = pygame.transform.scale(self.mario_running2_right, (40, 40))

        self.mario_running3_right = take_image(sheet, 321, 44, 16, 16)
        self.mario_running3_right = pygame.transform.scale(self.mario_running3_right, (40, 40))

        self.mario_jumping_right = take_image(sheet, 355, 44, 16, 16)
        self.mario_jumping_right = pygame.transform.scale(self.mario_jumping_right, (40, 40))



        self.mario_standing_left = take_image(sheet, 223,44, 16, 16)
        self.mario_standing_left = pygame.transform.scale(self.mario_standing_left, (40, 40))

        self.mario_running1_left = take_image(sheet,207, 44, 16, 16)
        self.mario_running1_left = pygame.transform.scale(self.mario_running1_left, (40, 40))

        self.mario_running2_left = take_image(sheet, 193, 44, 16, 16)
        self.mario_running2_left = pygame.transform.scale(self.mario_running2_left, (40, 40))

        self.mario_running3_left = take_image(sheet, 177, 44, 16, 16)
        self.mario_running3_left = pygame.transform.scale(self.mario_running3_left, (40, 40))

        self.mario_jumping_left = take_image(sheet, 141, 44, 16, 16)
        self.mario_jumping_left = pygame.transform.scale(self.mario_jumping_left, (40, 40))

        self.mario_dead = take_image(sheet,485,44,16,16)
        self.mario_dead = pygame.transform.scale(self.mario_dead,(40,40))

        self.mario_climb = pygame.transform.scale(take_image(sheet,373,44,16,16),(40,40))

        self.mario_right_run_animation = [self.mario_running1_right,self.mario_running2_right,self.mario_running3_right]
        self.mario_left_run_animation = [self.mario_running1_left,self.mario_running2_left,self.mario_running3_left]
    def update(self,state,frame_added):
        if state == "dead":
            return self.mario_dead
        if state == "right_stand":
            self.index = 0
            return self.mario_standing_right
        elif state == "left_stand":
            self.index = 0
            return self.mario_standing_left
        elif state == "left_jump":
            self.index = 0
            return self.mario_jumping_left
        elif state == "right_jump":
            self.index = 0
            return self.mario_jumping_right
        self.frame_per_sec += frame_added
        if self.frame_per_sec >= 7:
            self.frame_per_sec = self.frame_per_sec % 7
            if self.index >= 2:
                self.index = 0
            else:
                self.index += 1
        if state == "right_run":
            return self.mario_right_run_animation[self.index]
        elif state == "left_run":
            return self.mario_left_run_animation[self.index]


class GoombaAnimation():
    def __init__(self,sheet):
        self.index = 0
        self.frame_per_sec = 0

        self.goomba_left = take_image(sheet,296,187,16,16)
        self.goomba_left = pygame.transform.scale(self.goomba_left,(40,40))

        self.goomba_right = take_image(sheet,315,187,16,16)
        self.goomba_right = pygame.transform.scale(self.goomba_right, (40, 40))

        self.run_animation = [self.goomba_left,self.goomba_right]
    def update(self,state,frame_added):
        self.frame_per_sec+=frame_added
        # print(self.frame_per_sec)
        if self.frame_per_sec >= 20:
            self.frame_per_sec = self.frame_per_sec % 20
            if self.index >= 1:
                self.index = 0
            else:
                self.index += 1
        # print(self.index)
        return self.run_animation[self.index]
        # return self.goomba_left
class KoopaAnimation():
    def __init__(self,sheet):
        self.index = 0
        self.frame_per_sec = 0

        self.koopa_left1 = pygame.transform.scale(take_image(sheet,201,207,16,24),(40,60))
        self.koopa_left2 = pygame.transform.scale(take_image(sheet,182,207,16,24),(40,60))
        self.koopa_right1 = pygame.transform.scale(take_image(sheet, 296, 209, 16, 24), (40, 60))
        self.koopa_right2 = pygame.transform.scale(take_image(sheet, 315, 209, 16, 24), (40, 60))
        self.shell = pygame.transform.scale(take_image(sheet, 144, 215, 16, 16), (40, 40))

        self.left_run_animation = [self.koopa_left1,self.koopa_left2]
        self.right_run_animation = [self.koopa_right1,self.koopa_right2]

    def update(self, state, frame_added):
        self.frame_per_sec += frame_added
        if self.frame_per_sec >= 10:
            self.frame_per_sec = self.frame_per_sec % 10
            if self.index >= 1:
                self.index = 0
            else:
                self.index += 1
        if state == "sleep":
            return self.koopa_left1
        if state == "left":
            return self.left_run_animation[self.index]
        elif state == "right":
            return self.right_run_animation[self.index]
        elif state == "shell_left" or "shell_right":
            return self.shell
        else:
            return self.koopa_left1














