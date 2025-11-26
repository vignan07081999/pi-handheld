import time
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
        
        self.paddle_w = 60
        self.paddle_h = 10
        self.ball_size = 8
        
        self.level = 1
        self.reset_game()

    def reset_game(self):
        self.level = 1
        self.score = 0
        self.reset_level()

    def reset_level(self):
        self.paddle_x = (config.DISPLAY_WIDTH - self.paddle_w) // 2
        self.ball_pos = [config.DISPLAY_WIDTH // 2, config.DISPLAY_HEIGHT // 2]
        
        # Speed increases with level
        speed = 4 + (self.level - 1) * 0.5
        self.ball_vel = [speed, -speed]
        
        self.game_over = False
        
        # Generate Bricks
        self.bricks = []
        rows = 5 + (self.level // 2) # Add rows every 2 levels
        cols = 8
        brick_w = config.DISPLAY_WIDTH // cols
        brick_h = 15
        
        for r in range(rows):
            for c in range(cols):
                self.bricks.append({
                    'rect': [c * brick_w + 2, r * brick_h + 30, (c + 1) * brick_w - 2, (r + 1) * brick_h + 30 - 2],
                    'active': True,
                    'color': self._get_row_color(r)
                })

    def _get_row_color(self, row):
        colors = [
            (255, 0, 0),    # Red
            (255, 165, 0),  # Orange
            (255, 255, 0),  # Yellow
            (0, 255, 0),    # Green
            (0, 0, 255)     # Blue
        ]
        return colors[row % len(colors)]

    def move_paddle(self, dx):
        if self.game_over: return
        self.paddle_x += dx
        self.paddle_x = max(0, min(config.DISPLAY_WIDTH - self.paddle_w, self.paddle_x))

    def update(self):
        if self.game_over: return

        # Move Ball
        self.ball_pos[0] += self.ball_vel[0]
        self.ball_pos[1] += self.ball_vel[1]
        
        # Wall Collisions
        if self.ball_pos[0] <= 0 or self.ball_pos[0] >= config.DISPLAY_WIDTH - self.ball_size:
            self.ball_vel[0] *= -1
        if self.ball_pos[1] <= 0:
            self.ball_vel[1] *= -1
            
        # Paddle Collision
        paddle_y = config.DISPLAY_HEIGHT - 20
        if (paddle_y <= self.ball_pos[1] + self.ball_size <= paddle_y + self.paddle_h and
            self.paddle_x <= self.ball_pos[0] + self.ball_size/2 <= self.paddle_x + self.paddle_w):
            self.ball_vel[1] *= -1
            # Add some English based on hit position
            hit_pos = (self.ball_pos[0] - self.paddle_x) / self.paddle_w
            speed = math.hypot(self.ball_vel[0], self.ball_vel[1])
            angle_factor = (hit_pos - 0.5) * 2 # -1 to 1
            self.ball_vel[0] = angle_factor * speed * 0.8
            # Normalize speed
            current_speed = math.hypot(self.ball_vel[0], self.ball_vel[1])
            self.ball_vel[0] *= (speed / current_speed)
            self.ball_vel[1] *= (speed / current_speed)
            
        # Brick Collision
        ball_rect = [self.ball_pos[0], self.ball_pos[1], self.ball_pos[0] + self.ball_size, self.ball_pos[1] + self.ball_size]
        for brick in self.bricks:
            if brick['active']:
                br = brick['rect']
                if (ball_rect[0] < br[2] and ball_rect[2] > br[0] and
                    ball_rect[1] < br[3] and ball_rect[3] > br[1]):
                    brick['active'] = False
                    self.ball_vel[1] *= -1
                    self.score += 10
                    break # Only hit one brick per frame
                    
        # Game Over
        if self.ball_pos[1] > config.DISPLAY_HEIGHT:
            self.game_over = True
            highscore.save_highscore('breakout', self.score)
            
        # Win Condition (Level Up)
        if all(not b['active'] for b in self.bricks):
            self.level += 1
            self.reset_level()

    def draw(self):
        draw = self.display.get_draw()
        draw.rectangle((0, 0, config.DISPLAY_WIDTH, config.DISPLAY_HEIGHT), fill=config.COLOR_BG)
        
        if not self.game_over:
            # Draw Paddle
            draw.rectangle((self.paddle_x, config.DISPLAY_HEIGHT - 20, self.paddle_x + self.paddle_w, config.DISPLAY_HEIGHT - 20 + self.paddle_h), fill=config.COLOR_ACCENT)
            
            # Draw Ball
            draw.ellipse((self.ball_pos[0], self.ball_pos[1], self.ball_pos[0]+self.ball_size, self.ball_pos[1]+self.ball_size), fill=config.COLOR_TEXT)
            
            # Draw Bricks
            for brick in self.bricks:
                if brick['active']:
                    draw.rectangle(brick['rect'], fill=brick['color'])
                    
            # Score
            draw.text((10, 10), f"Score: {self.score}", fill="white")
            draw.text((config.DISPLAY_WIDTH - 60, 10), f"Level: {self.level}", fill="white")
        else:
            draw.text((60, 100), "GAME OVER", fill=config.COLOR_WARNING)
            draw.text((70, 140), f"Score: {self.score}", fill=config.COLOR_TEXT)
            draw.text((50, 240), "Press Select to Restart", fill=(100, 100, 100))
            draw.text((60, 260), "Hold Back to Exit", fill=(100, 100, 100))

    def handle_input(self, event):
        if self.game_over:
            if event == 'select':
                self.reset_game()
            elif event == 'back':
                return False
            return True

        if event == 'left':
            self.move_paddle(-20)
        elif event == 'right':
            self.move_paddle(20)
        elif event == 'back':
            return False
            
        return True
