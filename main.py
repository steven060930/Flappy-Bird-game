import pygame
from pygame import *
import time
import random
import sys, os

'''
param: K_SPACE for space key on the keyboard interavtive input

param: 

problem to fix:

-> the floor extending

features to be added:

-> the game over page
'''

pygame.init()
pygame.font.init()

WIN_WIDTH = 500
WIN_HEIGHT = 800
FLOOR = 730
FPS = 30
STAT_FONT = pygame.font.SysFont("comicsans", 25)
GAME_OVER_FONT = pygame.font.SysFont("comicsans", 40)
DRAW_LINES = False

bird_images = [pygame.transform.scale2x(pygame.image.load(os.path.join("assets", "bird1.png"))), pygame.transform.scale2x(pygame.image.load(os.path.join("assets", "bird2.png"))), pygame.transform.scale2x(pygame.image.load(os.path.join("assets", "bird3.png")))]
pipe_image = pygame.transform.scale2x(pygame.image.load(os.path.join("assets", "pipe.png")))
ground_image = pygame.transform.scale2x(pygame.image.load(os.path.join("assets", "base.png")))
background_image = pygame.transform.scale2x(pygame.image.load(os.path.join("assets", "bg.png")))

class Bird:
    IMGS = bird_images
    MAX_ROTATION = 25
    ROT_VEL = 20
    ANIMATION_TIME = 5

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.tilt = 0
        self.tick_count = 0
        self.velocity = 0
        self.height = self.y
        self.img_count = 0
        self.image = self.IMGS[0]

    def jump(self):
        self.velocity = -10 
        self.tick_count = 0
        self.height = self.y

    def move(self):
        self.tick_count += 1

        d = self.velocity *self.tick_count + 1.5 * self.tick_count**2
        # v0 + a t^2

        if d >= 0:
            d = min(16, d)
        else:
            d -= 2

        self.y += d

        if d < 0 or self.y < self.height + 50:
            if self.tilt < self.MAX_ROTATION:
                self.tilt = self.MAX_ROTATION
        else:
            if self.tilt > -90:
                self.tilt -= self.ROT_VEL
    
    def draw(self, win):
        self.img_count += 1

        if self.img_count < self.ANIMATION_TIME:
            self.image = self.IMGS[0]
        elif self.img_count < self.ANIMATION_TIME * 2:
            self.image = self.IMGS[1]
        elif self.img_count < self.ANIMATION_TIME * 3:
            self.image = self.IMGS[2]
        elif self.img_count < self.ANIMATION_TIME * 4:
            self.image = self.IMGS[1]
        elif self.img_count == self.ANIMATION_TIME * 4 + 1:
            self.img= self.IMGS[0]
            self.img_count = 0

        if self.tilt <= -80:
            self.img = self.IMGS[1]
            self.img_count = self.ANIMATION_TIME*2


        # rotate the image based on the center of the screen
        rotated_image = pygame.transform.rotate(self.image, self.tilt)
        new_rectangle = rotated_image.get_rect(center=self.image.get_rect(topleft = (self.x, self.y)).center)
        win.blit(rotated_image, new_rectangle.topleft)

    def get_mask(self):
        return pygame.mask.from_surface(self.image)

    
class Pipe:
    GAP = 200
    VEL = 5

    def __init__(self, x):
        self.x = x
        self.height = 0
        self.gap = 100

        self.top = 0
        self.bottom = 0

        # pipe_top is flipped upwards down
        self.PIPE_TOP = pygame.transform.flip(pipe_image, False, True)
        self.PIPE_BOTTOM = pipe_image
        
        self.passed = False
        self.set_height()

    def set_height(self):
        self.height = random.randrange(50, 450)
        self.top = self.height - self.PIPE_TOP.get_height()
        self.bottom = self.height + self.GAP

    def move(self):
        self.x -= self.VEL

    def draw(self, win):
        win.blit(self.PIPE_TOP, (self.x, self.top))
        win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))

    def collide(self, bird):
        #return if the bird will collide with the pipe (the obstacle)
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)

        top_offset = (self.x - bird.x, self.top - round(bird.y))
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

        bottom_point = bird_mask.overlap(bottom_mask, bottom_offset)
        top_point = bird_mask.overlap(top_mask, top_offset)

        if bottom_point or top_point:
            return True
        else:
            return False


class Base:
    #keep the base dynamically moving forawrd
    VELOCITY = 5
    WIDTH = ground_image.get_width()
    IMG = ground_image

    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH

    def move(self):
        self.x1 -= self.VELOCITY
        self.x2 -= self.VELOCITY

        #extending the base (the ground) to the next game window
        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH
        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH

    def draw(self, win):
        win.blit(self.IMG, (self.x1, self.y))
        win.blit(self.IMG, (self.x1, self.y))


def draw_window(win, bird, pipes, base, score):
    current_highest_score = -1
    with open('historically_best_score.txt' , 'r') as reader:
        current_highest_score = int(reader.readline())

    win.blit(background_image, (0, 0))

    for pipe in pipes:
        pipe.draw(win)

    text = STAT_FONT.render("Score: " + str(score), 1, (255, 255, 255))
    win.blit(text, (WIN_WIDTH - 10 - text.get_width()-15, 10))

    highest_score_text = STAT_FONT.render("Historcially Best: " + str(current_highest_score), 1, (255, 255, 255))
    win.blit(highest_score_text, (10, 10))

    base.draw(win)
    bird.draw(win)

    pygame.display.update()

def draw_game_over_window(win):
    '''
    end the game, show the ending window
    '''

    win.fill((0, 120, 255))
    display_text = GAME_OVER_FONT.render("Game over", True, (255,255,255))
    text_box = display_text.get_rect()
    text_box.center = (WIN_WIDTH//2, WIN_HEIGHT//2) 
    win.blit(display_text, text_box)
    pygame.display.update()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit(0)


def main():
    score = 0
    bird = Bird(230, 300)
    #base is located at the bottom of the screen
    base = Base(730)
    pipes = [Pipe(700)]
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    display.set_caption('Flappy Fird Game Project')

    clock = pygame.time.Clock()

    run = True
    while run:
        #set frame per second
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        bird.move()
  
        memo = []
        add_pipe = False
        game_over = False

        for pipe in pipes:
            if pipe.collide(bird):
                game_over = True
                #run = False
            
            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                memo.append(pipe)

            if not pipe.passed and pipe.x < bird.x:
                pipe.passed = True
                add_pipe = True

            pipe.move()

        if add_pipe:
            score += 1
            pipes.append(Pipe(600))

        for r in memo:
            pipes.remove(r)

        if bird.y + bird.image.get_height() >= 730 or bird.y < 0:
            game_over = True
            #run = False

        base.move()
        draw_window(win, bird, pipes, base, score)


        keys_pressed = pygame.key.get_pressed()

        jumping = False
        if keys_pressed[pygame.K_SPACE]:
            jumping = True

        if jumping:
            bird.jump()

        mx_score =0
        with open('historically_best_score.txt', 'r') as reader:
            mx_score = int(reader.readline())

        if score >= mx_score:
            with open('historically_best_score.txt', 'w') as writer:
                writer.write(str(score))
                writer.close() 

        while game_over:
            draw_game_over_window(win)
            #run = False

    pygame.quit()
    quit()


if __name__ == '__main__':
    main()