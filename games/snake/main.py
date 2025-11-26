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
        self.state = "menu" # menu, game, game_over
        self.wall_mode = True # True = Walled, False = Infinite
        
        # Grid settings
        self.cell_size = 10
        self.cols = config.DISPLAY_WIDTH // self.cell_size
        self.rows = config.DISPLAY_HEIGHT // self.cell_size
        
        self.menu = Menu([
            {'label': 'Walled Mode', 'action': lambda: self.start_game(True)},
            {'label': 'Infinite Mode', 'action': lambda: self.start_game(False)}
        ], title="Snake Mode")
        
        self.score = 0
        self.snake = []
        self.food = (0, 0)
        self.direction = (0, -1)
        self.last_move_dir = (0, -1) # Direction of the last frame

    def start_game(self, wall_mode):
        self.wall_mode = wall_mode
        self.state = "game"
        self.reset_game()
        
        # Setup Game Controls
        self.input.callbacks['left'] = []
        self.input.callbacks['right'] = []
        self.input.callbacks['select'] = []
        self.input.callbacks['back'] = []
        
        self.input.on('left', self.turn_left)
        self.input.on('right', self.turn_right)
        self.input.on('back', self.stop)

    def reset_game(self):
        # Head is last. Moving Up (0, -1).
        self.snake = [(10, 12), (10, 11), (10, 10)] 
        self.direction = (0, -1)
        self.last_move_dir = (0, -1)
        self.food = self._spawn_food()
        self.score = 0
        self.speed = 0.15

    def _spawn_food(self):
        while True:
            x = random.randint(0, self.cols - 1)
            y = random.randint(0, self.rows - 1)
            if (x, y) not in self.snake:
                return (x, y)

    def turn_left(self):
        # Rotate 90 CCW from CURRENT PLANNED direction
        # But to prevent 180s in one frame, we should base it on LAST MOVED direction?
        # If we base on last_move_dir, we can queue one turn per frame.
        # Let's try: New dir is 90 deg from last_move_dir.
        # (x, y) -> (y, -x)
        new_dir = (self.last_move_dir[1], -self.last_move_dir[0])
        self.direction = new_dir

    def turn_right(self):
        # Rotate 90 CW from LAST MOVED direction
        # (x, y) -> (-y, x)
        new_dir = (-self.last_move_dir[1], self.last_move_dir[0])
        self.direction = new_dir

    def update(self):
        if self.state != "game":
            return

        # Update last_move_dir to what we are about to use
        self.last_move_dir = self.direction
        
        head = self.snake[-1]
        new_head = (head[0] + self.direction[0], head[1] + self.direction[1])
        
        # Handle Walls
        if self.wall_mode:
            if (new_head[0] < 0 or new_head[0] >= self.cols or
                new_head[1] < 0 or new_head[1] >= self.rows):
                self.game_over()
                return
        else:
            # Wrap around
            new_head = (new_head[0] % self.cols, new_head[1] % self.rows)

        # Check Self Collision
        if new_head in self.snake:
            self.game_over()
            return

        self.snake.append(new_head)
        
        if new_head == self.food:
            self.score += 1
            self.food = self._spawn_food()
            self.speed = max(0.05, self.speed * 0.98)
        else:
            self.snake.pop(0)

    def game_over(self):
        self.state = "game_over"
        highscore.save_highscore('snake', self.score)
        # Reset controls for Game Over screen
        self.input.callbacks['left'] = []
        self.input.callbacks['right'] = []
        self.input.callbacks['select'] = []
        self.input.callbacks['back'] = []
        
        self.input.on('select', lambda: self.set_menu_mode()) # Restart goes to menu? Or restart same mode?
        # Let's go to menu to pick mode again
        self.input.on('back', self.stop)

    def set_menu_mode(self):
        self.state = "menu"
        self.input.callbacks['left'] = []
        self.input.callbacks['right'] = []
        self.input.callbacks['select'] = []
        self.input.callbacks['back'] = []
        
        self.input.on('left', lambda: self.menu.move_selection(-1))
        self.input.on('right', lambda: self.menu.move_selection(1))
        self.input.on('select', self.menu.select_current)
        self.input.on('back', self.stop)

    def draw(self):
        draw = self.display.get_draw()
        draw.rectangle((0, 0, config.DISPLAY_WIDTH, config.DISPLAY_HEIGHT), fill=config.COLOR_BG)
        
        if self.state == "menu":
            self.menu.update()
            self.menu.draw(draw)
            
        elif self.state == "game":
            # Draw Snake
            for segment in self.snake:
                x, y = segment
                draw.rectangle(
                    (x * self.cell_size, y * self.cell_size, (x + 1) * self.cell_size - 1, (y + 1) * self.cell_size - 1),
                    fill=config.COLOR_ACCENT
                )
            
            # Draw Food
            fx, fy = self.food
            draw.rectangle(
                (fx * self.cell_size, fy * self.cell_size, (fx + 1) * self.cell_size - 1, (fy + 1) * self.cell_size - 1),
                fill=config.COLOR_WARNING
            )
            
            # Draw Score
            draw.text((5, 5), f"Score: {self.score}", fill=config.COLOR_TEXT)
            
        elif self.state == "game_over":
            draw.text((60, 100), "GAME OVER", font=self.display.draw.font, fill=config.COLOR_WARNING)
            draw.text((70, 140), f"Score: {self.score}", fill=config.COLOR_TEXT)
            draw.text((40, 180), f"High: {highscore.get_highscore('snake')}", fill=config.COLOR_ACCENT)
            draw.text((50, 240), "Press Select to Menu", fill=(100, 100, 100))
            draw.text((60, 260), "Hold Back to Exit", fill=(100, 100, 100))

    def stop(self):
        self.running = False

    def run(self):
        self.set_menu_mode()
        
        while self.running:
            self.update()
            self.draw()
            self.display.show()
            
            if self.input.simulate:
                import pygame
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False
                    self.input.handle_pygame_event(event)
            
            time.sleep(self.speed if self.state == "game" else 0.05)
