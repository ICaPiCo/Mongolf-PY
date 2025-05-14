import pyxel
import math

class ShowCase:
    def __init__(self):
        self.boat_x = 0
        self.width = 192
        self.height = 120
        self.amplitude = 10
        self.frequency = 0.05
        self.phase = 0
        self.boat_speed = 0.5
        self.animation_X = 0
        
        pyxel.init(self.width, self.height, title="FunBoat")
        pyxel.load("my_resource.pyxres")
        pyxel.run(self.update, self.draw)
    
    def sea_y(self, x):
        return self.height // 2 + self.amplitude * math.sin(self.frequency * x + self.phase)
    
    def sea_slope_angle(self, x):
        slope = self.amplitude * self.frequency * math.cos(self.frequency * x + self.phase)
        angle = math.degrees(math.atan(slope))
        return angle
    
    def update(self):
        self.phase += 0.02
        self.boat_x += self.boat_speed
        
        if self.boat_x > self.width:
            self.boat_x = -16
        
        if pyxel.btnp(pyxel.KEY_Q) or pyxel.btnp(pyxel.KEY_ESCAPE):
            pyxel.quit()
        elif pyxel.btnp(pyxel.KEY_RIGHT) and self.boat_speed<2:
            self.boat_speed += 0.5
            self.animation_X += 8
        elif pyxel.btnp(pyxel.KEY_LEFT) and self.boat_speed>0.5:
            self.boat_speed -= 0.5
            self.animation_X -= 8
        elif pyxel.btn(pyxel.KEY_UP):
            self.amplitude += 1
        elif pyxel.btn(pyxel.KEY_DOWN):
            self.amplitude -= 1

    def draw(self):
        pyxel.cls(12)
        
        # Draw sea
        for x in range(self.width):
            y = int(self.sea_y(x))
            for y_fill in range(y, self.height):
                pyxel.pset(x, y_fill, 1)
        
        # Calculate boat position and rotation
        boat_y = self.sea_y(self.boat_x)
        angle = self.sea_slope_angle(self.boat_x)
        
        pyxel.blt(int(self.boat_x - 3),int(boat_y - 8),0,(0+self.animation_X), 0,8, 8,0,rotate=angle)


ShowCase()