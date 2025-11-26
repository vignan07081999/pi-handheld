import time
import random
from PIL import ImageDraw
import config
from core import highscore
from core.ui import Menu

class App:
    def __init__(self, display, input_manager):
        self.display = display
        self.input = input_manager
        self.running = True
        self.state = "menu_difficulty" # menu_difficulty, menu_points, game
        
        self.difficulty = "Medium"
        self.ai_speed_factor = 1.0
        
        self.menu_difficulty = Menu([
            {'label': 'Easy', 'action': lambda: self.set_difficulty('Easy', 0.6)},
            {'label': 'Medium', 'action': lambda: self.set_difficulty('Medium', 1.0)},
            {'label': 'Hard', 'action': lambda: self.set_difficulty('Hard', 1.5)},
            {'label': 'Impossible', 'action': lambda: self.set_difficulty('Impossible', 2.5)}
        ], title="Difficulty")
        
        self.menu_points = Menu([
            {'label': '3 Points', 'action': lambda: self.start_game(3)},
            {'label': '5 Points', 'action': lambda: self.start_game(5)},
            {'label': '10 Points', 'action': lambda: self.start_game(10)}
        ], title="Points")
        
        self.win_score = 5
        self.reset_game()

    def set_difficulty(self, name, factor):
        self.difficulty = name
        self.ai_speed_factor = factor
        self.state = "menu_points"

    def start_game(self, points):
        self.win_score = points
        self.state = "game"
        self.reset_game()

    def reset_game(self):
        self.paddle_w = 60
        self.paddle_h = 10
        self.ball_size = 10
        
        # Vertical Orientation
        # Player at Bottom
        self.player_x = (config.DISPLAY_WIDTH - self.paddle_w) // 2
        self.player_y = config.DISPLAY_HEIGHT - 20
        
        # AI at Top
        self.ai_x = (config.DISPLAY_WIDTH - self.paddle_w) // 2
        self.ai_y = 20
        
        self.ball_pos = [config.DISPLAY_WIDTH // 2, config.DISPLAY_HEIGHT // 2]
        self.ball_vel = [4, 4]
        if random.random() > 0.5: self.ball_vel[0] *= -1
        if random.random() > 0.5: self.ball_vel[1] *= -1
        
        self.current_speed_mult = 1.0
        self.score_player = 0
        self.score_ai = 0
        self.game_over = False

    def move_player(self, dx):
        if self.game_over: return
        self.player_x += dx
        self.player_x = max(0, min(config.DISPLAY_WIDTH - self.paddle_w, self.player_x))

    def update(self):
        if self.state == "menu_difficulty":
            self.menu_difficulty.update()
            return
        elif self.state == "menu_points":
            self.menu_points.update()
            return

        if self.game_over:
            return

        # Move Ball
        self.ball_pos[0] += self.ball_vel[0] * self.current_speed_mult
        self.ball_pos[1] += self.ball_vel[1] * self.current_speed_mult
        
        # Increase speed gradually
        self.current_speed_mult = min(2.5, self.current_speed_mult + 0.001)

        # Wall Collisions (Left/Right)
        if self.ball_pos[0] <= 0 or self.ball_pos[0] >= config.DISPLAY_WIDTH - self.ball_size:
            self.ball_vel[0] *= -1

        # Paddle Collisions
        # Player (Bottom)
        if (self.player_y <= self.ball_pos[1] + self.ball_size <= self.player_y + self.paddle_h and
            self.player_x <= self.ball_pos[0] + self.ball_size/2 <= self.player_x + self.paddle_w):
            self.ball_vel[1] *= -1
            self.ball_pos[1] = self.player_y - self.ball_size - 1
            
        # AI (Top)
        if (self.ai_y <= self.ball_pos[1] <= self.ai_y + self.paddle_h and
            self.ai_x <= self.ball_pos[0] + self.ball_size/2 <= self.ai_x + self.paddle_w):
            self.ball_vel[1] *= -1
            self.ball_pos[1] = self.ai_y + self.paddle_h + 1

        # Scoring
        if self.ball_pos[1] > config.DISPLAY_HEIGHT:
            self.score_ai += 1
            self._reset_ball()
        elif self.ball_pos[1] < 0:
            self.score_player += 1
            self._reset_ball()
            
        # AI Logic (Tracking with Speed Limit based on Difficulty)
        target_x = self.ball_pos[0] - self.paddle_w / 2
        
        # Base AI speed is 3.0 * speed_mult
        # Apply difficulty factor
        ai_speed = 3.0 * self.current_speed_mult * self.ai_speed_factor
        
        if self.ai_x < target_x:
            self.ai_x += ai_speed
        elif self.ai_x > target_x:
            self.ai_x -= ai_speed
        self.ai_x = max(0, min(config.DISPLAY_WIDTH - self.paddle_w, self.ai_x))
            
        if self.score_player >= self.win_score or self.score_ai >= self.win_score:
            self.game_over = True
            if self.score_player > self.score_ai:
                highscore.save_highscore('pong', self.score_player)

    def _reset_ball(self):
        self.ball_pos = [config.DISPLAY_WIDTH // 2, config.DISPLAY_HEIGHT // 2]
        self.ball_vel = [random.choice([-4, 4]), random.choice([-4, 4])]
        self.current_speed_mult = 1.0 # Reset speed

    def draw(self):
        draw = self.display.get_draw()
        draw.rectangle((0, 0, config.DISPLAY_WIDTH, config.DISPLAY_HEIGHT), fill=config.COLOR_BG)
        
        if self.state == "menu_difficulty":
            self.menu_difficulty.draw(draw, self.display.get_image())
            return
        elif self.state == "menu_points":
            self.menu_points.draw(draw, self.display.get_image())
            return

        if not self.game_over:
            # Draw Player Paddle (Bottom)
            draw.rectangle((self.player_x, self.player_y, self.player_x + self.paddle_w, self.player_y + self.paddle_h), fill=config.COLOR_ACCENT)
            
            # Draw AI Paddle (Top)
            draw.rectangle((self.ai_x, self.ai_y, self.ai_x + self.paddle_w, self.ai_y + self.paddle_h), fill=config.COLOR_WARNING)
            
            # Draw Ball
            draw.ellipse((self.ball_pos[0], self.ball_pos[1], self.ball_pos[0]+self.ball_size, self.ball_pos[1]+self.ball_size), fill=config.COLOR_TEXT)
            
            # Draw Scores
            draw.text((10, config.DISPLAY_HEIGHT // 2), str(self.score_player), fill=config.COLOR_ACCENT)
            draw.text((config.DISPLAY_WIDTH - 20, config.DISPLAY_HEIGHT // 2), str(self.score_ai), fill=config.COLOR_WARNING)
        else:
            res = "YOU WIN" if self.score_player > self.score_ai else "YOU LOSE"
            draw.text((80, 100), res, fill=config.COLOR_TEXT)
            draw.text((70, 140), f"{self.score_player} - {self.score_ai}", fill=config.COLOR_TEXT)
            draw.text((50, 240), "Press Select to Menu", fill=(100, 100, 100))
            draw.text((60, 260), "Hold Back to Exit", fill=(100, 100, 100))

    def handle_input(self, event):
        if self.state == "menu_difficulty":
            if event == 'left': self.menu_difficulty.move_selection(-1)
            elif event == 'right': self.menu_difficulty.move_selection(1)
            elif event == 'select': self.menu_difficulty.select_current()
            elif event == 'back': return False # Exit App
            
        elif self.state == "menu_points":
            if event == 'left': self.menu_points.move_selection(-1)
            elif event == 'right': self.menu_points.move_selection(1)
            elif event == 'select': self.menu_points.select_current()
            elif event == 'back': self.state = "menu_difficulty" # Back to difficulty
            
        elif self.state == "game":
            if event == 'left': self.move_player(-20) # Move Left
            elif event == 'right': self.move_player(20) # Move Right
            elif event == 'back': 
                self.state = "menu_difficulty" # Back to menu
                return True
                
        elif self.game_over:
            if event == 'select': self.state = "menu_difficulty"
            elif event == 'back': return False
        
        return True # Default consumed

    def stop(self):
        self.running = False
