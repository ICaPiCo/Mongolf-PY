import pyxel
from math import *

class golf:

    def __init__(self, holes):
            self.bX = 20
            self.bY = 228
            self.bvX = 0
            self.bvY = 0

            self.playing = False
            self.stopped = True
            self.shots = 0
            self.power = 3
            self.rotation = 270
            self.holes = holes
            pyxel.init(256, 256, title="Golf", fps=120, display_scale=4)
            pyxel.load("assets.pyxres")
            pyxel.run(self.update, self.draw)

    def controls(self):
        if pyxel.btnp(pyxel.KEY_SPACE):
            self.stopped = False
            self.bvX = int(cos(radians(self.rotation)) * self.power)
            self.bvY = int(sin(radians(self.rotation)) * self.power)

        elif pyxel.btnp(pyxel.KEY_UP) and self.power < 10:
            self.power += 1
        elif pyxel.btnp(pyxel.KEY_DOWN) and self.power > 1:
            self.power -= 1
        elif pyxel.btn(pyxel.KEY_LEFT):
            self.rotation -= 1
        elif pyxel.btn(pyxel.KEY_RIGHT):
            self.rotation += 1
        elif pyxel.btnp(pyxel.KEY_R):
            self.bX = 20
            self.bY = 228
            self.bvX = 0
            self.bvY = 0
            self.stopped = True

    def residual(self):
        if abs(self.bvX) < 0.1 and abs(self.bvY) < 0.1:
            self.stopped = True
            self.shots += 1
            self.bvX = 0
            self.bvY = 0
            self.power = 3

    def outOfBounds(self):
        if self.bX < 0 or self.bX > 256 or self.bY < 0 or self.bY > 256:
            self.stopped = True
            self.shots += 1
            self.bX = 20
            self.bY = 228
            self.bvX = 0
            self.bvY = 0
            self.power = 3

    def stopNow(self):
        self.stopped = True
        self.shots += 1
        self.bvX = 0
        self.bvY = 0
        self.power = 3

    def wouldCollide(self, x, y):
        """Check if position (x,y) would collide with walls"""
        for px, py in self.collisionCircle(x+4, y+4):
            if pyxel.pget(px, py) == 4:  # Wall color
                return True
        return False

    def checkCollision(self):
        circleCollision = self.collisionCircle((self.bX+4),(self.bY+4))
        oldX=self.bX-self.bvX
        oldY=self.bY-self.bvY
        for i in circleCollision:
            x,y=i[0],i[1]
            if pyxel.pget(x,y) == 4:
                return True
            elif pyxel.pget(x,y) == 8:
                self.holes += 1
                self.stopped = True
                self.playing = False
                self.bX = 20
                self.bY = 228
                break
            elif pyxel.pget(x, y) == 10:
                self.stopNow()
                self.bX = oldX
                self.bY = oldY
            
            elif pyxel.pget(x, y) == 6:
                self.bvX *= 0.90
                self.bvY *= 0.90

    def textStuff(self):
        if self.holes == 0:
            pyxel.text(120, 20, "Use the arrow keys to aim", 7)
            pyxel.text(120, 30, "and the space bar to shoot.", 7)
            pyxel.text(120, 40, "Press R to reset the ball.", 7)
            pyxel.text(120, 50, "Press space to shoot.", 7)
        if self.holes == 1 or 2 or 3:
            pyxel.text(120, 10, "Nice!", 7)
        if self.holes == 4:
            pyxel.text(120, 10, "You win!", 7)
            pyxel.text(100, 20, f"With an average of {self.shots/(self.holes+1)} shots per holes", 7)

    def update(self):
        if self.stopped:
            self.controls()
        else:
            self.moveBall()
            self.residual()
        self.checkCollision()
        self.circle360()
        self.outOfBounds()
        self.inWall()

    def moveBall(self):
        self.bvX *= 0.985
        self.bvY *= 0.985
        
        new_x = self.bX + self.bvX
        new_y = self.bY + self.bvY
        
        if not self.wouldCollide(new_x, self.bY):
            self.bX = new_x
        else:
            self.bvX *= -0.6
            self.bX += 1 if self.bvX > 0 else -1
        
        if not self.wouldCollide(self.bX, new_y):
            self.bY = new_y
        else:
            self.bvY *= -0.6
            self.bY += 1 if self.bvY > 0 else -1

    def inWall(self):
        if self.stopped:
            max_attempts = 10
            attempts = 0
            while attempts < max_attempts:
                colliding = False
                for x, y in self.collisionCircle((self.bX+4), (self.bY+4)):
                    if pyxel.pget(x, y) == 4:
                        colliding = True
                        break
                
                if not colliding:
                    break

                self.bX += cos(radians(self.rotation + 180)) * 2 
                self.bY += sin(radians(self.rotation + 180)) * 2
                attempts += 1

    def checkHoles(self):
        scale=16

        if self.holes == 0:
            pyxel.blt(7.5*scale,7.5*scale,(1),0,0,16,16, scale=scale)
            if not self.playing:
                self.bX = 20
                self.bY = 228
                self.playing = True

        elif self.holes == 1:
            pyxel.blt(7.5*scale,7.5*scale,(1),16,0,16,16, scale=scale)
            if not self.playing:
                self.bX = 20
                self.bY = 228
                self.playing = True

        elif self.holes == 2:
            pyxel.blt(7.5*scale,7.5*scale,(1),32,0,16,16, scale=scale)
            if not self.playing:
                self.bX = 20
                self.bY = 228
                self.playing = True

        elif self.holes == 3:
            pyxel.blt(7.5*scale,7.5*scale,(1),48,0,16,16, scale=scale)
            if not self.playing:
                self.bX = 20
                self.bY = 228
                self.playing = True

        elif self.holes == 4:
            pyxel.blt(7.5*scale,7.5*scale,(1),64,0,16,16, scale=scale)
            if not self.playing:
                self.bX = 20
                self.bY = 228
                self.playing = True

    def arrow(self):
        if self.stopped:
            pyxel.blt(self.bX, self.bY-4, (0), 8, 0, 8, 16, colkey=0, rotate=self.rotation+90, scale=(self.power/10)+1)

    def debug(self):
        pyxel.text(0, 0, (f"Rotation: {self.rotation}°"), 7)
        pyxel.text(0, 8, (f"Power: {self.power}"), 7)
        pyxel.text(0, 16, (f"Shots: {self.shots}"), 7)
        pyxel.text(0, 24, (f"X: {self.bX}"), 7)
        pyxel.text(0, 32, (f"Y: {self.bY}"), 7)
        pyxel.text(0, 40, (f"Stopped?: {self.stopped}"), 7)
        pyxel.text(0, 48, (f"Playing?: {self.playing}"), 7)
        pyxel.text(0, 56, (f"Holes: {self.holes}"), 7)
        pyxel.text(0, 64, (f"X Velocity: {self.bvX}"), 7)
        pyxel.text(0, 72, (f"Y Velocity: {self.bvY}"), 7)

    def info(self):
        pyxel.text(0, 0, (f"Rotation: {self.rotation}°"), 7)
        pyxel.text(0, 8, (f"Power: {self.power}"), 7)
        pyxel.text(0, 16, (f"Shots: {self.shots}"), 7)
        pyxel.text(0, 24, (f"Current hole: {self.holes}"), 7)

    def draw(self):
        pyxel.cls(0)
        self.checkHoles()
        pyxel.blt(self.bX, self.bY, (0), 0, 0, 8, 8, colkey=0)
        self.arrow()
        self.info()
        self.textStuff()
        #self.debug()
        
    def circle360(self):
        if self.rotation > 360:
            self.rotation = 0
        elif self.rotation < 0:
            self.rotation = 360

    def collisionCircle(self,x, y):
        size = 4
        positions=[]
        for direction in range(360):
            changeX = cos(radians(direction)) * size
            changeY = sin(radians(direction)) * size
            end = [int(x + changeX), int(y + changeY)]
            if end not in positions:
                positions.append(end)
        return positions

golf(0)