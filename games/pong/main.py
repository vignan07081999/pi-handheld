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
        self.score_player = 0
        self.score_ai = 0
        
        self.paddle_width = 60
        self.paddle_height = 10
        self.ball_size = 10
        
        self.reset_game()

    def reset_game(self):
        self.player_x = (config.DISPLAY_WIDTH - self.paddle_width) // 2
        self.ai_x = (config.DISPLAY_WIDTH - self.paddle_width) // 2
        
        self.ball_pos = [config.DISPLAY_WIDTH // 2, config.DISPLAY_HEIGHT // 2]
        self.ball_vel = [4, 4]
        if random.random() > 0.5: self.ball_vel[0] *= -1
        if random.random() > 0.5: self.ball_vel[1] *= -1
        
        self.game_over = False

    def move_player(self, delta):
        self.player_x += delta
        self.player_x = max(0, min(config.DISPLAY_WIDTH - self.paddle_width, self.player_x))

    def update(self):
        if self.game_over: return

        # Move Ball
        self.ball_pos[0] += self.ball_vel[0]
        self.ball_pos[1] += self.ball_vel[1]
        
        # Wall Collisions (Left/Right)
        if self.ball_pos[0] <= 0 or self.ball_pos[0] >= config.DISPLAY_WIDTH - self.ball_size:
            self.ball_vel[0] *= -1
            
        # Paddle Collisions
        # Player (Bottom)
        player_y = config.DISPLAY_HEIGHT - 20
        if (player_y <= self.ball_pos[1] + self.ball_size <= player_y + self.paddle_height and
            self.player_x <= self.ball_pos[0] + self.ball_size/2 <= self.player_x + self.paddle_width):
            self.ball_vel[1] *= -1.1 # Speed up
            self.ball_pos[1] = player_y - self.ball_size - 1
            
        # AI (Top)
        ai_y = 20
        if (ai_y <= self.ball_pos[1] <= ai_y + self.paddle_height and
            self.ai_x <= self.ball_pos[0] + self.ball_size/2 <= self.ai_x + self.paddle_width):
            self.ball_vel[1] *= -1
            self.ball_pos[1] = ai_y + self.paddle_height + 1

        # Score / Reset
        if self.ball_pos[1] > config.DISPLAY_HEIGHT:
            self.score_ai += 1
            self.reset_ball()
        elif self.ball_pos[1] < 0:
            self.score_player += 1
            self.reset_ball()
            
        # AI Logic
        target_x = self.ball_pos[0] - self.paddle_width / 2
        if self.ai_x < target_x:
            self.ai_x += 3
        elif self.ai_x > target_x:
            self.ai_x -= 3
        self.ai_x = max(0, min(config.DISPLAY_WIDTH - self.paddle_width, self.ai_x))

    def reset_ball(self):
        self.ball_pos = [config.DISPLAY_WIDTH // 2, config.DISPLAY_HEIGHT // 2]
        self.ball_vel = [4, 4 * (1 if random.random() > 0.5 else -1)]
        
        if self.score_player >= 5 or self.score_ai >= 5:
            self.game_over = True
            if self.score_player > self.score_ai:
                highscore.save_highscore('pong', self.score_player)

    def draw(self):
        draw = self.display.get_draw()
        draw.rectangle((0, 0, config.DISPLAY_WIDTH, config.DISPLAY_HEIGHT), fill=config.COLOR_BG)
        
        if not self.game_over:
            # Draw Paddles
            draw.rectangle((self.player_x, config.DISPLAY_HEIGHT - 20, self.player_x + self.paddle_width, config.DISPLAY_HEIGHT - 20 + self.paddle_height), fill=config.COLOR_ACCENT)
            draw.rectangle((self.ai_x, 20, self.ai_x + self.paddle_width, 20 + self.paddle_height), fill=config.COLOR_WARNING)
            
            # Draw Ball
            draw.rectangle((self.ball_pos[0], self.ball_pos[1], self.ball_pos[0] + self.ball_size, self.ball_pos[1] + self.ball_size), fill=config.COLOR_TEXT)
            
            # Draw Scores
            draw.text((10, config.DISPLAY_HEIGHT // 2), str(self.score_player), fill=config.COLOR_ACCENT)
            draw.text((config.DISPLAY_WIDTH - 20, config.DISPLAY_HEIGHT // 2), str(self.score_ai), fill=config.COLOR_WARNING)
        else:
            res = "YOU WIN" if self.score_player > self.score_ai else "YOU LOSE"
            draw.text((80, 100), res, fill=config.COLOR_TEXT)
            draw.text((50, 240), "Press Select to Restart", fill=(100, 100, 100))
            draw.text((60, 260), "Hold Back to Exit", fill=(100, 100, 100))

    def stop(self):
        self.running = False

    def handle_input(self, event):
        if event == 'left': self.move_player(-15)
        elif event == 'right': self.move_player(15)
        elif event == 'select': 
            if self.game_over: self.reset_game()
