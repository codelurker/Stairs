#! /usr/bin/python
# -*- coding: utf-8 -*-

import sys
import random
import pygame
import pygame.mixer
from pygame.locals import *

class Kamen(pygame.sprite.Sprite):
    speed = 1
    status = 0 #0-down,1-left,2-right
    down = 0

    def __init__(self):
        super(Kamen, self).__init__()
        image = pygame.image.load('kamen.png').convert()
        image.set_colorkey(image.get_at((0, 0)), RLEACCEL)
        self.image = image
        self.rect = image.get_rect()
        self.cX = 0
        self.cY = 0

    def update(self, args):
        if args[1]:
            self.init()
            return

        if self.cY > 640:
            self.cY = 0
            self.cX = -60
            self.status = 1

        if not self.status:
            if ( (self.down + self.speed) > 60 ) and (self.cY < 400):
                self.status = random.randint(1, 2)
                self.cY += (60 - self.down)
            else:
                self.down += self.speed
                self.cY += self.speed

        if self.status:
            level = (self.cY + 60) / 60
            if level < 8:
                level = game_location.upstairs[level - 1]
                down = 0
                for i in xrange(0, 3):
                    if abs((self.cX + 30) - (level[i] + 16)) < 20:
                        down = 1
                if down:
                    self.status = 0
                    self.down = 0

        if self.cX > 700:
            self.cX = -60
        if self.cX < -60:
            self.cX = 700
        if self.status == 1:
            self.cX -= self.speed
        if self.status == 2:
            self.cX += self.speed

        self.rect.x = self.cX
        self.rect.y = self.cY

    def init(self):
        self.cY = 0
        self.cX = random.randint(0, 580)
        self.speed = general.level + 1
        if self.speed > 50:
            self.speed = 50
        self.status = random.randint(1, 2)


class Kolobok(pygame.sprite.Sprite):
    def __init__(self):
        super(Kolobok, self).__init__()
        image = pygame.image.load('kolobok.png').convert()
        image.set_colorkey(image.get_at((0, 0)), RLEACCEL)
        self.image = image
        self.rect = image.get_rect()
        self.cX = 0
        self.cY = 450

    def win(self):
        if (self.cX > 590) and (self.cY < 110):
            return 1
        return 0

    def draw(self, window):
        self.rect.x = self.cX
        self.rect.y = self.cY
        window.blit(self.image, (self.cX, self.cY))

    def notYup(self):
        level = (self.cY + 29) / 60
        level = game_location.upstairs[level - 1]
        ret = 1
        for i in xrange(0, 3):
            if abs((self.cX + 15) - (level[i] + 16)) < 20:
                ret = 0
        if ret:
            return 1
        return 0

    def notYdown(self):
        if self.cY > 449:
            return 0
        level = (self.cY + 30) / 60
        level = game_location.upstairs[level - 1]
        ret = 1
        for i in xrange(0, 3):
            if abs((self.cX + 15) - (level[i] + 16)) < 20:
                ret = 0
        if ret:
            return 1
        return 0

    def up(self):
        if self.notYup():
            return
        self.cY -= 5
        if self.cY < 90:
            self.cY = 90

    def down(self):
        if self.notYdown():
            return
        self.cY += 5
        if self.cY > 450:
            self.cY = 450

    def left(self):
        if self.notX():
            return
        self.cX -= 5
        if self.cX < -30:
            self.cX = 640 + 30

    def right(self):
        if self.notX():
            return
        self.cX += 5
        if self.cX > 670:
            self.cX = -30

    def notX(self):
        return 1 if (self.cY + 30) % 60 else 0


class Location(object):
    def __init__(self):
        self.window = pygame.display.get_surface()

    def event(self, event):
        pass

    def draw(self):
        pass


