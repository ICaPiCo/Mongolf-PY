import sys
import pyxel
import random
from math import *
import game_clock, game_coin, game_golf, game_shooter, game_tag, game_wam

print("Starting game...")

class HotAirBalloonGame:
    def __init__(self):
        """
        Initializes a new instance of the HotAirBalloonGame class.
        
        Sets up the game window, loads the game resources, and initializes the game state.
        
        Parameters:
            None
        
        Returns:
            None
        """
        print("Initializing game...")
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
        self.isMenu = True
        
        # 3D Menu properties (from your paste.txt)
        self.menu_xAxis = 0
        self.menu_yAxis = 8.4
        self.menu_rotation = 0
        self.menu_scale = 6
        self.letterSize = 16
        self.big = 3
        self.medium = 2
        
        print("Starting game loop...")
        pyxel.run(self.update, self.draw)
    
    def update(self):
        """
        Updates the game state based on the current game mode.

        If the game is in the menu state, it calls the menuUpdate method.
        Otherwise, it updates the game state based on the current game type.
        If a minigame is active, it updates the minigame state and checks if it's done.
        If the minigame is done, it resets the game state to the balloon game.

        Parameters:
            None

        Returns:
            None
        """
        if self.isMenu:
            self.menuUpdate()
        else:
            if self.current_game == "balloon":
                self.update_balloon()
            elif self.minigame:
                self.minigame.update()
                if getattr(self.minigame, "done", False):
                    self.current_game = "balloon"
                    self.minigame = None

    def update_balloon(self):
        """
        Updates the balloon's position based on user input and checks for minigame triggers.

        Parameters:
            None

        Returns:
            None
        """
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
        """
        Starts a randomly selected minigame.

        Sets the current game state to "minigame" and initializes a new instance of a randomly chosen minigame.

        Parameters:
            None

        Returns:
            None
        """
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
    
    def menuUpdate(self):
        """
        Updates the game's menu state.

        This method is responsible for updating the game's menu state, including the rotation of the balloon and the start of the game when the SPACE key is pressed.

        Parameters:
            None

        Returns:
            None
        """
        # Auto-rotate the balloon
        if self.menu_rotation >= 360:
            self.menu_rotation = 0
        self.menu_rotation += 0.5
        
        # Start game with SPACE
        if pyxel.btnp(pyxel.KEY_SPACE):
            self.isMenu = False

    def menuDraw(self):
        """
        Draws the game's menu screen, including the 3D hot air balloon, 
        balloon rope/string, basket connection, basket parts, and title text.

        The menu screen is drawn with a light blue background and includes 
        game instructions and optional debug information.

        Parameters:
            None

        Returns:
            None
        """
        pyxel.cls(6)  # Light blue background like in your 3D code
        
        # Draw background sprite
        pyxel.blt(0, 0, 1, 0, 0, 256, 256)
        
        # Get center position for the 3D balloon
        imgX, imgY = self.getSpriteCenter()
        imgY += 10
        
        # Draw the 3D hot air balloon (adapted from your code)
        pyxel.blt(imgX, imgY, 0, 0, 0, 8, 8, colkey=0, scale=self.menu_scale+1, rotate=self.menu_rotation)

        # Draw balloon rope/string
        for i in range(3 * self.big):
            pyxel.blt(imgX, imgY, 0, 8, 0, 8, 8, colkey=0, scale=self.menu_scale+1, rotate=self.menu_rotation)
            imgY -= self.menu_yAxis / self.big
            imgX -= self.menu_xAxis / self.big

        # Draw basket connection
        pyxel.blt(imgX, imgY, 0, 0, 8, 8, 8, colkey=0, scale=self.menu_scale+1, rotate=self.menu_rotation)
        imgY -= self.menu_yAxis
        imgX -= self.menu_xAxis
        
        # Draw more rope
        for i in range(3 * self.big):
            pyxel.blt(imgX, imgY, 0, 8, 8, 8, 8, colkey=0, scale=self.menu_scale+1, rotate=self.menu_rotation)
            imgY -= self.menu_yAxis / self.big
            imgX -= self.menu_xAxis / self.big

        # Draw basket parts
        pyxel.blt(imgX, imgY, 0, 16, 8, 8, 8, colkey=0, scale=self.menu_scale+1, rotate=self.menu_rotation)
        imgY -= self.menu_yAxis
        imgX -= self.menu_xAxis

        # Draw balloon envelope (main balloon parts)
        balloon_parts = [
            (24, 0), (24, 8), (32, 0), (24, 8), (24, 0), (16, 8)
        ]
        
        for part_x, part_y in balloon_parts:
            pyxel.blt(imgX, imgY, 0, part_x, part_y, 8, 8, colkey=0, scale=self.menu_scale+6, rotate=self.menu_rotation)
            imgY -= self.menu_yAxis
            imgX -= self.menu_xAxis

        # Draw title text using sprites (MONGOL letters from your code)
        textRealScale = 0.8
        title_x = (pyxel.width - 5 * self.letterSize * textRealScale) // 2
        title_y = 20
        
        letter_positions = [(0, 16), (16, 16), (32, 16), (48, 16), (64, 16)]  # M O N G O
        for i, (letter_x, letter_y) in enumerate(letter_positions):
            pyxel.blt(title_x + i * self.letterSize * textRealScale, title_y, 0, 
                     letter_x, letter_y, 16, 16, scale=textRealScale, colkey=0 ,rotate=self.menu_rotation)
        
        # Game instructions
        text = "Hot Air Balloon Adventure"
        textX, textY = self.getTextCenter(text)
        textY += 8
        pyxel.text(textX, textY, text, pyxel.COLOR_RED)
        text = "Press SPACE to start"
        textX, textY = self.getTextCenter(text)
        textY += 16
        pyxel.text(textX, textY, text, pyxel.COLOR_RED)
        
        # Debug info (optional)
        #pyxel.text(0, 0, f"xAxis: {int(self.menu_xAxis*10)/10}, yAxis: {int(self.menu_yAxis*10)/10}, rot: {self.menu_rotation}, scale: {int(self.menu_scale*10)/10}", pyxel.COLOR_WHITE)

    def draw(self):
        """
        Draws the current game state, including the menu or the active game.

        If the game is in the menu state, it calls the menuDraw method.
        Otherwise, it draws the current game based on the game type.
        If a minigame is active, it calls the draw method of the minigame.

        Parameters:
            None

        Returns:
            None
        """
        if self.isMenu:
            self.menuDraw()
        else:
            if self.current_game == "balloon":
                pyxel.load("my_resource.pyxres")
                self.draw_balloon()
            elif self.minigame:
                self.minigame.draw()
    
    def draw_balloon(self):
        """
        Draws the hot air balloon game state, including the background, collected dots, 
        and the hot air balloon itself. It also displays a prompt to play a minigame 
        when the balloon is close to a dot.

        Parameters:
            None

        Returns:
            None
        """
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

    # Helper functions from your 3D code
    def getSpriteCenter(self):
        """
        Calculates the center position of a sprite on the Pyxel screen.

        Parameters:
            None

        Returns:
            tuple: A tuple containing the x and y coordinates of the sprite center.
        """
        return ((pyxel.width - 4) / 2), ((pyxel.height - 4) / 2)+50

    def getTextCenter(self,text):
        """
        Calculates the center position of a text on the Pyxel screen.

        Parameters:
            text (str): The text for which to calculate the center position.

        Returns:
            tuple: A tuple containing the x and y coordinates of the text center.
        """
        return ((pyxel.width - len(text) * 4)//2), ((pyxel.height - 4) / 2)+50


# Create and run the game
game = HotAirBalloonGame()