import pyxel
from math import *
import random
import time

class ball():
    def __init__(self, n):
        self.bX = 20 if n == 1 else 235 # Different starting positions
        self.bY = 228
        self.bvX = 0
        self.bvY = 0
        self.g = 0.1
        self.jump = 2
        self.upPressed = False
        self.player = n
        self.tag = 0

    def controls(self):
        if self.player == 2:  # Arrow keys for player 1
            if pyxel.btnp(pyxel.KEY_UP):
                if self.jump > 0:
                    self.bvY -= 2.5
                    self.jump -= 1
                self.upPressed = True
            if pyxel.btn(pyxel.KEY_DOWN):
                self.bvY += 1
            if pyxel.btn(pyxel.KEY_LEFT):
                self.bvX -= 0.12/1.18
            if pyxel.btn(pyxel.KEY_RIGHT):
                self.bvX += 0.12/1.18
            if pyxel.btnp(pyxel.KEY_R):
                self.bX = 20
                self.bY = 228
                self.bvX = 0
                self.bvY = 0
        
        elif self.player == 1:  # ZQSD keys for player 2
            if pyxel.btnp(pyxel.KEY_Z):  # Z = jump
                if self.jump > 0:
                    self.bvY -= 2.5
                    self.jump -= 1
                self.upPressed = True
            if pyxel.btn(pyxel.KEY_S):  # S = down
                self.bvY += 1
            if pyxel.btn(pyxel.KEY_Q):  # Q = left
                self.bvX -= 0.12/1.18
            if pyxel.btn(pyxel.KEY_D):  # D = right
                self.bvX += 0.12/1.18
            if pyxel.btnp(pyxel.KEY_T):  # T = reset for player 2
                self.bX = 50
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
        for i in circleCollision:
            x, y = i[0], i[1]
            if pyxel.pget(x, y) == 4:
                return True
        return False

    def moveBall(self):
        self.bvX *= 0.985
        self.bvY *= 0.985
        
        new_x = self.bX + self.bvX
        new_y = self.bY + self.bvY
        
        if not self.wouldCollide(new_x, self.bY):
            self.bX = new_x
        else:
            self.bvX *= -0.8
        
        if not self.wouldCollide(self.bX, new_y):
            self.bY = new_y
        else:
            self.bvY *= -0.8

    def collisionCircle(self, x, y):
        size = 4
        positions = []
        for direction in range(360):
            changeX = cos(radians(direction)) * size
            changeY = sin(radians(direction)) * size
            end = [int(x + changeX), int(y + changeY)]
            if end not in positions:
                positions.append(end)
        return positions

    def checkBallCollision(self, other_ball):
        """Check collision with another ball"""
        # Calculate distance between ball centers
        dx = (self.bX + 4) - (other_ball.bX + 4)  # +4 to get center of 8x8 sprite
        dy = (self.bY + 4) - (other_ball.bY + 4)
        distance = sqrt(dx*dx + dy*dy)
        
        # If balls are overlapping (collision radius = 4 pixels each, so 8 total)
        if distance < 8 and distance > 0:
            # Calculate collision normal
            nx = dx / distance
            ny = dy / distance
            
            # Separate balls to prevent overlap
            overlap = 8 - distance
            separation = overlap / 2
            
            # Store original positions
            orig_self_x, orig_self_y = self.bX, self.bY
            orig_other_x, orig_other_y = other_ball.bX, other_ball.bY
            
            # Try to separate balls
            new_self_x = self.bX + nx * separation
            new_self_y = self.bY + ny * separation
            new_other_x = other_ball.bX - nx * separation
            new_other_y = other_ball.bY - ny * separation
            
            # Check if separation would cause wall collision
            if not self.wouldCollide(new_self_x, new_self_y):
                self.bX = new_self_x
                self.bY = new_self_y
            
            if not other_ball.wouldCollide(new_other_x, new_other_y):
                other_ball.bX = new_other_x
                other_ball.bY = new_other_y
            
            # Calculate relative velocity
            dvx = self.bvX - other_ball.bvX
            dvy = self.bvY - other_ball.bvY
            
            # Calculate collision impulse
            impulse = 2 * (dvx * nx + dvy * ny) / 2  # Assuming equal mass
            
            # Apply impulse (with some energy loss)
            bounce_factor = 0.8
            self.bvX -= impulse * nx * bounce_factor
            self.bvY -= impulse * ny * bounce_factor
            other_ball.bvX += impulse * nx * bounce_factor
            other_ball.bvY += impulse * ny * bounce_factor
            return True
        return False

    def update(self):
        self.controls()
        self.moveBall()
        self.gravity()
        self.residual()
        self.checkCollision()
        self.outOfBounds()
        self.upPressed = False

    def draw(self):
        if self.player == 1:
            if self.tag != 1:
                pyxel.blt(self.bX, self.bY, 0, 0, 0, 8, 8, colkey=0)
            else:
                pyxel.blt(self.bX, self.bY, 0, 0, 8, 8, 8, colkey=0)
        elif self.player ==2:
            if self.tag != 2:
                pyxel.blt(self.bX, self.bY, 0, 8, 0, 8, 8, colkey=0)
            else:
                pyxel.blt(self.bX, self.bY, 0, 8, 8, 8, 8, colkey=0)

