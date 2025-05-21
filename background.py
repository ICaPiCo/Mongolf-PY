import random
import math
import pyxel
#from testMeteo import weather_dir,

LYR_CNT = 3

class Background:
    def __init__(self):
        self.x = 128  # Start in the middle of the screen
        self.y = 128
        self.scale = 1
        self.direction = 0
        self.speed = 0
        
    def input_change(self):
        # Handle position controls
        if pyxel.btn(pyxel.KEY_D):
            self.x -= 1
        if pyxel.btn(pyxel.KEY_A):
            self.x += 1
        if pyxel.btn(pyxel.KEY_W):
            self.y += 1
        if pyxel.btn(pyxel.KEY_S):
            self.y -= 1
            
        # Handle scale controls
        if pyxel.btn(pyxel.KEY_Q) and self.scale < 30:
            self.scale += 0.5
        if pyxel.btn(pyxel.KEY_E) and self.scale > 0.5:
            self.scale -= 0.5
            
        # Handle direction and speed
        if pyxel.btn(pyxel.KEY_RIGHT):
            self.direction = (self.direction + 10) % 360
        if pyxel.btn(pyxel.KEY_LEFT):
            self.direction = (self.direction - 10) % 360
        if pyxel.btn(pyxel.KEY_UP):
            self.speed = min(self.speed + 0.5, 10)
        if pyxel.btn(pyxel.KEY_DOWN):
            self.speed = max(self.speed - 1, 0)
    
    def move(self):
        if self.speed > 0:
            self.x -= self.speed * math.cos(math.radians(self.direction))
            self.y -= self.speed * math.sin(math.radians(self.direction))

pyxel.init(256, 256, title="MONGO", display_scale=3)
pyxel.load("my_resource.pyxres")



class tile_grid:
    def __init__(self):
        self.background_equivalent = Background()
        self.x = 0
        self.y = 0
        self.weather_data = [[[] for i in range (256**2)] for j in range(LYR_CNT)]
        # [[[speed,direction],[speed,direction]...][]]
    def fill_vectors(self,layer,index,speed,direction): # [[]...]
        self.weather_data[layer][index] = [speed, direction]
    def __str__(self):
        return str(self.weather_data[0][:10])
#Lille tuto for pyxel
grid = tile_grid()
'''
weather_data_l = [[[random.random()]] for i in range(LYR_CNT)]
weather_dir_l = [[random.choice(360)] for i in range(LYR_CNT)]
'''
'''
for layer in range(LYR_CNT):
    for i,n in enumerate(zip(weather_data_l,weather_dir_l)):
        grid.fill_vectors(layer,i, weather_data[i], weather_dir[i])
'''

def update():
    # Check for quit
    if pyxel.btnp(pyxel.KEY_Q) and pyxel.btn(pyxel.KEY_CTRL):
        pyxel.quit()
        
    # Update background
    grid.background_equivalent.input_change()
    grid.background_equivalent.move()

def draw():
    # Clear the screen
    pyxel.cls(0)
    
    # Draw the sprite
    # Parameters: x, y, img_bank, u, v, width, height, colkey (transparent color)
    pyxel.blt(
        grid.background_equivalent.x, grid.background_equivalent.y,  # Position
        1,                          # Image bank (0-2)
        0, 0,                       # Top-left position in the image bank
        256, 256,                     # Width and height of the sprite
        colkey=0,                   # Transparent color (0 is usually black)
        scale=grid.background_equivalent.scale      # Scale factor
    )
    
    # Display debug info
    pyxel.text(5, 5, f"Dir: {grid.background_equivalent.direction}, Speed: {grid.background_equivalent.speed:.1f}", 7)
    pyxel.text(5, 15, f"X: {grid.background_equivalent.x:.1f}, Y: {grid.background_equivalent.y:.1f}", 7)

# Start the game loop
pyxel.run(update, draw)
