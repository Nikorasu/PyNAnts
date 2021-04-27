#!/usr/bin/env python3
from math import sin, cos, atan2, radians, degrees
from random import randint
import pygame as pg
'''
NAnts
Copyright (c) 2021  Nikolaus Stromberg  nikorasu85@gmail.com
'''
FLLSCRN = False         # True for Fullscreen, or False for Window.
ANTS = 20              # Number of Ants to spawn.
WIDTH = 1200            # default 1200
HEIGHT = 800            # default 800
FPS = 48                # 48-90

class Ant(pg.sprite.Sprite):
    def __init__(self, drawSurf, nest):
        super().__init__()
        self.drawSurf = drawSurf
        self.nest = nest
        #self.image = pg.img.load("ant.png").convert_alpha()
        self.image = pg.Surface((12, 21))#, pg.HWSURFACE | pg.SRCALPHA)
        self.image.set_colorkey(0)
        cBrown = (80,42,42)
        pg.draw.aaline(self.image, cBrown, [0, 5], [11, 15])
        pg.draw.aaline(self.image, cBrown, [0, 15], [11, 5]) # legs
        pg.draw.aaline(self.image, cBrown, [0, 10], [12, 10])
        pg.draw.aaline(self.image, cBrown, [2, 0], [4, 3]) #3 antena l
        pg.draw.aaline(self.image, cBrown, [9, 0], [7, 3]) #8 antena r
        pg.draw.ellipse(self.image, cBrown, (3, 2, 6, 6)) # head
        pg.draw.ellipse(self.image, cBrown, (4, 6, 4, 9)) # body
        pg.draw.ellipse(self.image, cBrown, (3, 13, 6, 8)) # rear

        self.orig_img = pg.transform.rotate(self.image.copy(), -90)
        #dS_w, dS_h = self.drawSurf.get_size()
        #self.home = (dS_w/2, dS_h/2)
        self.rect = self.image.get_rect(center=self.nest)
        self.ang = randint(0, 360)
        self.dzDir = pg.Vector2(cos(radians(self.ang)),sin(radians(self.ang)))
        self.pos = pg.Vector2(self.rect.center)
        self.vel = pg.Vector2(0,0)
        self.last_phero = nest

    def update(self, dt):  # behavior
        selfCenter = pg.Vector2(self.rect.center)
        curW, curH = self.drawSurf.get_size()
        accel = pg.Vector2(0,0)
        maxSpeed = 10
        steerStr = 2
        wandrStr = 0.16


        #fMid_sensor = self.pos + pg.Vector2(20, 0).rotate(self.ang)#.normalize()  # directional vec forward
        #fMid_sensor = (round(fMid_sensor[0]),round(fMid_sensor[1]))
        left_sensr1 = vec2round(self.pos + pg.Vector2(20, -12).rotate(self.ang))
        left_sensr2 = vec2round(self.pos + pg.Vector2(20, -16).rotate(self.ang))
        #fLeft_sensor = (round(fLeft_sensor[0]),round(fLeft_sensor[1]))
        right_sensr1 = vec2round(self.pos + pg.Vector2(20, 12).rotate(self.ang))
        right_sensr2 = vec2round(self.pos + pg.Vector2(20, 16).rotate(self.ang))
        #fRight_sensor = (round(fRight_sensor[0]),round(fRight_sensor[1]))
        #pg.draw.circle(self.drawSurf, (200,0,0), fMid_sensor, 2)
        #pg.draw.circle(self.drawSurf, (200,0,0), left_sensr, 2)
        #pg.draw.circle(self.drawSurf, (200,0,0), right_sensr, 2)

        #if fM_sensor[0] in range(0, curW) and fM_sensor[1] in range(0, curH)
        #if self.drawSurf.get_rect().collidepoint(fMid_sensor) and self.drawSurf.get_at(fMid_sensor) == (0,0,100,255): print("Mid")

        ls_chk1 = self.drawSurf.get_rect().collidepoint(left_sensr1) and self.drawSurf.get_at(left_sensr1) == (0,0,100,255)
        ls_chk2 = self.drawSurf.get_rect().collidepoint(left_sensr2) and self.drawSurf.get_at(left_sensr2) == (0,0,100,255)
        if ls_chk1 or ls_chk2:
            print("Left")

        rs_chk1 = self.drawSurf.get_rect().collidepoint(right_sensr1) and self.drawSurf.get_at(right_sensr1) == (0,0,100,255)
        rs_chk2 = self.drawSurf.get_rect().collidepoint(right_sensr2) and self.drawSurf.get_at(right_sensr2) == (0,0,100,255)
        if rs_chk1 or rs_chk2:
            print("Right")
        # if pixel color value [2] > blueThreshold
        randAng = randint(0,360)
        randDir = pg.Vector2(cos(radians(randAng)),sin(radians(randAng)))
        self.dzDir = pg.Vector2(self.dzDir + randDir * wandrStr).normalize() # this line disable to steer
        dzVel = self.dzDir * maxSpeed
        dzStrFrc = (dzVel - self.vel) * steerStr
        accel = dzStrFrc if pg.Vector2(dzStrFrc).magnitude() <= steerStr else pg.Vector2(dzStrFrc.normalize() * steerStr)
        velo = self.vel + accel * dt
        self.vel = velo if pg.Vector2(velo).magnitude() <= maxSpeed else pg.Vector2(velo.normalize() * maxSpeed)

        self.pos += self.vel * dt
        self.ang = degrees(atan2(self.vel[1],self.vel[0]))


        #if pg.Vector2(self.pos - self.last_phero).length()
        if selfCenter.distance_to(self.last_phero) > 32:
            self.groups()[0].add(Trail(selfCenter, 1))
            self.last_phero = pg.Vector2(self.rect.center)

        # adjusts angle of boid img to match heading
        self.image = pg.transform.rotate(self.orig_img, -self.ang)
        self.rect = self.image.get_rect(center=self.rect.center)  # recentering fix

        if not self.drawSurf.get_rect().contains(self.rect):
            if self.rect.bottom < 0 : self.pos.y = curH
            elif self.rect.top > curH : self.pos.y = 0
            if self.rect.right < 0 : self.pos.x = curW
            elif self.rect.left > curW : self.pos.x = 0
        # actually update position of boid
        self.rect.center = self.pos

