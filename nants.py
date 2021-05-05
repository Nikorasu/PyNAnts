#!/usr/bin/env python3
from math import pi, sin, cos, atan2, radians, degrees
from random import randint
import pygame as pg
'''
NAnts
Copyright (c) 2021  Nikolaus Stromberg  nikorasu85@gmail.com
'''
FLLSCRN = True         # True for Fullscreen, or False for Window.
ANTS = 100              # Number of Ants to spawn.
WIDTH = 1200            # default 1200
HEIGHT = 800            # default 800
FPS = 48                # 48-90

class Ant(pg.sprite.Sprite):
    def __init__(self, drawSurf, nest):
        super().__init__()
        self.drawSurf = drawSurf
        self.nest = nest
        self.image = pg.Surface((12, 21))#, pg.HWSURFACE)
        self.image.set_colorkey(0)
        cBrown = (80,42,42)
        # Draw Ant
        pg.draw.aaline(self.image, cBrown, [0, 5], [11, 15])
        pg.draw.aaline(self.image, cBrown, [0, 15], [11, 5]) # legs
        pg.draw.aaline(self.image, cBrown, [0, 10], [12, 10])
        pg.draw.aaline(self.image, cBrown, [2, 0], [4, 3]) # antena l
        pg.draw.aaline(self.image, cBrown, [9, 0], [7, 3]) # antena r
        pg.draw.ellipse(self.image, cBrown, [3, 2, 6, 6]) # head
        pg.draw.ellipse(self.image, cBrown, [4, 6, 4, 9]) # body
        pg.draw.ellipse(self.image, cBrown, [3, 13, 6, 8]) # rear
        # save drawing for later
        self.orig_img = pg.transform.rotate(self.image.copy(), -90)
        self.rect = self.image.get_rect(center=self.nest)
        self.ang = randint(0, 360)
        self.desireDir = pg.Vector2(cos(radians(self.ang)),sin(radians(self.ang)))
        self.pos = pg.Vector2(self.rect.center)
        self.vel = pg.Vector2(0,0)
        self.last_phero = nest
        self.mode = 0

    def update(self, dt):  # behavior
        curW, curH = self.drawSurf.get_size()
        mid_result = left_result = right_result = [0,0,0]
        randAng = randint(0,360)
        accel = pg.Vector2(0,0)
        wandrStr = .14
        maxSpeed = 11  # more than 11 may stretch pheros too much
        steerStr = 3  # 2-4

        if self.mode == 0 and self.pos.distance_to(self.nest) > 42:
            self.mode = 1

        #mid_sensr = vec2round(self.pos + pg.Vector2(20, 0).rotate(self.ang))#.normalize() # directional vec forward
        mid_sensL = Vec2.vint(self.pos + pg.Vector2(21, -3).rotate(self.ang))
        mid_sensR = Vec2.vint(self.pos + pg.Vector2(21, 3).rotate(self.ang))
        left_sensr1 = Vec2.vint(self.pos + pg.Vector2(18, -14).rotate(self.ang))
        left_sensr2 = Vec2.vint(self.pos + pg.Vector2(16, -21).rotate(self.ang))
        right_sensr1 = Vec2.vint(self.pos + pg.Vector2(18, 14).rotate(self.ang))
        right_sensr2 = Vec2.vint(self.pos + pg.Vector2(16, 21).rotate(self.ang))
        # either mid sensor needs to be a bit in front, or side sensors need to be more back..

        #pg.draw.circle(self.drawSurf, (200,0,200), mid_sensL, 1)
        #pg.draw.circle(self.drawSurf, (200,0,200), mid_sensR, 1)
        #pg.draw.circle(self.drawSurf, (200,0,200), left_sensr1, 1)
        #pg.draw.circle(self.drawSurf, (200,0,200), left_sensr2, 1)
        #pg.draw.circle(self.drawSurf, (200,0,200), right_sensr1, 1)
        #pg.draw.circle(self.drawSurf, (200,0,200), right_sensr2, 1)

        if self.drawSurf.get_rect().collidepoint(mid_sensL) and self.drawSurf.get_rect().collidepoint(mid_sensR):
            ms_rL = self.drawSurf.get_at(mid_sensL)[:3]
            ms_rR = self.drawSurf.get_at(mid_sensR)[:3]
            mid_result = (max(ms_rL[0], ms_rR[0]), max(ms_rL[1], ms_rR[1]), max(ms_rL[2], ms_rR[2]))
        if self.drawSurf.get_rect().collidepoint(left_sensr1) and self.drawSurf.get_rect().collidepoint(left_sensr2):
            ls_r1 = self.drawSurf.get_at(left_sensr1)[:3]
            ls_r2 = self.drawSurf.get_at(left_sensr2)[:3]
            left_result = (max(ls_r1[0], ls_r2[0]), max(ls_r1[1], ls_r2[1]), max(ls_r1[2], ls_r2[2]))
        if self.drawSurf.get_rect().collidepoint(right_sensr1) and self.drawSurf.get_rect().collidepoint(right_sensr2):
            rs_r1 = self.drawSurf.get_at(right_sensr1)[:3]
            rs_r2 = self.drawSurf.get_at(right_sensr2)[:3]
            right_result = (max(rs_r1[0], rs_r2[0]), max(rs_r1[1], rs_r2[1]), max(rs_r1[2], rs_r2[2]))

        if self.pos.distance_to(self.last_phero) > 22 and self.mode != 3: # 20-25 seems best, too high they get distracted
            pheromones.add(Trail(self.pos, self.mode))  # + pg.Vector2(-5, 0).rotate(self.ang) # self.groups()[0]
            self.last_phero = pg.Vector2(self.rect.center)

        if self.mode == 1:
            if mid_result == (2,150,2): # if food
                self.desireDir += pg.Vector2(-1,0).rotate(self.ang).normalize()
                self.mode = 2
            elif mid_result[1] > max(left_result[1], right_result[1]) and (mid_result[0],mid_result[2]) == (0,0):
                self.desireDir += pg.Vector2(1,0).rotate(self.ang).normalize()
                wandrStr = 0
            elif left_result[1] > right_result[1] and (left_result[0],left_result[2]) == (0,0):
                self.desireDir += pg.Vector2(1,-2).rotate(self.ang).normalize() #left (0,-1)
                wandrStr = 0
            elif right_result[1] > left_result[1] and (right_result[0],right_result[2]) == (0,0):
                self.desireDir += pg.Vector2(1,2).rotate(self.ang).normalize() #right (0, 1)
                wandrStr = 0

        elif self.mode == 2:
            if self.pos.distance_to(self.nest) < 32:
                self.desireDir += pg.Vector2(-1,0).rotate(self.ang).normalize()
                self.mode = 1
            elif mid_result[2] > max(left_result[2], right_result[2]) and mid_result[:2] == (0,0):
                self.desireDir += pg.Vector2(1,0).rotate(self.ang).normalize()
                wandrStr = 0
            elif left_result[2] > right_result[2] and left_result[:2] == (0,0):
                self.desireDir += pg.Vector2(1,-2).rotate(self.ang).normalize() #left (0,-1)
                wandrStr = 0
            elif right_result[2] > left_result[2] and right_result[:2] == (0,0):
                self.desireDir += pg.Vector2(1,2).rotate(self.ang).normalize() #right (0, 1)
                wandrStr = 0
            else: # needs work, can't avoid walls.. maybe needs more wandrStr
                self.desireDir += pg.Vector2(self.nest - self.pos).normalize() * .1
                wandrStr = .1   #pg.Vector2(self.desireDir + (1,0)).rotate(pg.math.Vector2.as_polar(self.nest - self.pos)[1])
        elif self.mode == 3:
            if mid_result == (2,150,2): # if food
                self.desireDir += pg.Vector2(-1,0).rotate(self.ang).normalize()
                self.mode = 2
            elif mid_result[1] > max(left_result[1], right_result[1]) and (mid_result[0],mid_result[2]) == (0,0):
                self.desireDir += pg.Vector2(1,0).rotate(self.ang).normalize()
                wandrStr = 0
            elif left_result[1] > right_result[1] and (left_result[0],left_result[2]) == (0,0):
                self.desireDir += pg.Vector2(1,-2).rotate(self.ang).normalize() #left (0,-1)
                wandrStr = 0
            elif right_result[1] > left_result[1] and (right_result[0],right_result[2]) == (0,0):
                self.desireDir += pg.Vector2(1,2).rotate(self.ang).normalize() #right (0, 1)
                wandrStr = 0
            if self.pos.distance_to(self.nest) < 32:
                self.desireDir += pg.Vector2(-1,0).rotate(self.ang).normalize()
                self.mode = 1

        wallColor = (50,50,50)  # avoid walls of this color
        if left_result == wallColor:
            self.desireDir += pg.Vector2(0,1).rotate(self.ang).normalize()
            wandrStr = .1
            steerStr = 4
            if self.mode == 1 : self.mode = 3
        elif right_result == wallColor:
            self.desireDir += pg.Vector2(0,-1).rotate(self.ang).normalize()
            wandrStr = .1
            steerStr = 4
            if self.mode == 1 : self.mode = 3
        elif mid_result == wallColor:
            self.desireDir += pg.Vector2(-1,0).rotate(self.ang).normalize()
            wandrStr = .1
            steerStr = 4
            if self.mode == 1 : self.mode = 3

        # Avoid edges
        margin = 42
        if min(self.pos.x, self.pos.y, curW - self.pos.x, curH - self.pos.y) < margin:
            if self.pos.x < margin : self.desireDir = pg.Vector2(self.desireDir + (1,0)).normalize()
            elif self.pos.x > curW - margin : self.desireDir = pg.Vector2(self.desireDir + (-1,0)).normalize()
            if self.pos.y < margin : self.desireDir = pg.Vector2(self.desireDir + (0,1)).normalize()
            elif self.pos.y > curH - margin : self.desireDir = pg.Vector2(self.desireDir + (0,-1)).normalize()
            if self.mode == 1 : self.mode = 3

        randDir = pg.Vector2(cos(radians(randAng)),sin(radians(randAng)))
        self.desireDir = pg.Vector2(self.desireDir + randDir * wandrStr).normalize()
        dzVel = self.desireDir * maxSpeed
        dzStrFrc = (dzVel - self.vel) * steerStr
        accel = dzStrFrc if pg.Vector2(dzStrFrc).magnitude() <= steerStr else pg.Vector2(dzStrFrc.normalize() * steerStr)
        velo = self.vel + accel * dt
        self.vel = velo if pg.Vector2(velo).magnitude() <= maxSpeed else pg.Vector2(velo.normalize() * maxSpeed)

        self.pos += self.vel * dt
        self.ang = degrees(atan2(self.vel[1],self.vel[0]))

        # adjusts angle of img to match heading
        self.image = pg.transform.rotate(self.orig_img, -self.ang)
        self.rect = self.image.get_rect(center=self.rect.center)  # recentering fix
        # actually update position
        self.rect.center = self.pos

