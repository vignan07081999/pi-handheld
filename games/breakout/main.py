import time
import random
import math
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
        self.paddle_w = 60 # Reset width
        self.paddle_x = (config.DISPLAY_WIDTH - self.paddle_w) // 2
        
        # Balls list for Multi-ball
        self.balls = []
        self._add_ball()
        
        self.powerups = []
        
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

    def _add_ball(self, x=None, y=None):
        if x is None: x = config.DISPLAY_WIDTH // 2
        if y is None: y = config.DISPLAY_HEIGHT // 2
        
        speed = 4 + (self.level - 1) * 0.5
        vel = [random.choice([-speed, speed]), -speed]
        
        self.balls.append({
            'pos': [x, y],
            'vel': vel
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

        # Update Balls
        for ball in self.balls:
            # Move
            ball['pos'][0] += ball['vel'][0]
            ball['pos'][1] += ball['vel'][1]
            
            # Wall Collisions
            if ball['pos'][0] <= 0 or ball['pos'][0] >= config.DISPLAY_WIDTH - self.ball_size:
                ball['vel'][0] *= -1
            if ball['pos'][1] <= 0:
                ball['vel'][1] *= -1
                
            # Paddle Collision
            paddle_y = config.DISPLAY_HEIGHT - 20
            if (paddle_y <= ball['pos'][1] + self.ball_size <= paddle_y + self.paddle_h and
                self.paddle_x <= ball['pos'][0] + self.ball_size/2 <= self.paddle_x + self.paddle_w):
                ball['vel'][1] *= -1
                # English
                hit_pos = (ball['pos'][0] - self.paddle_x) / self.paddle_w
                speed = math.hypot(ball['vel'][0], ball['vel'][1])
                angle_factor = (hit_pos - 0.5) * 2
                ball['vel'][0] = angle_factor * speed * 0.8
                # Normalize
                current_speed = math.hypot(ball['vel'][0], ball['vel'][1])
                if current_speed > 0:
                    ball['vel'][0] *= (speed / current_speed)
                    ball['vel'][1] *= (speed / current_speed)

            # Brick Collision
            ball_rect = [ball['pos'][0], ball['pos'][1], ball['pos'][0] + self.ball_size, ball['pos'][1] + self.ball_size]
            for brick in self.bricks:
                if brick['active']:
                    br = brick['rect']
                    if (ball_rect[0] < br[2] and ball_rect[2] > br[0] and
                        ball_rect[1] < br[3] and ball_rect[3] > br[1]):
                        brick['active'] = False
                        ball['vel'][1] *= -1
                        self.score += 10
                        
                        # Spawn Powerup (10%)
                        if random.random() < 0.1:
                            self._spawn_powerup((br[0] + br[2])//2, (br[1] + br[3])//2)
                        break

        # Remove dead balls
        self.balls = [b for b in self.balls if b['pos'][1] <= config.DISPLAY_HEIGHT]
        
        if not self.balls:
            self.game_over = True
            highscore.save_highscore('breakout', self.score)

        # Update Powerups
        for p in self.powerups:
            p['y'] += 2
            # Collision with paddle
            if (p['y'] + 10 >= config.DISPLAY_HEIGHT - 20 and
                self.paddle_x <= p['x'] <= self.paddle_x + self.paddle_w):
                self._activate_powerup(p['type'])
                p['active'] = False
        self.powerups = [p for p in self.powerups if p['active'] and p['y'] < config.DISPLAY_HEIGHT]

        # Win Condition
        if all(not b['active'] for b in self.bricks):
            self.level += 1
            self.reset_level()

    def _spawn_powerup(self, x, y):
        types = ['WIDER', 'SLOW', 'MULTI']
        self.powerups.append({
            'x': x,
            'y': y,
            'type': random.choice(types),
            'active': True
        })

    def _activate_powerup(self, p_type):
        if p_type == 'WIDER':
            self.paddle_w = min(100, self.paddle_w + 20)
            # Adjust x if it pushes off screen
            if self.paddle_x + self.paddle_w > config.DISPLAY_WIDTH:
                self.paddle_x = config.DISPLAY_WIDTH - self.paddle_w
        elif p_type == 'SLOW':
            for ball in self.balls:
                ball['vel'][0] *= 0.8
                ball['vel'][1] *= 0.8
        elif p_type == 'MULTI':
            # Add a ball at current paddle pos
            self._add_ball(self.paddle_x + self.paddle_w//2, config.DISPLAY_HEIGHT - 40)

    def draw(self):
        draw = self.display.get_draw()
        draw.rectangle((0, 0, config.DISPLAY_WIDTH, config.DISPLAY_HEIGHT), fill=config.COLOR_BG)
        
        if not self.game_over:
            # Draw Paddle
            draw.rectangle((self.paddle_x, config.DISPLAY_HEIGHT - 20, self.paddle_x + self.paddle_w, config.DISPLAY_HEIGHT - 20 + self.paddle_h), fill=config.COLOR_ACCENT)
            
            # Draw Balls
            for ball in self.balls:
                draw.ellipse((ball['pos'][0], ball['pos'][1], ball['pos'][0]+self.ball_size, ball['pos'][1]+self.ball_size), fill=config.COLOR_TEXT)
            
            # Draw Bricks
            for brick in self.bricks:
                if brick['active']:
                    draw.rectangle(brick['rect'], fill=brick['color'])
                    
            # Draw Powerups
            for p in self.powerups:
                color = "white"
                if p['type'] == 'WIDER': color = "green"
                elif p['type'] == 'SLOW': color = "blue"
                elif p['type'] == 'MULTI': color = "red"
                
                draw.ellipse((p['x']-5, p['y']-5, p['x']+5, p['y']+5), fill=color)
                draw.text((p['x']-3, p['y']-6), p['type'][0], fill="white", font=None) # Simple letter
                    
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