class Trail(pg.sprite.Sprite):
    def __init__(self, pos, phero_type):
        super().__init__()
        self.image = pg.Surface((16, 16))
        self.image.fill(0)
        self.image.set_colorkey(0)
        #if phero_type = 1
        pg.draw.circle(self.image, (0,0,100), (8, 8), 7)
        self.img_copy = self.image.copy()
        self.rect = self.image.get_rect(center=pos)
        self.pos = pg.Vector2(self.rect.center)
        self.str = 700

    def update(self, dt):
        self.str -= 1
        self.image.fill(0)
        pg.draw.circle(self.image, (0,0,100), (8, 8), 5*(self.str/1000)+2)
        if self.str == 0:
            return self.kill()

def vec2round(vec2):
    return (round(vec2[0]),round(vec2[1]))

def main():
    pg.init()  # prepare window
    pg.display.set_caption("NAnts")
    try: pg.display.set_icon(pg.img.load("nants.png"))
    except: print("FYI: nants.png icon not found, skipping..")
    # setup fullscreen or window mode
    if FLLSCRN:  #screen = pg.display.set_mode((0,0), pg.FULLSCREEN)
        currentRez = (pg.display.Info().current_w, pg.display.Info().current_h)
        screen = pg.display.set_mode(currentRez, pg.SCALED) # pg.FULLSCREEN | #pg.display.toggle_fullscreen()
        pg.mouse.set_visible(False)
    else: screen = pg.display.set_mode((WIDTH, HEIGHT), pg.RESIZABLE)# | pg.DOUBLEBUF)

    cur_w, cur_h = screen.get_size()
    nest = (cur_w/2, cur_h/2)

    workers = pg.sprite.Group()
    for n in range(ANTS):
        workers.add(Ant(screen, nest))
    #allBoids = nBoids.sprites()

    clock = pg.time.Clock()
    fpsChecker = 0
    # main loop
    while True:
        for e in pg.event.get():
            if e.type == pg.QUIT or e.type == pg.KEYDOWN and e.key == pg.K_ESCAPE:
                return

        dt = clock.tick(FPS) / 100
        #screen.fill(0) # before update prevents get_at

        workers.update(dt)
        #pheromones.update()

        screen.fill(0)
        pg.draw.circle(screen, (64,64,64), nest, 16, 5)
        workers.draw(screen)
        #pheromones.draw()

        pg.display.update()

        fpsChecker+=1  #fpsChecker = 0  # must go before main loop
        if fpsChecker>=FPS:  # quick debug to see fps in terminal
            print(round(clock.get_fps(),2))
            fpsChecker=0

if __name__ == '__main__':
    main()  # by Nik
    pg.quit()
