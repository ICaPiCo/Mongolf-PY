import pyxel
import time
import random

class Clock:
    def __init__(self):
        pyxel.init(200, 200, title="Stop the Clock!", fps=60)
        self.target_time = random.randint(5, 20)
        self.start_time = time.time()
        self.current_time = 0.0
        self.stopped = False
        self.score = 0
        self.game_over = False
        self.fade_timer = 0
        self.show_result = False
        self.timer_faded = False
        self.fade_alpha = 1.0
        pyxel.run(self.update, self.draw)

    def update(self):
        if not self.stopped and not self.game_over:
            self.current_time = time.time() - self.start_time
            
            # Check if timer should start fading (after 1/3 of target time)
            fade_start_time = self.target_time / 3
            if self.current_time >= fade_start_time:
                if not self.timer_faded:
                    self.timer_faded = True
                
                # Calculate fade progress (from 1.0 to 0.0)
                fade_duration = self.target_time / 6  # Fade over 1/6 of target time
                fade_progress = (self.current_time - fade_start_time) / fade_duration
                self.fade_alpha = max(0.0, 1.0 - fade_progress)
            
            # Manual stop (spacebar)
            if pyxel.btnp(pyxel.KEY_SPACE):
                self.stopped = True
                self.show_result = True
                error = abs(self.current_time - self.target_time)
                self.score = max(0, 100 - int(error * 20))  # 100-0 points based on accuracy
                
        # Handle game over state and restart
        if self.stopped:
            self.fade_timer += 1
            if self.fade_timer > 180:  # Show result for 3 seconds
                if pyxel.btnp(pyxel.KEY_R):
                    self.restart_game()
                    
    def restart_game(self):
        """Reset the game state"""
        self.target_time = random.randint(5, 20)  # New random target
        self.start_time = time.time()
        self.current_time = 0.0
        self.stopped = False
        self.game_over = False
        self.fade_timer = 0
        self.show_result = False
        self.score = 0
        self.timer_faded = False

    def draw(self):
        pyxel.cls(1)  # Dark blue background
        
        if not self.stopped:
            # Draw running clock (faded after 1/3 of target time)
            time_str = f"{self.current_time:.2f}s"
            if self.timer_faded:
                # Use dither to make text disappear gradually
                pyxel.dither(0.3)  # Make text very faint
                pyxel.text(100 - len(time_str)*2, 90, time_str, 7)
                pyxel.dither(1.0)  # Reset dither
            else:
                # Normal timer
                pyxel.text(100 - len(time_str)*2, 90, time_str, 7)  # White
            
            # Instructions
            pyxel.text(60, 50, "Press SPACE to stop!", 10)
            
        else:
            # Show stopped time
            time_str = f"{self.current_time:.2f}s"
            pyxel.text(100 - len(time_str)*2, 70, time_str, 7)
            
            # Show result
            if self.show_result:
                error = abs(self.current_time - self.target_time)
                if error < 0.1:
                    result_text = "PERFECT!"
                    result_color = 11  # Light green
                elif error < 0.5:
                    result_text = "GREAT!"
                    result_color = 10  # Yellow
                elif error < 1.0:
                    result_text = "GOOD"
                    result_color = 9   # Orange
                else:
                    result_text = "TRY AGAIN"
                    result_color = 8   # Red
                    
                pyxel.text(100 - len(result_text)*2, 100, result_text, result_color)
                pyxel.text(80, 120, f"Error: {error:.2f}s", 7)
                
                # Show restart instruction after a delay
                if self.fade_timer > 60:
                    pyxel.text(70, 150, "Press R to restart", 6)
        
        # Target hint (always visible)
        pyxel.text(70, 30, f"Target: {self.target_time}s", 12)
        
        # Score
        pyxel.text(10, 10, f"Score: {self.score}", 7)
        
        # Instructions at bottom
        if not self.stopped:
            fade_time = self.target_time // 3
            pyxel.text(10, 180, f"Timer fades at {fade_time}s!", 6)