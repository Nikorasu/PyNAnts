#!/usr/bin/env python3
from math import sin, cos, atan2, radians, degrees
from random import randint
import pygame as pg
'''
NAnts
Copyright (c) 2021  Nikolaus Stromberg  nikorasu85@gmail.com
'''
FLLSCRN = False         # True for Fullscreen, or False for Window.
ANTS = 5              # Number of Ants to spawn.
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
        pg.draw.ellipse(self.image, cBrown, [3, 2, 6, 6]) # head
        pg.draw.ellipse(self.image, cBrown, [4, 6, 4, 9]) # body
        pg.draw.ellipse(self.image, cBrown, [3, 13, 6, 8]) # rear

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

        if selfCenter.distance_to(self.last_phero) > 32:
            self.groups()[0].add(Trail(selfCenter, 1))
            self.last_phero = pg.Vector2(self.rect.center)


        mid_sensr = vec2round(self.pos + pg.Vector2(16, 0).rotate(self.ang))#.normalize()  # directional vec forward
        #fMid_sensor = (round(fMid_sensor[0]),round(fMid_sensor[1]))
        left_sensr1 = vec2round(self.pos + pg.Vector2(20, -12).rotate(self.ang))
        left_sensr2 = vec2round(self.pos + pg.Vector2(20, -18).rotate(self.ang))

        right_sensr1 = vec2round(self.pos + pg.Vector2(20, 12).rotate(self.ang))
        right_sensr2 = vec2round(self.pos + pg.Vector2(20, 18).rotate(self.ang))

        #pg.draw.circle(self.drawSurf, (200,0,0), mid_sensr, 1)
        #pg.draw.circle(self.drawSurf, (200,0,0), left_sensr1, 1)
        #pg.draw.circle(self.drawSurf, (200,0,0), right_sensr1, 1)
        #pg.draw.circle(self.drawSurf, (200,0,0), left_sensr2, 1)
        #pg.draw.circle(self.drawSurf, (200,0,0), right_sensr2, 1)

        mids_result = self.drawSurf.get_at(mid_sensr)[:3]
        ls_result1 = self.drawSurf.get_at(left_sensr1)[:3]
        ls_result2 = self.drawSurf.get_at(left_sensr2)[:3]
        rs_result1 = self.drawSurf.get_at(right_sensr1)[:3]
        rs_result2 = self.drawSurf.get_at(right_sensr2)[:3]
        if mids_result!= (0,0,0): print(mids_result)
        #ls_chk1 = self.drawSurf.get_rect().collidepoint(left_sensr1) and self.drawSurf.get_at(left_sensr1) == (0,0,100,255)
        #ls_chk2 = self.drawSurf.get_rect().collidepoint(left_sensr2) and self.drawSurf.get_at(left_sensr2) == (0,0,100,255)
        #if ls_chk1 or ls_chk2 : print("Left")

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

        margin = 64
        if min(self.pos.x, self.pos.y, curW - self.pos.x, curH - self.pos.y) < margin:
            if self.pos.x < margin : self.dzDir = pg.Vector2(self.dzDir + (1,0)).normalize()
            elif self.pos.x > curW - margin : self.dzDir = pg.Vector2(self.dzDir + (-1,0)).normalize()
            if self.pos.y < margin : self.dzDir = pg.Vector2(self.dzDir + (0,1)).normalize()
            elif self.pos.y > curH - margin : self.dzDir = pg.Vector2(self.dzDir + (0,-1)).normalize()

        # adjusts angle of img to match heading
        self.image = pg.transform.rotate(self.orig_img, -self.ang)
        self.rect = self.image.get_rect(center=self.rect.center)  # recentering fix
        # actually update position
        self.rect.center = self.pos

class Trail(pg.sprite.Sprite):
    def __init__(self, pos, phero_type):
        super().__init__()
        self.image = pg.Surface((16, 16))#, pg.SRCALPHA)
        self.image.fill(0)
        self.image.set_colorkey(0)
        #if phero_type = 1
        pg.draw.circle(self.image, [0,0,100], [8, 8], 6)
        self.img_copy = self.image.copy()
        self.rect = self.image.get_rect(center=pos)
        self.pos = pg.Vector2(self.rect.center)
        self.str = 800

    def update(self, dt):
        self.str -= 1
        evap = self.str/800
        self.image.fill(0)
        pg.draw.circle(self.image, [0,0,80*evap+20], [8, 8], 3*evap+3)
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
    nest = (cur_w/3, cur_h/2)

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

        screen.fill(0) # where this should be
        pg.draw.circle(screen, [40,10,10], (nest[0],nest[1]+6), 6, 3)
        pg.draw.circle(screen, [50,20,20], (nest[0],nest[1]+4), 9, 4)
        pg.draw.circle(screen, [60,30,30], (nest[0],nest[1]+2), 12, 4)
        pg.draw.circle(screen, [70,40,40], nest, 16, 5)
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
