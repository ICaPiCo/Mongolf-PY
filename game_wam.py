import pyxel
import time
import random

class Wam:
    def __init__(self):
        pyxel.init(200, 200, title="Whack-a-Mole!")
        pyxel.mouse(True)
        self.moles = [
            {"x": 40, "y": 50, "visible": 0, "points": 1},
            {"x": 100, "y": 50, "visible": 0, "points": 1},
            {"x": 160, "y": 50, "visible": 0, "points": 1},
            {"x": 40, "y": 100, "visible": 0, "points": 1},
            {"x": 100, "y": 100, "visible": 0, "points": 1},
            {"x": 160, "y": 100, "visible": 0, "points": 1},
        ]
        self.score = 0
        self.time_left = 60  # 60 seconds
        pyxel.run(self.update, self.draw)

    def update(self):
        # Randomly show moles
        if pyxel.frame_count % 30 == 0:  # Every half second
            mole = random.choice(self.moles)
            if mole["visible"] <= 0:
                mole["visible"] = 30  # Visible for 30 frames (~1 sec)

        # Update mole visibility
        for mole in self.moles:
            if mole["visible"] > 0:
                mole["visible"] -= 1

        # Check for mouse clicks
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            for mole in self.moles:
                if mole["visible"] > 0:
                    # Check if click hit the mole
                    dx = mole["x"] - pyxel.mouse_x
                    dy = mole["y"] - pyxel.mouse_y
                    if dx*dx + dy*dy < 100:  # 10px radius
                        self.score += mole["points"]
                        mole["visible"] = 0  # Hide immediately

        # Update timer
        self.time_left -= 1 / (pyxel.frame_count + 1)
        if self.time_left <= 0:
            print(f"Game Over! Final Score: {self.score}")
            pyxel.quit()

    def draw(self):
        pyxel.cls(0)
        
        # Draw holes (brown circles)
        for mole in self.moles:
            pyxel.circ(mole["x"], mole["y"] + 15, 15, 6)  # Hole
        
        # Draw moles (visible ones)
        for mole in self.moles:
            if mole["visible"] > 0:
                pyxel.circ(mole["x"], mole["y"], 10, 8)  # Mole
        
        # Draw UI
        pyxel.text(10, 10, f"Score: {self.score}", 7)
        pyxel.text(10, 20, f"Time: {int(self.time_left)}", 7)
        pyxel.text(10, 180, "Click the moles!", 7)

#Wam()