class Vec2():
	def __init__(self, x=0, y=0):
		self.x = x
		self.y = y
	def vint(self):
		return (int(self.x), int(self.y))

class Trail(pg.sprite.Sprite):
    def __init__(self, pos, phero_type):
        super().__init__()
        self.type = phero_type
        self.image = pg.Surface((8, 8))
        self.image.fill(0)
        self.image.set_colorkey(0)
        self.rect = self.image.get_rect(center=pos)
        self.str = 500
        # maybe if ontop of same color, add color to self, using surface.get_at()
    def update(self, dt):
        self.str -= ((dt/10)*FPS) * (60/FPS)
        if self.str < 0:
            return self.kill()
        evap = self.str/500
        self.image.fill(0)
        if self.type == 1 : pg.draw.circle(self.image, [0, 0, 90*evap+10], [4, 4], 4)
        if self.type == 2 : pg.draw.circle(self.image, [0, 90*evap+10, 0], [4, 4], 4)

class Food(pg.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.pos = pos
        self.image = pg.Surface((16, 16))
        self.image.fill(0)
        self.image.set_colorkey(0)
        pg.draw.circle(self.image, [2,150,2], [8, 8], 4)
        self.rect = self.image.get_rect(center=pos)
    def pickup(self):
        self.kill()

pheromones = pg.sprite.Group()

def main():
    pg.init()  # prepare window
    pg.display.set_caption("NAnts")
    try: pg.display.set_icon(pg.img.load("nants.png"))
    except: print("FYI: nants.png icon not found, skipping..")
    # setup fullscreen or window mode
    if FLLSCRN:  #screen = pg.display.set_mode((0,0), pg.FULLSCREEN)
        currentRez = (pg.display.Info().current_w, pg.display.Info().current_h)
        screen = pg.display.set_mode(currentRez, pg.SCALED) # pg.FULLSCREEN | #pg.display.toggle_fullscreen()
        #pg.mouse.set_visible(False)
    else: screen = pg.display.set_mode((WIDTH, HEIGHT), pg.RESIZABLE)# | pg.DOUBLEBUF)

    cur_w, cur_h = screen.get_size()
    nest = (cur_w/3, cur_h/2)

    #background = pg.img.load("background.png").convert_alpha()

    workers = pg.sprite.Group()

    for n in range(ANTS):
        workers.add(Ant(screen, nest))

    foodList = []
    foods = pg.sprite.Group()
    clock = pg.time.Clock()
    fpsChecker = 0
    # main loop
    while True:
        for e in pg.event.get():
            if e.type == pg.QUIT or e.type == pg.KEYDOWN and e.key == pg.K_ESCAPE:
                return

            elif e.type == pg.MOUSEBUTTONDOWN:
                if e.button == 1:
                    foodBits = 100
                    fRadius = 32
                    mousepos = pg.mouse.get_pos()
                    for i in range(0, foodBits):
                        dist = pow(i / (foodBits - 1.0), 0.5) * fRadius # (i / (foodBits - 1.0)**.5 #sqrt(i / (foodBits - 1.0))
                        angle = 2 * pi * 0.618033 * i
                        #angle = 3 * 2 * pi * (i / foodBits) ** 0.5
                        #dist = 100 * (i / foodBits) ** 0.5
                        fx = mousepos[0] + dist * cos(angle)
                        fy = mousepos[1] + dist * sin(angle)
                        foods.add(Food((fx,fy)))
                    foodList.extend(foods.sprites())
                if e.button == 3:
                    mousepos = pg.mouse.get_pos()
                    for fbit in foodList:
                        if pg.Vector2(fbit.rect.center).distance_to(mousepos) < fRadius:
                            fbit.pickup()
                    foodList = foods.sprites()

        dt = clock.tick(FPS) / 100
        #screen.fill(0) # enable this to show sensor debug spots

        pheromones.update(dt)
        workers.update(dt)

        screen.fill(0) # fill MUST be after sensors update, so previous draw is visible to them

        pheromones.draw(screen)
        foods.draw(screen)

        pg.draw.circle(screen, [30,10,10], (nest[0],nest[1]+6), 6, 3)
        pg.draw.circle(screen, [40,20,20], (nest[0],nest[1]+4), 9, 4)
        pg.draw.circle(screen, [50,30,30], (nest[0],nest[1]+2), 12, 4)
        pg.draw.circle(screen, [60,40,40], nest, 16, 5)

        pg.draw.rect(screen, (50,50,50), [1000, 300, 42, 400])

        workers.draw(screen)
        pg.display.update()

        fpsChecker+=1  #fpsChecker = 0  # must go before main loop
        if fpsChecker>=FPS:  # quick debug to see fps in terminal
            print(round(clock.get_fps(),2))
            #print((dt/10)*FPS)
            fpsChecker=0

if __name__ == '__main__':
    main()  # by Nik
    pg.quit()
