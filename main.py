import pyxel
import random
import game_clock, game_coin, game_golf, game_shooter, game_tag, game_wam

class HotAirBalloonGame:
    def __init__(self):
        """
        Initializes the game state.
        
        Prints initialization messages, loads resources, sets up the Pyxel window,
        and initializes the game state.
        """
        print("[INIT] Initializing game...")
        pyxel.init(256, 256, title="Hot Air Balloon Adventure", display_scale=3)
        pyxel.load("my_resource.pyxres")
        
        self.current_game = "balloon"
        self.minigame = None

        self.balloon_x = pyxel.width // 2
        self.balloon_y = (pyxel.height // 2) + 50

        self.bg_x = 0
        self.bg_y = 0

        pyxel.mouse(True)

        self.dot_positions = [
            (126, 165), (120, 139), (116, 123), 
            (50, 38), (109, 181), (184, 160)
        ]
        print(f"[INIT] Balloon starting position: ({self.balloon_x}, {self.balloon_y})")

    def update(self):
        """
        Updates the game state.
        
        Checks the current game state and runs either the hot air balloon update
        or the minigame update.
        """
        
        print(f"[UPDATE] Current game state: {self.current_game}")
        if self.current_game == "balloon":
            self.update_balloon()
        elif self.minigame:
            print("[UPDATE] Running minigame update")
            self.minigame.update()

    def update_balloon(self):
        """
        Updates the position of the hot air balloon and checks for interactions.
        
        This method handles user input to move the balloon position on the screen
        and checks if the balloon is near any predefined dot positions. If the 
        balloon is near a dot and the space key is pressed, a minigame is triggered.
        """

        print(f"[BALLOON] Position: ({self.balloon_x}, {self.balloon_y})")
        # Movement
        if pyxel.btn(pyxel.KEY_UP):
            self.balloon_y -= 1
            print(" - Moving UP")
        if pyxel.btn(pyxel.KEY_DOWN):
            self.balloon_y += 1
            print(" - Moving DOWN")
        if pyxel.btn(pyxel.KEY_LEFT):
            self.balloon_x -= 1
            print(" - Moving LEFT")
        if pyxel.btn(pyxel.KEY_RIGHT):
            self.balloon_x += 1
            print(" - Moving RIGHT")

        near_dot = False
        for x, y in self.dot_positions:
            dist = abs(self.balloon_x - x) + abs(self.balloon_y - y)
            print(f" - Checking dot at ({x}, {y}) → dist = {dist}")
            if dist < 4:
                near_dot = True

        if near_dot:
            print(" - NEAR DOT")
        else:
            print(" - NOT NEAR ANY DOT")

        if pyxel.btnp(pyxel.KEY_SPACE):
            print(" - SPACE KEY PRESSED")
        else:
            print(" - SPACE NOT PRESSED")

        if near_dot and pyxel.btnp(pyxel.KEY_SPACE):
            print(" >>> Triggering minigame...")
            self.start_minigame()

    def start_minigame(self):
        """
        Selects and starts a random minigame.
        """
        print("[MINIGAME] Selecting and starting minigame...")
        self.current_game = "minigame"
        minigame_classes = [
            game_clock.Clock,
            game_coin.Coin,
            game_golf.Golf,
            game_shooter.Shooter,
            game_tag.Tag,
            game_wam.Wam
        ]
        MinigameClass = random.choice(minigame_classes)
        print(f"[MINIGAME] Chosen class: {MinigameClass.__name__}")
        self.minigame = MinigameClass()

    def draw(self):
        """
        Renders the current game state on the screen.

        Depending on the current game state, it either draws the hot air balloon
        scene or delegates the drawing to the currently active minigame.
        """

        if self.current_game == "balloon":
            self.draw_balloon()
        elif self.minigame:
            self.minigame.draw()

    def draw_balloon(self):
        """
        Renders the hot air balloon scene.

        This includes drawing the background image, the dots that trigger
        minigames, and the hot air balloon itself.

        If the balloon is near a dot, it also displays a message prompting
        the user to press the space bar to start a minigame.
        """
        pyxel.cls(0)

        pyxel.blt(
            self.bg_x, self.bg_y,
            1, 0, 0, 256, 256,
            colkey=0, scale=1
        )

        for x, y in self.dot_positions:
            pyxel.circ(x, y, 2, pyxel.COLOR_YELLOW)

        pyxel.circ(self.balloon_x, self.balloon_y, 4, pyxel.COLOR_RED)

        near_dot = any(
            abs(self.balloon_x - x) + abs(self.balloon_y - y) < 4
            for x, y in self.dot_positions
        )
        if near_dot:
            msg = "Want to play a minigame? (SPACE)"
            pyxel.text((pyxel.width - len(msg) * 4) // 2, 10, msg, pyxel.COLOR_WHITE)
            print(" - [DRAW] Showing minigame prompt")

game = HotAirBalloonGame()
pyxel.run(game.update, game.draw)