class Exit_location(Location):
    def __init__(self):
        Location.__init__(self)

    def event(self, event):
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                sys.exit()

    def draw(self):
        self.background = pygame.Surface(self.window.get_size())
        self.background.fill((0, 200, 200))
        font = pygame.font.Font(None, 36)

        score = font.render("your level: " + str(general.level), 1, (20, 20, 20))
        scorepos = score.get_rect(center=(320, 150))
        self.background.blit(score, scorepos)

        text = font.render("press Esc key to exit", 1, (10, 10, 10))
        textpos = text.get_rect(center=(320, 450))
        self.background.blit(text, textpos)
        self.window.blit(self.background, (0, 0))


class Game_location(Location):
    def __init__(self):
        Location.__init__(self)
        self.kolobok = Kolobok()
        self.kamens = pygame.sprite.Group()
        for i in xrange(0, 3):
            self.kamens.add(Kamen())
        self.generate_background()

    def draw(self):
        keys = pygame.key.get_pressed()
        if keys[K_LEFT]:
            self.kolobok.left()
        if keys[K_RIGHT]:
            self.kolobok.right()
        if keys[K_UP]:
            self.kolobok.up()
        if keys[K_DOWN]:
            self.kolobok.down()

        self.window.blit(self.background, (0, 0))
        self.kolobok.draw(self.window)
        if self.kolobok.win():
            general.level += 1
            self.generate_background()

        self.kamens.update([self.window, 0])
        self.kamens.draw(self.window)

        for _ in pygame.sprite.spritecollide(self.kolobok, self.kamens, 0):
            general.location = exit_location

    def generate_background(self):
        self.kamens.update([self.window, 1])
        self.background = pygame.Surface(self.window.get_size())
        self.background.fill((200, 200, 200))
        for i in xrange(60, 480, 60):
            pygame.draw.line(self.background, (0, 0, 0), (0, i), (640, i), 2)
        door = pygame.image.load('door.png').convert()
        door.set_colorkey(door.get_at((0, 0)), RLEACCEL)
        self.background.blit(door, (595, 61))

        self.upstairs = []
        for i in xrange(0, 7):
            maxx = 630 if i else 530

            x1 = random.randint(0, maxx)
            x2 = random.randint(0, maxx)
            while 1:
                if abs(x2 - x1) > 100:
                    break
                x2 = random.randint(0, maxx)

            x3 = random.randint(0, maxx)
            while 1:
                x3 = random.randint(0, maxx)
                if (abs(x3 - x1) > 100) and (abs(x3 - x2) > 100):
                    break

            self.upstairs.append([x1, x2, x3])

        upstair = pygame.image.load('lestnica.png').convert()
        upstair.set_colorkey(upstair.get_at((0, 0)), RLEACCEL)

        for i in xrange(0, 7):
            for ii in self.upstairs[i]:
                self.background.blit(upstair, (ii, i * 60 + 60))

        self.kolobok.cX = 0
        self.kolobok.cY = 450


class Start_location(Location):
    def __init__(self):
        Location.__init__(self)
        self.background = pygame.image.load('first.png')

    def draw(self):
        self.window.blit(self.background, (0, 0))

    def event(self, event):
        if event.type == KEYDOWN:
            if event.key == 13:
                general.location = game_location


class General():
    level = 0
    music = 0

    def __init__(self):
        pygame.init()
        pygame.display.set_mode((640, 480))
        pygame.display.set_caption('][akep')
        pygame.mixer.music.load('s.mp3')
        pygame.mixer.music.play()
        pygame.mixer.music.pause()

    def event(self, event):
        if event.type == QUIT:
            sys.exit()
        if event.type == KEYUP:
            if event.key == K_m:
                if self.music:
                    pygame.mixer.music.pause()
                    self.music = 0
                else:
                    pygame.mixer.music.unpause()
                    self.music = 1
            elif event.key == K_ESCAPE:
                general.location = exit_location


general = General()

start_location = Start_location()
game_location = Game_location()
exit_location = Exit_location()

general.location = start_location

clock = pygame.time.Clock()
while 1:
    for event in pygame.event.get():
        general.location.event(event)
        general.event(event)
    general.location.draw()
    pygame.display.flip()
    clock.tick(30)