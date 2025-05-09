import pygame
import sys

screen_x, screen_y = 1920, 1200

pygame.init()
screen = pygame.display.set_mode((screen_x, screen_y))
pygame.display.set_caption("test")

# Create font
font = pygame.font.SysFont(None, 48)

class Game:
    def __init__(self, name, angle):
        self.name = name
        self.angle = angle
        self.running = True

    def update(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.angle += 1
            if self.angle > 360:
                self.angle = 0
        elif keys[pygame.K_RIGHT]:
            self.angle -= 1
            if self.angle < 0:
                self.angle = 360

    def draw(self):
        screen.fill((0, 0, 0))
        text_to_draw = "Boat"
        text_surface = font.render(text_to_draw, True, (255, 255, 255))
        
        # Rotate the text surface
        rotated_text = pygame.transform.rotate(text_surface, self.angle)
        
        # Get the rect of the rotated text and center it
        text_rect = rotated_text.get_rect(center=(screen_x/2, screen_y/2))
        
        # Draw the rotated text
        screen.blit(rotated_text, text_rect)
        pygame.display.update()

    def get_text_size(self, text):
        text_surface = font.render(text, True, (255, 255, 255))
        return text_surface.get_size()

    def get_text_center(self, text):
        text_width, text_height = self.get_text_size(text)
        return (screen_x - text_width) / 2, (screen_y - text_height) / 2


boat = Game("boat", 0)

while boat.running:
    boat.update()
    boat.draw()
    pygame.time.Clock().tick(60)  # Limit to 60 FPS

pygame.quit()
sys.exit()