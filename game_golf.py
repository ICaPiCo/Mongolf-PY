import pyxel
from math import *

class Golf:

    def __init__(self):
            """
            Initializes a new instance of the Golf class, setting initial values for ball position, velocity, game state, and loading the golf game resources.
            """
            self.bX = 20
            self.bY = 228
            self.bvX = 0
            self.bvY = 0

            self.playing = False
            self.stopped = True
            self.shots = 0
            self.power = 3
            self.rotation = 270
            self.holes = 0
            pyxel.load("golf.pyxres")

    def controls(self):
        """
        Handles user input for the golf game.

        Updates the game state based on the following keyboard inputs:
            - A: Quits the game
            - Space: Hits the ball with the current power and rotation
            - Up arrow: Increases the power
            - Down arrow: Decreases the power
            - Left arrow: Decreases the rotation
            - Right arrow: Increases the rotation
            - R: Resets the ball to its initial position
        """
        if pyxel.btnp(pyxel.KEY_A):
            self.done = True

        if pyxel.btnp(pyxel.KEY_SPACE):
            self.stopped = False
            self.bvX = cos(radians(self.rotation)) * self.power
            self.bvY = sin(radians(self.rotation)) * self.power

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
        """
        Checks if the ball's velocity is close to zero and stops the ball if so.

        If the absolute values of both the x and y components of the ball's velocity
        are less than 0.1, the ball is considered stopped. In this case, the ball's
        stopped state is set to True, the number of shots is incremented, and the
        ball's velocity is reset to zero. The power is also reset to its initial value.
        """
        if abs(self.bvX) < 0.1 and abs(self.bvY) < 0.1:
            self.stopped = True
            self.shots += 1
            self.bvX = 0
            self.bvY = 0
            self.power = 3

    def outOfBounds(self):
        """
        Checks if the ball is out of the game boundaries and resets its position if so.

        If the ball's x or y coordinates are outside the range of 0 to 256, this function
        stops the ball, increments the number of shots, and resets the ball's position to
        its initial coordinates. The ball's velocity and power are also reset to their
        initial values.
        """
        if self.bX < 0 or self.bX > 256 or self.bY < 0 or self.bY > 256:
            self.stopped = True
            self.shots += 1
            self.bX = 20
            self.bY = 228
            self.bvX = 0
            self.bvY = 0
            self.power = 3

    def stopNow(self):
        """
        Immediately stops the ball's movement and resets its velocity.

        Sets the ball's stopped state to True, increments the number of shots, and resets the ball's velocity and power to their initial values.
        """
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
        """
        Checks for collisions between the ball and the environment.

        This function checks for collisions with walls, holes, and other obstacles.
        It updates the game state accordingly, including the ball's position, velocity, and game flags.

        Returns:
            bool: True if a collision with a wall is detected, False otherwise.
        """
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
            
            elif pyxel.pget(x, y) == 15:
                self.bvX *= 0.99
                self.bvY *= 0.99

    def textStuff(self):
        """
        Displays in-game text based on the current state of the game.

        Depending on the number of holes completed, this function displays different messages to the player.
        These messages include instructions for the player, congratulatory messages, and the player's score.
        """
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
        """
        Updates the game state by handling user input, moving the ball, checking for collisions, 
        and updating the game flags accordingly.

        Parameters:
            None

        Returns:
            None
        """
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
        """
        Updates the position and velocity of the ball based on its current velocity and collision with the environment.

        This function applies a friction factor to the ball's velocity, calculates its new position, and checks for collisions with walls.
        If a collision is detected, it updates the ball's velocity and position accordingly.

        Parameters:
            None

        Returns:
            None
        """
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
        """
        Moves the ball out of a wall if it is stopped and colliding with one.

        This function checks if the ball is stopped and colliding with a wall. If so, it attempts to move the ball out of the wall by adjusting its position in the opposite direction of its rotation. The function repeats this process up to a maximum number of attempts until the ball is no longer colliding with the wall.

        Parameters:
            None

        Returns:
            None
        """
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
        """
        Draws the current hole on the screen based on the number of holes completed.

        Parameters:
            None

        Returns:
            None
        """
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
        """
        Draws an arrow on the screen to indicate the direction of the golf ball when it is stopped.

        Parameters:
            None

        Returns:
            None
        """
        if self.stopped:
            pyxel.blt(self.bX, self.bY-4, (0), 8, 0, 8, 16, colkey=0, rotate=self.rotation+90, scale=(self.power/10)+1)

    def debug(self):
        """
        Displays debug information about the current state of the game.

        This function prints various game-related variables to the screen, including rotation, power, shots taken, ball position, velocity, and game state.

        Parameters:
            None

        Returns:
            None
        """
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
        """
        Displays in-game information about the current state of the golf game.

        This function prints various game-related variables to the screen, including rotation, power, shots taken, and current hole.

        Parameters:
            None

        Returns:
            None
        """
        pyxel.text(0, 0, (f"Rotation: {self.rotation}°"), 7)
        pyxel.text(0, 8, (f"Power: {self.power}"), 7)
        pyxel.text(0, 16, (f"Shots: {self.shots}"), 7)
        pyxel.text(0, 24, (f"Current hole: {self.holes}"), 7)

    def draw(self):
        """
        Draws the current state of the golf game on the screen.

        This function clears the screen, draws the current hole, the golf ball, an arrow indicating the ball's direction, 
        and displays in-game information such as rotation, power, shots taken, and the current hole.

        Parameters:
            None

        Returns:
            None
        """
        pyxel.cls(0)
        self.checkHoles()
        pyxel.blt(self.bX, self.bY, (0), 0, 0, 8, 8, colkey=0)
        self.arrow()
        self.info()
        self.textStuff()
        #self.debug()
        
    def circle360(self):
        """
        Ensures the rotation value stays within the range of 0 to 360 degrees.

        Parameters:
            None

        Returns:
            None
        """
        if self.rotation > 360:
            self.rotation = 0
        elif self.rotation < 0:
            self.rotation = 360

    def collisionCircle(self,x, y):
        """
        Generates a circle of positions around a given point.

        This function takes in x and y coordinates and returns a list of positions that form a circle around the point.
        The circle is defined by a size parameter, which determines the radius of the circle.

        Parameters:
            x (int): The x-coordinate of the center of the circle.
            y (int): The y-coordinate of the center of the circle.

        Returns:
            list: A list of positions that form a circle around the given point.
        """
        size = 4
        positions=[]
        for direction in range(360):
            changeX = cos(radians(direction)) * size
            changeY = sin(radians(direction)) * size
            end = [int(x + changeX), int(y + changeY)]
            if end not in positions:
                positions.append(end)
        return positions

#Golf()