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
        
        self.reset_game()

    def reset_game(self):
        self.player_x = config.DISPLAY_WIDTH // 2
        self.player_y = config.DISPLAY_HEIGHT - 20
        self.player_w = 20
        self.player_h = 10
        
        self.bullets = []
        self.aliens = []
        self.alien_rows = 4
        self.alien_cols = 6
        self.alien_w = 15
        self.alien_h = 10
        self.alien_dir = 1 # 1: Right, -1: Left
        self.alien_speed = 2
        self.alien_drop_timer = 0
        
        # Spawn Aliens
        start_x = 20
        start_y = 30
        for r in range(self.alien_rows):
            for c in range(self.alien_cols):
                self.aliens.append({
                    'x': start_x + c * (self.alien_w + 10),
                    'y': start_y + r * (self.alien_h + 10),
                    'active': True
                })
        
        self.game_over = False
        self.score = 0
        self.win = False

    def update(self):
        if self.game_over: return

        # Move Bullets
        for b in self.bullets:
            b['y'] -= 5
        self.bullets = [b for b in self.bullets if b['y'] > 0]
        
        # Move Aliens
        move_down = False
        # Check edges
        left_edge = min(a['x'] for a in self.aliens if a['active']) if any(a['active'] for a in self.aliens) else 0
        right_edge = max(a['x'] + self.alien_w for a in self.aliens if a['active']) if any(a['active'] for a in self.aliens) else 0
        
        if right_edge >= config.DISPLAY_WIDTH - 5 and self.alien_dir == 1:
            self.alien_dir = -1
            move_down = True
        elif left_edge <= 5 and self.alien_dir == -1:
            self.alien_dir = 1
            move_down = True
            
        for a in self.aliens:
            if a['active']:
                a['x'] += self.alien_dir * self.alien_speed
                if move_down:
                    a['y'] += 10
                    if a['y'] + self.alien_h >= self.player_y:
                        self.game_over = True # Aliens reached player
                        
        # Collision: Bullet vs Alien
        for b in self.bullets:
            for a in self.aliens:
                if a['active']:
                    if (a['x'] <= b['x'] <= a['x'] + self.alien_w and
                        a['y'] <= b['y'] <= a['y'] + self.alien_h):
                        a['active'] = False
                        b['y'] = -10 # Remove bullet
                        self.score += 10
                        # Increase speed slightly?
                        pass
                        
        # Win Condition
        if all(not a['active'] for a in self.aliens):
            self.game_over = True
            self.win = True
            highscore.save_highscore('space_invaders', self.score)

    def draw(self):
        draw = self.display.get_draw()
        draw.rectangle((0, 0, config.DISPLAY_WIDTH, config.DISPLAY_HEIGHT), fill="black")
        
        if not self.game_over:
            # Draw Player
            draw.rectangle((self.player_x - self.player_w//2, self.player_y, self.player_x + self.player_w//2, self.player_y + self.player_h), fill="green")
            # Turret
            draw.rectangle((self.player_x - 2, self.player_y - 5, self.player_x + 2, self.player_y), fill="green")
            
            # Draw Aliens
            for a in self.aliens:
                if a['active']:
                    draw.rectangle((a['x'], a['y'], a['x'] + self.alien_w, a['y'] + self.alien_h), fill="red")
            
            # Draw Bullets
            for b in self.bullets:
                draw.rectangle((b['x'] - 1, b['y'], b['x'] + 1, b['y'] + 5), fill="yellow")
                
            # Score
            draw.text((10, 10), f"SCORE: {self.score}", fill="white")
        else:
            res = "YOU WIN" if self.win else "GAME OVER"
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
            self.player_x -= 10
            self.player_x = max(self.player_w//2, self.player_x)
        elif event == 'right':
            self.player_x += 10
            self.player_x = min(config.DISPLAY_WIDTH - self.player_w//2, self.player_x)
        elif event == 'select':
            # Shoot
            self.bullets.append({'x': self.player_x, 'y': self.player_y - 5})
        elif event == 'back':
            return False
            
        return True
