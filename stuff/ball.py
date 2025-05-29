import pyxel
import math

class Ball:
    def __init__(self, x, y, radius, color, vx=0, vy=0):
        self.x = x                  # x-position
        self.y = y                  # y-position
        self.radius = radius        # ball radius
        self.color = color          # ball color
        self.speed_x = vx           # x-velocity
        self.speed_y = vy           # y-velocity
        self.bounce_factor = 0.8    # energy loss on bounce (1.0 = no loss)
        
        # Pre-calculate offset points around the ball for normal detection
        self.offsets = []
        steps = 16  # Number of points to check
        for i in range(steps):
            angle = 2 * math.pi * i / steps
            offset_x = math.cos(angle) * self.radius
            offset_y = math.sin(angle) * self.radius
            self.offsets.append((offset_x, offset_y))
    
    def update(self):
        # Simple update - just save old position and apply velocity
        old_x, old_y = self.x, self.y
        
        # Apply velocity
        self.x += self.speed_x
        self.y += self.speed_y
        
        # Check for collision
        if self.is_colliding():
            # Move back to original position before collision
            self.x, self.y = old_x, old_y
            
            # Find the normal vector of the collision surface
            normal_x, normal_y = self.find_normal()
            
            # Calculate bounce using the normal vector
            self.bounce(normal_x, normal_y)
            
            # Move slightly along the normal to prevent sticking
            self.x += normal_x * 0.5
            self.y += normal_y * 0.5
    
    def is_colliding(self):
        # Check if ball is colliding with any non-black pixel
        min_x = max(0, int(self.x - self.radius))
        max_x = min(pyxel.width - 1, int(self.x + self.radius))
        min_y = max(0, int(self.y - self.radius))
        max_y = min(pyxel.height - 1, int(self.y + self.radius))
        
        for check_x in range(min_x, max_x + 1):
            for check_y in range(min_y, max_y + 1):
                # If pixel is within radius
                dx = check_x - self.x
                dy = check_y - self.y
                if dx*dx + dy*dy <= self.radius*self.radius:
                    # Get the pixel color at this position
                    if pyxel.pget(check_x, check_y) != 0:  # If not black
                        return True
        return False
    
    def find_normal(self):
        # Find the normal vector of the collision surface
        collision_points = []
        
        # Check each offset point
        for offset_x, offset_y in self.offsets:
            check_x = int(self.x + offset_x)
            check_y = int(self.y + offset_y)
            
            # Check if this point is in a wall (non-black)
            if (0 <= check_x < pyxel.width and 
                0 <= check_y < pyxel.height and
                pyxel.pget(check_x, check_y) != 0):
                # Add this point to our collision points
                collision_points.append((offset_x, offset_y))
        
        # If no collision points found, use a default normal
        if not collision_points:
            return 0, -1  # Default to pointing up
        
        # Calculate the average normal vector (pointing away from collision)
        normal_x = 0
        normal_y = 0
        for offset_x, offset_y in collision_points:
            # Invert because we want normal pointing away from wall
            normal_x -= offset_x  
            normal_y -= offset_y
        
        # Normalize the resulting normal vector
        length = math.sqrt(normal_x*normal_x + normal_y*normal_y)
        if length > 0:
            normal_x /= length
            normal_y /= length
            
        return normal_x, normal_y
    
    def bounce(self, normal_x, normal_y):
        # Calculate dot product of velocity and normal
        dot_product = self.speed_x * normal_x + self.speed_y * normal_y
        
        # Calculate reflection vector: v' = v - 2(v·n)n
        # This is the key formula for reflection!
        self.speed_x = self.speed_x - 2 * dot_product * normal_x
        self.speed_y = self.speed_y - 2 * dot_product * normal_y
        
        # Apply bounce factor to reduce energy
        self.speed_x *= self.bounce_factor
        self.speed_y *= self.bounce_factor
    
    def draw(self):
        # Draw the ball
        pyxel.circ(self.x, self.y, self.radius, self.color)


class App:
    def __init__(self):
        # Initialize Pyxel with window size
        pyxel.init(160, 120, title="Basic Bounce Physics")
        
        # Create a ball with initial velocity
        self.ball = Ball(40, 30, 5, 11, vx=1.5, vy=1.2)
        
        # Draw the level/obstacles once at the beginning
        pyxel.cls(0)
        self.draw_level()
        
        # Keep a copy of the background
        self.bg_image = pyxel.Image(160, 120)
        self.bg_image.load(0, 0, "pyxel_screen_capture.png")
        
        # Start the game loop
        pyxel.run(self.update, self.draw)
    
    def draw_level(self):
        # Draw some obstacles for the ball to bounce off
        pyxel.circb(80, 60, 40, 7)  # Circle in middle
        
        # Draw a triangle
        pyxel.tri(120, 20, 140, 60, 100, 80, 14)
        
        # Draw some rectangles
        pyxel.rectb(20, 20, 40, 30, 15)
        pyxel.rectb(100, 90, 50, 20, 12)
        
        # Draw a curved shape
        for i in range(20):
            angle = i / 20 * math.pi
            x = 40 + math.cos(angle) * 20
            y = 100 + math.sin(angle) * 15
            pyxel.pset(int(x), int(y), 9)
    
    def update(self):
        # Exit if Q key is pressed
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()
        
        # Update ball
        self.ball.update()
    
    def draw(self):
        # Clear screen
        pyxel.cls(0)
        
        # Redraw the level
        self.draw_level()
        
        # Draw ball
        self.ball.draw()
        
        # Draw instructions
        pyxel.text(5, 5, "Q to quit", 7)


# Run the app
if __name__ == "__main__":
    App()