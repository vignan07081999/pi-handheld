import time
import math
import random
from PIL import ImageDraw
import config
from core import highscore

class App:
    def __init__(self, display, input_manager):
        self.display = display
        self.input = input_manager
        self.running = True
        self.game_over = False
        self.score = 0
        
        self.level = 1
        self.reset_game()

    def reset_game(self):
        self.level = 1
        self.score = 0
        self.reset_level()

    def reset_level(self):
        self.x = config.DISPLAY_WIDTH // 2
        self.y = 20
        self.vx = 0
        self.vy = 0
        self.angle = 0 # Degrees. 0 is Up.
        self.fuel = 100
        
        # Difficulty increases with level
        self.gravity = 0.05 + (self.level - 1) * 0.01
        self.thrust_power = 0.15
        
        self.landed = False
        self.crashed = False
        self.game_over = False
        
        # Terrain
        self.pad_w = max(15, 40 - (self.level - 1) * 5)
        self.pad_x = random.randint(20, config.DISPLAY_WIDTH - self.pad_w - 20)
        self.pad_y = config.DISPLAY_HEIGHT - 20
        
        self.last_input = None
        self.last_input_time = 0

    def update(self):
        if self.game_over: return

        # Physics
        self.vy += self.gravity
        self.x += self.vx
        self.y += self.vy
        
        # Wrap X
        if self.x < 0: self.x = config.DISPLAY_WIDTH
        if self.x > config.DISPLAY_WIDTH: self.x = 0
        
        # Collision
        # Check Pad
        if self.y >= self.pad_y - 10:
            if (self.pad_x <= self.x <= self.pad_x + self.pad_w and
                abs(self.vy) < 2.0 and abs(self.vx) < 1.0 and abs(self.angle) < 15):
                self.landed = True
                self.game_over = True
                self.score += int(self.fuel * 10) * self.level
                highscore.save_highscore('lander', self.score)
            else:
                self.crashed = True
                self.game_over = True

    def draw(self):
        draw = self.display.get_draw()
        draw.rectangle((0, 0, config.DISPLAY_WIDTH, config.DISPLAY_HEIGHT), fill="black")
        
        # Draw Terrain
        draw.line((0, self.pad_y, self.pad_x, self.pad_y), fill="white")
        draw.line((self.pad_x + self.pad_w, self.pad_y, config.DISPLAY_WIDTH, self.pad_y), fill="white")
        # Landing Pad
        draw.rectangle((self.pad_x, self.pad_y, self.pad_x + self.pad_w, self.pad_y + 5), fill="green")
        
        if not self.game_over:
            # Draw Lander
            rad = math.radians(self.angle - 90)
            
            tip_x = self.x + 10 * math.cos(rad)
            tip_y = self.y + 10 * math.sin(rad)
            
            left_rad = math.radians(self.angle - 90 + 140)
            left_x = self.x + 10 * math.cos(left_rad)
            left_y = self.y + 10 * math.sin(left_rad)
            
            right_rad = math.radians(self.angle - 90 - 140)
            right_x = self.x + 10 * math.cos(right_rad)
            right_y = self.y + 10 * math.sin(right_rad)
            
            draw.polygon([(tip_x, tip_y), (left_x, left_y), (right_x, right_y)], fill="white", outline="white")
            
            # HUD
            draw.text((10, 10), f"FUEL: {int(self.fuel)}", fill="white")
            draw.text((10, 25), f"ALT: {int(self.pad_y - self.y)}", fill="white")
            draw.text((config.DISPLAY_WIDTH - 60, 10), f"LVL: {self.level}", fill="white")
            draw.text((config.DISPLAY_WIDTH - 60, 25), f"VY: {self.vy:.1f}", fill="white")
            
            # Debug Input
            if self.last_input and time.time() - self.last_input_time < 0.5:
                draw.text((config.DISPLAY_WIDTH // 2, 50), self.last_input, fill="yellow")
            
        else:
            if self.landed:
                draw.text((60, 100), "SUCCESS!", fill="green")
                draw.text((70, 140), f"Score: {self.score}", fill="white")
                draw.text((50, 240), "Press Select for Next Level", fill=(100, 100, 100))
            else:
                draw.text((60, 100), "CRASHED!", fill="red")
                draw.text((70, 140), f"Score: {self.score}", fill="white")
                draw.text((50, 240), "Press Select to Restart", fill=(100, 100, 100))
                
            draw.text((60, 260), "Hold Back to Exit", fill=(100, 100, 100))

    def handle_input(self, event):
        if self.game_over:
            if event == 'select':
                if self.landed:
                    self.level += 1
                    self.reset_level()
                else:
                    self.reset_game()
            elif event == 'back':
                return False
            return True

        if event == 'left':
            self.angle -= 10
            self.last_input = "LEFT"
            self.last_input_time = time.time()
            print(f"DEBUG: Lander Left. Angle: {self.angle}")
        elif event == 'right':
            self.angle += 10
            self.last_input = "RIGHT"
            self.last_input_time = time.time()
            print(f"DEBUG: Lander Right. Angle: {self.angle}")
        elif event == 'select':
            # Thrust Burst
            if self.fuel > 0:
                self.fuel -= 5
                rad = math.radians(self.angle - 90)
                self.vx += self.thrust_power * math.cos(rad) * 5 # Burst multiplier
                self.vy += self.thrust_power * math.sin(rad) * 5
                self.last_input = "THRUST"
                self.last_input_time = time.time()
        elif event == 'back':
            return False
            
        return True
