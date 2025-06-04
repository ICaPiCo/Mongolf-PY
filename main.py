import pyxel
import random
import game_clock, game_coin, game_golf, game_shooter, game_tag, game_wam

class HotAirBalloonGame:
    def __init__(self):
        # Initialize game window
        pyxel.init(256, 256, title="Hot Air Balloon Adventure", display_scale=4, fps=70)
        pyxel.load("my_resource.pyxres")
        
        # Game state
        self.current_game = "balloon"
        self.minigame = None
        
        # Balloon properties
        self.balloon_x = pyxel.width // 2
        self.balloon_y = (pyxel.height // 2) + 50

        # Background properties
        self.bg_x = 0
        self.bg_y = 0
        self.scale = 1
        pyxel.mouse(True)
        self.dot_positions = [
            (126, 165), (120, 139), (116, 123), 
            (50, 38), (109, 181), (184, 160)
        ]
    
    def update(self):
        if self.current_game == "balloon":
            self.update_balloon()
        elif self.minigame:
            self.minigame.update()
            # Add logic to return to balloon game when minigame ends
    
    def update_balloon(self):
        # Balloon movement controls
        if pyxel.btn(pyxel.KEY_UP):
            self.balloon_y -= 1
        if pyxel.btn(pyxel.KEY_DOWN):
            self.balloon_y += 1
        if pyxel.btn(pyxel.KEY_LEFT):
            self.balloon_x -= 1
        if pyxel.btn(pyxel.KEY_RIGHT):
            self.balloon_x += 1

        # Check for minigame trigger
        distance = min(abs(self.balloon_x - x) + abs(self.balloon_y - y) for x, y in self.dot_positions)
        if distance < 4 and pyxel.btnp(pyxel.KEY_SPACE):
            self.start_minigame()
    
    def start_minigame(self):
        self.current_game = "minigame"
        games = [
            game_clock.Clock,
            game_coin.Coin,
            game_golf.Golf,
            game_shooter.Shooter,
            game_tag.Tag,
            game_wam.Wam
        ]
        self.minigame = random.choice(games)()
    
    def draw(self):
        if self.current_game == "balloon":
            self.draw_balloon()
        elif self.minigame:
            self.minigame.draw()
    
    def draw_balloon(self):
        pyxel.cls(0)
        
        # Draw background sprite
        pyxel.blt(
            self.bg_x, self.bg_y,
            1,                      # Image bank
            0, 0,                   # Source coordinates
            256, 256,               # Source dimensions
            colkey=0,
            scale=1
        )
        
        # Draw all collected dots
        for x, y in self.dot_positions:
            pyxel.circ(x, y, 2, pyxel.COLOR_YELLOW)
        
        # Draw the hot air balloon
        pyxel.circ(self.balloon_x, self.balloon_y, 4, pyxel.COLOR_RED)

        distance = min(abs(self.balloon_x - x) + abs(self.balloon_y - y) for x, y in self.dot_positions)
        if distance < 4:
            text = "Want to play a minigame? (SPACE)"
            pyxel.text((pyxel.width - len(text) * 4)//2, 10, text, pyxel.COLOR_WHITE)

# Create and run the game
game = HotAirBalloonGame()
pyxel.run(game.update, game.draw)