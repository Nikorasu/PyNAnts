#!/usr/bin/env python3
from math import pi, sin, cos, atan2, radians, degrees
from random import randint
import pygame as pg
import numpy as np
'''
NAnts
Copyright (c) 2021  Nikolaus Stromberg  nikorasu85@gmail.com
'''
FLLSCRN = True          # True for Fullscreen, or False for Window.
ANTS = 200              # Number of Ants to spawn.
WIDTH = 1200            # default 1200
HEIGHT = 800            # default 800
FPS = 60                # 48-90
PRATIO = 5              # Pixel Size for Pheromone grid

class Ant(pg.sprite.Sprite):
    def __init__(self, drawSurf, nest, pheroLayer):
        super().__init__()
        self.drawSurf = drawSurf
        self.phero = pheroLayer
        self.nest = nest
        self.image = pg.Surface((12, 21)).convert()
        self.image.set_colorkey(0)
        cBrown = (100,42,42)
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
        self.last_sdp = (nest[0]/10/2,nest[1]/10/2)
        self.mode = 0

    def update(self, dt):  # behavior
        curW, curH = self.drawSurf.get_size()
        mid_result = left_result = right_result = [0,0,0]
        mid_A_result = left_A_result = right_A_result = [0,0,0]
        randAng = randint(0,360)
        accel = pg.Vector2(0,0)
        wandrStr = .13
        maxSpeed = 12
        steerStr = 3  # 3 or 4

        if self.mode == 0 and self.pos.distance_to(self.nest) > 42:
            self.mode = 1

        psSize = (int(curW/PRATIO), int(curH/PRATIO))
        scaledown_pos = (int((self.pos.x/curW)*psSize[0]), int((self.pos.y/curH)*psSize[1]))
        color_rgb = (0,0,200)
        # check if current pos diff from last pos
        if scaledown_pos != self.last_sdp and scaledown_pos[0] in range(0,psSize[0]) and scaledown_pos[1] in range(0,psSize[1]):
            #self.phero.input2grid(scaledown_pos, color_rgb)
            self.phero.img_array[scaledown_pos] += color_rgb
            self.last_sdp = scaledown_pos

        #mid_sensr = vec2round(self.pos + pg.Vector2(20, 0).rotate(self.ang))#.normalize() # directional vec forward
        mid_sensL = Vec2.vint(self.pos + pg.Vector2(21, -3).rotate(self.ang))
        mid_sensR = Vec2.vint(self.pos + pg.Vector2(21, 3).rotate(self.ang))
        left_sens1 = Vec2.vint(self.pos + pg.Vector2(18, -14).rotate(self.ang))
        left_sens2 = Vec2.vint(self.pos + pg.Vector2(16, -21).rotate(self.ang))
        right_sens1 = Vec2.vint(self.pos + pg.Vector2(18, 14).rotate(self.ang))
        right_sens2 = Vec2.vint(self.pos + pg.Vector2(16, 21).rotate(self.ang))
        # either mid sensor needs to be a bit in front, or side sensors need to be more back..

        if self.drawSurf.get_rect().collidepoint(mid_sensL) and self.drawSurf.get_rect().collidepoint(mid_sensR):
            #mid_L_sdpos = (int((mid_sensL[0]/curW)*psSize[0]), int((mid_sensL[1]/curH)*psSize[1]))
            #mid_L_result = self.phero.img_array[mid_L_sdpos]
            #mid_R_sdpos = (int((mid_sensR[0]/curW)*psSize[0]), int((mid_sensR[1]/curH)*psSize[1]))
            #mid_R_result = self.phero.img_array[mid_R_sdpos]
            #mid_A_result = (max(mid_L_result[0], mid_R_result[0]), max(mid_L_result[1], mid_R_result[1]), max(mid_L_result[2], mid_R_result[2]))
            mid_A_result = self.sensArray(mid_sensL, mid_sensR)
            #mid_gaL = self.drawSurf.get_at(mid_sensL)[:3]
            #mid_gaR = self.drawSurf.get_at(mid_sensR)[:3]
            #mid_result = (max(mid_gaL[0], mid_gaR[0]), max(mid_gaL[1], mid_gaR[1]), max(mid_gaL[2], mid_gaR[2]))
            mid_result = self.sensGA(mid_sensL, mid_sensR)
        if self.drawSurf.get_rect().collidepoint(left_sens1) and self.drawSurf.get_rect().collidepoint(left_sens2):
            left_A_result = self.sensArray(left_sens1, left_sens2)
            #left_ga1 = self.drawSurf.get_at(left_sens1)[:3]
            #left_ga2 = self.drawSurf.get_at(left_sens2)[:3]
            #left_result = (max(left_ga1[0], left_ga2[0]), max(left_ga1[1], left_ga2[1]), max(left_ga1[2], left_ga2[2]))
            left_result = self.sensGA(left_sens1, left_sens2)
        if self.drawSurf.get_rect().collidepoint(right_sens1) and self.drawSurf.get_rect().collidepoint(right_sens2):
            right_A_result = self.sensArray(right_sens1, right_sens2)
            #right_ga1 = self.drawSurf.get_at(right_sens1)[:3]
            #right_ga2 = self.drawSurf.get_at(right_sens2)[:3]
            #right_result = (max(right_ga1[0], right_ga2[0]), max(right_ga1[1], right_ga2[1]), max(right_ga1[2], right_ga2[2]))
            right_result = self.sensGA(right_sens1, right_sens2)
        # INSTEAD OF get_at, try checking Array color at sensor spot equivalent scaledown locations


        if mid_A_result[2] > max(left_A_result[2], right_A_result[2]) and mid_A_result[:2] == (0,0):
            self.desireDir += pg.Vector2(1,0).rotate(self.ang).normalize() # might not need +=
            wandrStr = .01
        elif left_A_result[2] > right_A_result[2] and left_A_result[:2] == (0,0):
            self.desireDir += pg.Vector2(1,-2).rotate(self.ang).normalize() #left (0,-1)
            wandrStr = .01
        elif right_A_result[2] > left_A_result[2] and right_A_result[:2] == (0,0):
            self.desireDir += pg.Vector2(1,2).rotate(self.ang).normalize() #right (0, 1)
            wandrStr = .01

        '''
        if self.mode == 1:
            if mid_result == (2,150,2): # if food
                self.desireDir += pg.Vector2(-1,0).rotate(self.ang).normalize()
                self.mode = 2
            elif mid_result[1] > max(left_result[1], right_result[1]) and (mid_result[0],mid_result[2]) == (0,0):
                self.desireDir += pg.Vector2(1,0).rotate(self.ang).normalize()
                wandrStr = .1
            elif left_result[1] > right_result[1] and (left_result[0],left_result[2]) == (0,0):
                self.desireDir += pg.Vector2(1,-2).rotate(self.ang).normalize() #left (0,-1)
                wandrStr = .1
            elif right_result[1] > left_result[1] and (right_result[0],right_result[2]) == (0,0):
                self.desireDir += pg.Vector2(1,2).rotate(self.ang).normalize() #right (0, 1)
                wandrStr = .1
        elif self.mode == 2:
            if self.pos.distance_to(self.nest) < 32:
                self.desireDir += pg.Vector2(-1,0).rotate(self.ang).normalize()
                self.mode = 1
            elif mid_result[2] > max(left_result[2], right_result[2]) and mid_result[:2] == (0,0):
                self.desireDir += pg.Vector2(1,0).rotate(self.ang).normalize()
                wandrStr = .1
            elif left_result[2] > right_result[2] and left_result[:2] == (0,0):
                self.desireDir += pg.Vector2(1,-2).rotate(self.ang).normalize() #left (0,-1)
                wandrStr = .1
            elif right_result[2] > left_result[2] and right_result[:2] == (0,0):
                self.desireDir += pg.Vector2(1,2).rotate(self.ang).normalize() #right (0, 1)
                wandrStr = .1
            else:
                self.desireDir += pg.Vector2(self.nest - self.pos).normalize() * .1
                wandrStr = .1   #pg.Vector2(self.desireDir + (1,0)).rotate(pg.math.Vector2.as_polar(self.nest - self.pos)[1])
        elif self.mode == 3:
            if mid_result == (2,150,2): # if food
                self.desireDir += pg.Vector2(-1,0).rotate(self.ang).normalize()
                self.mode = 2
            elif mid_result[1] > max(left_result[1], right_result[1]) and (mid_result[0],mid_result[2]) == (0,0):
                self.desireDir += pg.Vector2(1,0).rotate(self.ang).normalize()
                wandrStr = .1
            elif left_result[1] > right_result[1] and (left_result[0],left_result[2]) == (0,0):
                self.desireDir += pg.Vector2(1,-2).rotate(self.ang).normalize() #left (0,-1)
                wandrStr = .1
            elif right_result[1] > left_result[1] and (right_result[0],right_result[2]) == (0,0):
                self.desireDir += pg.Vector2(1,2).rotate(self.ang).normalize() #right (0, 1)
                wandrStr = .1
            if self.pos.distance_to(self.nest) < 32:
                self.desireDir += pg.Vector2(-1,0).rotate(self.ang).normalize()
                self.mode = 1
        '''

        wallColor = (50,50,50)  # avoid walls of this color
        if left_result == wallColor:
            self.desireDir += pg.Vector2(0,1).rotate(self.ang) #.normalize()
            wandrStr = .1
            steerStr = 4
            if self.mode == 1 : self.mode = 3
        elif right_result == wallColor:
            self.desireDir += pg.Vector2(0,-1).rotate(self.ang) #.normalize()
            wandrStr = .1
            steerStr = 4
            if self.mode == 1 : self.mode = 3
        elif mid_result == wallColor:
            self.desireDir += pg.Vector2(-2,0).rotate(self.ang) #.normalize()
            wandrStr = .1
            steerStr = 4
            if self.mode == 1 : self.mode = 3

        # Avoid edges
        if not self.drawSurf.get_rect().collidepoint(left_sens2) and self.drawSurf.get_rect().collidepoint(right_sens2):
            self.desireDir += pg.Vector2(0,1).rotate(self.ang) #.normalize()
            wandrStr = .01
            steerStr = 4
        elif not self.drawSurf.get_rect().collidepoint(right_sens2) and self.drawSurf.get_rect().collidepoint(left_sens2):
            self.desireDir += pg.Vector2(0,-1).rotate(self.ang) #.normalize()
            wandrStr = .01
            steerStr = 4
        elif not self.drawSurf.get_rect().collidepoint(Vec2.vint(self.pos + pg.Vector2(21, 0).rotate(self.ang))):
            self.desireDir += pg.Vector2(-1,0).rotate(self.ang) #.normalize()
            wandrStr = .01
            steerStr = 5
        #elif not self.drawSurf.get_rect().collidepoint(self.pos): #self.drawSurf.get_rect().contains(self.rect):
        #    self.desireDir = pg.Vector2((curW/2 - self.rect.centerx, curH/2 - self.rect.centery)).normalize()
        '''
        if self.rect.top < 0 or self.rect.bottom > curH:
            self.desireDir[1] = -self.desireDir[1]
            self.vel[1] = -self.vel[1]
        if self.rect.left < 0 or self.rect.right > curW:
            self.desireDir[0] = -self.desireDir[0]
            self.vel[0] = -self.vel[0]
        '''

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

    def sensArray(self, sens_pos1, sens_pos2):
        curW, curH = self.drawSurf.get_size()
        psSize = (int(curW/PRATIO), int(curH/PRATIO))
        sdpos1 = (int((sens_pos1[0]/curW)*psSize[0]), int((sens_pos1[1]/curH)*psSize[1]))
        result1 = self.phero.img_array[sdpos1]
        sdpos2 = (int((sens_pos2[0]/curW)*psSize[0]), int((sens_pos2[1]/curH)*psSize[1]))
        result2 = self.phero.img_array[sdpos2]
        return (max(result1[0], result2[0]), max(result1[1], result2[1]), max(result1[2], result2[2]))

    def sensGA(self, ga_pos1, ga_pos2):
        ga_r1 = self.drawSurf.get_at(ga_pos1)[:3]
        ga_r2 = self.drawSurf.get_at(ga_pos2)[:3]
        return (max(ga_r1[0], ga_r2[0]), max(ga_r1[1], ga_r2[1]), max(ga_r1[2], ga_r2[2]))

