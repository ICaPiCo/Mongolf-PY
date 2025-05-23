import random
import math
import pyxel
#from testMeteo import weather_dir,

LYR_CNT = 3

class Background:
    def __init__(self):
        self.x = 0  # Start in the middle of the screen
        self.y = 0
        self.scale = 2
        self.direction = 0
        self.speed = 0
        
    def input_change(self):
        # Handle scale controls
        if pyxel.btn(pyxel.KEY_Q) and self.scale < 30:
            self.scale += 0.3
        if pyxel.btn(pyxel.KEY_E) and self.scale > 0.5:
            self.scale -= 0.3
            
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
            # Calculate new positions
            new_x = self.x - self.speed * math.cos(math.radians(self.direction))
            new_y = self.y - self.speed * math.sin(math.radians(self.direction))
            
            # Check boundaries before applying movement
            map_size = 256 * self.scale
            screen_size = 256
            
           
            if map_size > screen_size:
                min_boundary = screen_size - map_size
                max_boundary = 0
                if min_boundary <= new_x <= max_boundary:
                    self.x = new_x
                if min_boundary <= new_y <= max_boundary:
                    self.y = new_y
            else:
                # For small maps, keep them fully visible
                min_boundary = 0
                max_boundary = screen_size - map_size
                
                # Only update if within bounds
                if min_boundary <= new_x <= max_boundary:
                    self.x = new_x
                if min_boundary <= new_y <= max_boundary:
                    self.y = new_y

pyxel.init(256, 256, title="MONGO", display_scale=3)
pyxel.load("my_resource.pyxres")

class tile_grid:
    def __init__(self):
        self.background_equivalent = Background()
        self.weather_data = [[[] for i in range(256**2)] for j in range(LYR_CNT)]
        # [[[speed,direction],[speed,direction]...][]]
        self.grid_visible = True
        self.grid_size = 16  # Size of grid cells in pixels
        self.hover_x = -1
        self.hover_y = -1
        self.current_layer = 0  # Current layer being viewed
        
    def fill_vectors(self, layer, index, speed, direction):
        self.weather_data[layer][index] = [speed, direction]
    
    def screen_to_grid(self, screen_x, screen_y):
        """Convert screen coordinates to grid coordinates"""
        
        bg = self.background_equivalent
        if bg.scale == 0: 
            return -1, -1
            
        
        rel_x = (screen_x - bg.x) / bg.scale
        rel_y = (screen_y - bg.y) / bg.scale
        
        # Check if within bounds of the map
        if 0 <= rel_x < 256 and 0 <= rel_y < 256:
            grid_x = int(rel_x)
            grid_y = int(rel_y)
            return grid_x, grid_y
        return -1, -1
    
    def update_hover(self):
        """Update the hover position based on mouse position"""
        mouse_x = pyxel.mouse_x
        mouse_y = pyxel.mouse_y
        self.hover_x, self.hover_y = self.screen_to_grid(mouse_x, mouse_y)
    
    def draw_grid(self):
        """Draw the grid overlay on the map"""
        if not self.grid_visible:
            return
            
        bg = self.background_equivalent
        
        
        start_x = max(0, int(-bg.x / bg.scale))
        end_x = min(256, int((256 - bg.x) / bg.scale))
        start_y = max(0, int(-bg.y / bg.scale))
        end_y = min(256, int((256 - bg.y) / bg.scale))
        
        # Draw vertical grid lines (aligned with the map)
        for i in range(start_x - (start_x % self.grid_size), end_x + self.grid_size, self.grid_size):
            screen_x = bg.x + i * bg.scale
            if 0 <= screen_x < 256:
                pyxel.line(screen_x, 0, screen_x, 256, 5)
        
        # Draw horizontal grid lines (aligned with the map)
        for i in range(start_y - (start_y % self.grid_size), end_y + self.grid_size, self.grid_size):
            screen_y = bg.y + i * bg.scale
            if 0 <= screen_y < 256:
                pyxel.line(0, screen_y, 256, screen_y, 5)
    
    def draw_hover_info(self):
        """Draw information about the hovered grid cell"""
        if self.hover_x >= 0 and self.hover_y >= 0:
            # Highlight the hovered grid cell
            bg = self.background_equivalent
            cell_x = bg.x + self.hover_x * bg.scale
            cell_y = bg.y + self.hover_y * bg.scale
            cell_size = bg.scale
            
            
            pyxel.rectb(cell_x, cell_y, cell_size, cell_size, 8)  # Color 8 is red
            
            
            grid_index = self.hover_y * 256 + self.hover_x
            
            
            vector_info = "No vector data"
            if 0 <= grid_index < 256**2 and len(self.weather_data[self.current_layer]) > grid_index and self.weather_data[self.current_layer][grid_index]:
                speed, direction = self.weather_data[self.current_layer][grid_index]
                vector_info = f"Speed: {speed:.1f}, Dir: {direction:.1f}"
            
            # Display information
            info_text = f"Grid: ({self.hover_x},{self.hover_y})\nIndex: {grid_index}\nLayer: {self.current_layer}\n{vector_info}"
            
            
            text_x = 5
            text_y = 35
            
            # Draw background for text
            pyxel.rect(text_x-2, text_y-2, len(info_text.split('\n')[0])*4+4, 30, 1)
            
            # Draw text lines
            for i, line in enumerate(info_text.split('\n')):
                pyxel.text(text_x, text_y + i*8, line, 7)
    
    def toggle_grid(self):
        """Toggle grid visibility"""
        self.grid_visible = not self.grid_visible
    
    def cycle_layer(self):
        
        self.current_layer = (self.current_layer + 1) % LYR_CNT
    
    def __str__(self):
        return str(self.weather_data[0][:10])


grid = tile_grid()

def update():
    
    if pyxel.btnp(pyxel.KEY_Q) and pyxel.btn(pyxel.KEY_CTRL):
        pyxel.quit()
    
    
    if pyxel.btnp(pyxel.KEY_G):
        grid.toggle_grid()
    
    
    if pyxel.btnp(pyxel.KEY_L):
        grid.cycle_layer()
    
    # Update background
    grid.background_equivalent.input_change()
    grid.background_equivalent.move()
    
    # Update hover position
    grid.update_hover()

def draw():
    # Clear the screen
    pyxel.cls(0)
    
    # Draw the sprite
    pyxel.blt(
        grid.background_equivalent.x, grid.background_equivalent.y,  # Position
        1,                          # Image bank (0-2)
        0, 0,                       # Top-left position in the image bank
        256, 256,                   # Width and height of the sprite
        colkey=0,                   # Transparent color (0 is usually black)
        scale=grid.background_equivalent.scale  # Scale factor
    )
    
    # Draw the grid overlay
    grid.draw_grid()
    
    # Draw hover information
    grid.draw_hover_info()
    
    # Display debug info
    pyxel.text(5, 5, f"Dir: {grid.background_equivalent.direction}, Speed: {grid.background_equivalent.speed:.1f}", 7)
    pyxel.text(5, 15, f"X: {grid.background_equivalent.x:.1f}, Y: {grid.background_equivalent.y:.1f}", 7)
    pyxel.text(5, 25, f"Scale: {grid.background_equivalent.scale:.1f} Grid: {'ON' if grid.grid_visible else 'OFF'}", 7)

# Enable mouse
pyxel.mouse(True)

# Start the game loop
pyxel.run(update, draw)