import pyxel
from math import *

class game:

    def __init__(self, holes):
            self.bX = 20
            self.bY = 228
            self.bvX = 0
            self.bvY = 0
            self.g = 0.1
            self.jump = 2
            self.holes = holes
            self.upPressed = False
            pyxel.init(256, 256, title="Golf", fps=120, display_scale=4)
            pyxel.load("assets.pyxres")
            pyxel.run(self.update, self.draw)

    def controls(self):
        if pyxel.btnp(pyxel.KEY_UP):
            if self.jump > 0:
                self.bvY -= 3.5
                self.jump -= 1
            self.upPressed = True
        elif pyxel.btn(pyxel.KEY_DOWN):
            self.bvY += 0.12
        elif pyxel.btn(pyxel.KEY_LEFT):
            self.bvX -= 0.12
        elif pyxel.btn(pyxel.KEY_RIGHT):
            self.bvX += 0.12
        elif pyxel.btnp(pyxel.KEY_R):
            self.bX = 20
            self.bY = 228
            self.bvX = 0
            self.bvY = 0

    def gravity(self):
        if not self.upPressed:
            self.bvY += self.g

    def residual(self):
        if abs(self.bvX) < 0.1:
            self.bvX = 0

        if abs(self.bvY) < 0.1:
            self.bvY = 0

    def outOfBounds(self):
        if self.bX < 0 or self.bX > 256 or self.bY < 0 or self.bY > 256:
            self.bX = 20
            self.bY = 228
            self.bvX = 0
            self.bvY = 0

    def stopNow(self):
        self.bvX = 0
        self.bvY = 0

    def wouldCollide(self, x, y):
        """Check if position (x,y) would collide with walls"""
        for px, py in self.collisionCircle(x+4, y+4):
            if pyxel.pget(px, py) == 4:
                self.jump = 2
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

    def update(self):
        self.controls()
        self.moveBall()
        self.gravity()
        self.residual()
        self.checkCollision()
        self.outOfBounds()
        self.upPressed = False

    def moveBall(self):
        self.bvX *= 0.985
        self.bvY *= 0.985
        
        new_x = self.bX + self.bvX
        new_y = self.bY + self.bvY
        
        if not self.wouldCollide(new_x, self.bY):
            self.bX = new_x
        else:
            self.bvX *= -0.8
            #self.bX += 1 if self.bvX > 0 else -1
        
        if not self.wouldCollide(self.bX, new_y):
            self.bY = new_y
        else:
            self.bvY *= -0.8
            #self.bY += 1 if self.bvY > 0 else -1

    def checkHoles(self):
        scale=16
        pyxel.blt(7.5*scale,7.5*scale,(1),0,0,16,16, scale=scale)

    def debug(self):
        pyxel.text(0, 24, (f"X: {self.bX}"), 7)
        pyxel.text(0, 32, (f"Y: {self.bY}"), 7)
        pyxel.text(0, 64, (f"X Velocity: {self.bvX}"), 7)
        pyxel.text(0, 72, (f"Y Velocity: {self.bvY}"), 7)
        pyxel.text(0, 96, (f"Jump: {self.jump}"), 7)

    def draw(self):
        pyxel.cls(0)
        self.checkHoles()
        pyxel.blt(self.bX, self.bY, (0), 0, 0, 8, 8, colkey=0)
        self.debug()

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

game(0)