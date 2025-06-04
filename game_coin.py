import pyxel
import random  # <-- ADDED

class Coin:
    def __init__(self):
        """
        Initializes a new instance of the Coin class.
        
        Sets up the initial game state, including the coin positions, player position, score, and time left.
        
        No parameters are taken, and no value is returned.
        """
        self.coins = [[random.randint(0, 600), random.randint(0, 400)] for _ in range(10)]
        self.score = 0
        self.time_left = 30
        self.player_x = pyxel.width//2
        self.player_y = pyxel.height//2 
        self.done = False

    def update(self):
        """
        Updates the game state based on user input and game logic.

        Checks for keyboard input to move the player, collision with coins, and updates the score and time left accordingly.

        No parameters are taken, and no value is returned.
        """
        if pyxel.btn(pyxel.KEY_LEFT):  # <-- CHANGED to btn() for smooth movement
            self.player_x -= 3  # <-- ADDED self.
        if pyxel.btn(pyxel.KEY_RIGHT):
            self.player_x += 3
        if pyxel.btn(pyxel.KEY_UP):
            self.player_y -= 3
        if pyxel.btn(pyxel.KEY_DOWN):
            self.player_y += 3
        if pyxel.btnp(pyxel.KEY_A):
            self.done = True

        # Coin collision check
        for coin in self.coins[:]:
            if abs(self.player_x - coin[0]) < 5 and abs(self.player_y - coin[1]) < 5:
                self.coins.remove(coin)
                self.score += 1
                # Add new coin to keep total at 10
                self.coins.append([random.randint(0, pyxel.width), random.randint(0, pyxel.height)])

        self.time_left -= 1 / (pyxel.frame_count + 1)  # <-- ADDED pyxel.frame_count
        if self.time_left <= 0:
            print("Game Over! Score:", self.score)
            pyxel.quit()

    def draw(self):
        """
        Draws the current state of the game, including coins, the player, and the game UI.

        No parameters are taken, and no value is returned.
        """
        pyxel.cls(0)  # Clear screen
        # Draw coins
        for x, y in self.coins:
            pyxel.circ(x, y, 2, pyxel.COLOR_YELLOW)
        # Draw player (simple circle)
        pyxel.circ(self.player_x, self.player_y, 5, pyxel.COLOR_RED)
        # Draw UI
        pyxel.text(10, 10, f"Score: {self.score}", 7)
        pyxel.text(10, 20, f"Time: {int(self.time_left)}", 7)

#Coin()