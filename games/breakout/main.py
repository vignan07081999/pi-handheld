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
        
        self.reset_game()

    def reset_game(self):
        self.paddle_x = (config.DISPLAY_WIDTH - self.paddle_w) // 2
        self.ball_pos = [config.DISPLAY_WIDTH // 2, config.DISPLAY_HEIGHT // 2]
        self.ball_vel = [4, -4] # Start moving up
        
        self.game_over = False
        self.score = 0
        
        # Generate Bricks
        self.bricks = []
        rows = 5
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
            self.ball_vel[0] = (hit_pos - 0.5) * 10 # -5 to 5
            
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
            
        # Win Condition
        if all(not b['active'] for b in self.bricks):
            self.game_over = True
            # Level up? For now just game over win.

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
        else:
            res = "YOU WIN" if all(not b['active'] for b in self.bricks) else "GAME OVER"
            draw.text((80, 100), res, fill=config.COLOR_WARNING)
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