class PheroGrid():
    def __init__(self, bigSize):
        self.surfSize = (bigSize[0]/PRATIO, bigSize[1]/PRATIO)
        self.image = pg.Surface(self.surfSize).convert()
        self.img_array = np.array(pg.surfarray.array3d(self.image)).astype(np.float64)
    def update(self, dt):
        self.img_array[self.img_array > 0] -= .9 * (60/FPS) * ((dt/10) * FPS)
        self.img_array[self.img_array < 1] = 0  # ensure no leftover floats <1
        self.img_array[self.img_array > 255] = 255  # ensures nothing over 255
        pg.surfarray.blit_array(self.image, self.img_array)
        return self.image
#    def input2grid(self, scaled_pos, color_rgb):
#        self.img_array[scaled_pos] += color_rgb

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

class Vec2():
	def __init__(self, x=0, y=0):
		self.x = x
		self.y = y
	def vint(self):
		return (int(self.x), int(self.y))

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
    else: screen = pg.display.set_mode((WIDTH, HEIGHT)) #, pg.RESIZABLE) # | pg.DOUBLEBUF)

    cur_w, cur_h = screen.get_size()
    screenSize = (cur_w, cur_h)
    nest = (cur_w/3, cur_h/2)

    #background = pg.img.load("background.png").convert_alpha()

    workers = pg.sprite.Group()
    pheroLayer = PheroGrid(screenSize)

    for n in range(ANTS):
        workers.add(Ant(screen, nest, pheroLayer))

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
                mousepos = pg.mouse.get_pos()
                if e.button == 1: # and pg.Vector2(mousepos).distance_to(nest) > 242:
                    foodBits = 200
                    fRadius = 50
                    for i in range(0, foodBits):
                        dist = pow(i / (foodBits - 1.0), 0.5) * fRadius
                        angle = 2 * pi * 0.618033 * i
                        fx = mousepos[0] + dist * cos(angle)
                        fy = mousepos[1] + dist * sin(angle)
                        foods.add(Food((fx,fy)))
                    foodList.extend(foods.sprites())
                if e.button == 3:
                    for fbit in foodList:
                        if pg.Vector2(mousepos).distance_to(fbit.rect.center) < fRadius:
                            fbit.pickup()
                    foodList = foods.sprites()

        dt = clock.tick(FPS) / 100

        pheroImg = pheroLayer.update(dt)

        workers.update(dt)

        screen.fill(0) # fill MUST be after sensors update, so previous draw is visible to them

        rescaled_img = pg.transform.scale(pheroImg, (cur_w, cur_h))
        pg.Surface.blit(screen, rescaled_img, (0,0))

        foods.draw(screen)

        pg.draw.circle(screen, [40,10,10], (nest[0],nest[1]+6), 6, 3)
        pg.draw.circle(screen, [50,20,20], (nest[0],nest[1]+4), 9, 4)
        pg.draw.circle(screen, [60,30,30], (nest[0],nest[1]+2), 12, 4)
        pg.draw.circle(screen, [70,40,40], nest, 16, 5)

        pg.draw.rect(screen, (50,50,50), [900, 300, 50, 400]) #wall

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