class terrain():
    def __init__(self):
        pass  # Initialize terrain data here if needed

    def checkHoles(self):
        scale = 8
        pyxel.blt(14*scale, 14*scale, 1, 0, 0, 32, 32, scale=scale)

class Tag:
    def __init__(self):
        pyxel.load("tag.pyxres")  # Make sure this file exists
        
        # Create instances as class attributes
        self.tag = random.randint(1,2)
        self.ball1 = ball(1)
        self.ball2 = ball(2)
        self.tag = random.randint(1,2)
        self.ball1.tag = self.tag
        self.ball2.tag= self.tag
        self.terrain = terrain()
        self.gameOver = False
        self.timerIs = 0
        self.done = False
        
        self.startTime = time.monotonic()*100

    def timer(self):
        self.currentTime = time.monotonic()*100
        
        self.timerIs = (int(self.currentTime) - int(self.startTime))/100
        if self.timerIs > 0:
            self.remainingTime = 50 - self.timerIs
        else:
            self.remainingTime = 0
        pyxel.text(0, 8, f"Time:{self.timerIs}", 7)

    def isGameOver(self):
        if self.timerIs > 50:
            pyxel.text(200, 8, f"Player {self.ball1.tag} lost", 7)
            self.gameOver = True
            if pyxel.btnp(pyxel.KEY_A):
                    self.done = True

    def debug(self):
        # Debug info for both balls
        pyxel.text(0, 8, "Player 1 (Arrows):", 7)
        pyxel.text(0, 16, f"X: {self.ball1.bX:.1f}", 7)
        pyxel.text(0, 24, f"Y: {self.ball1.bY:.1f}", 7)
        pyxel.text(0, 32, f"VelX: {self.ball1.bvX:.2f}", 7)
        pyxel.text(0, 40, f"VelY: {self.ball1.bvY:.2f}", 7)
        
        pyxel.text(0, 56, "Player 2 (ZQSD):", 7)
        pyxel.text(0, 64, f"X: {self.ball2.bX:.1f}", 7)
        pyxel.text(0, 72, f"Y: {self.ball2.bY:.1f}", 7)
        pyxel.text(0, 80, f"VelX: {self.ball2.bvX:.2f}", 7)
        pyxel.text(0, 88, f"VelY: {self.ball2.bvY:.2f}", 7)
        
        pyxel.text(0, 104, "R=Reset P1, T=Reset P2", 7)

    def update(self):
        self.ball1.update()
        self.ball2.update()
        
        # Check ball-to-ball collision
        if not self.gameOver:
            if self.ball1.checkBallCollision(self.ball2):
                if self.ball1.tag <2:
                    self.ball1.tag+=1
                    self.ball2.tag+=1
                else:
                    self.ball1.tag=1
                    self.ball2.tag=1
        
        # Re-check wall collisions after ball collision (to prevent pushing through walls)
        if self.ball1.wouldCollide(self.ball1.bX, self.ball1.bY):
            self.ball1.bX -= self.ball1.bvX * 0.1  # Small step back
            self.ball1.bY -= self.ball1.bvY * 0.1
            self.ball1.bvX *= -0.5  # Reduce velocity
            self.ball1.bvY *= -0.5
            
        if self.ball2.wouldCollide(self.ball2.bX, self.ball2.bY):
            self.ball2.bX -= self.ball2.bvX * 0.1  # Small step back
            self.ball2.bY -= self.ball2.bvY * 0.1
            self.ball2.bvX *= -0.5  # Reduce velocity
            self.ball2.bvY *= -0.5

    def draw(self):
        pyxel.cls(0)
        self.terrain.checkHoles()
        self.ball1.draw()
        self.ball2.draw()
        #self.debug()
        self.timer()
        self.isGameOver()

