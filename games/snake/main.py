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
        
        # Grid settings
        self.cell_size = 10
        self.cols = config.DISPLAY_WIDTH // self.cell_size
        self.rows = config.DISPLAY_HEIGHT // self.cell_size
        
        self.reset_game()

    def reset_game(self):
        # Head is last. Moving Up (0, -1).
        # Body should be below head.
        # Head: (10, 10). Body: (10, 11), (10, 12).
        self.snake = [(10, 12), (10, 11), (10, 10)] 
        self.direction = (0, -1) # Moving Up
        self.food = self._spawn_food()
        self.score = 0
        self.game_over = False
        self.speed = 0.15

    def _spawn_food(self):
        while True:
            x = random.randint(0, self.cols - 1)
            y = random.randint(0, self.rows - 1)
            if (x, y) not in self.snake:
                return (x, y)

    def turn_left(self):
        # Rotate direction vector 90 deg CCW
        # (x, y) -> (y, -x)
        self.direction = (self.direction[1], -self.direction[0])

    def turn_right(self):
        # Rotate direction vector 90 deg CW
        # (x, y) -> (-y, x)
        self.direction = (-self.direction[1], self.direction[0])

    def update(self):
        if self.game_over:
            return

        head = self.snake[-1]
        new_head = (head[0] + self.direction[0], head[1] + self.direction[1])
        
        # Check Collision
        if (new_head[0] < 0 or new_head[0] >= self.cols or
            new_head[1] < 0 or new_head[1] >= self.rows or
            new_head in self.snake):
            self.game_over = True
            highscore.save_highscore('snake', self.score)
            return

        self.snake.append(new_head)
        
        if new_head == self.food:
            self.score += 1
            self.food = self._spawn_food()
            self.speed = max(0.05, self.speed * 0.98) # Increase speed
        else:
            self.snake.pop(0)

    def draw(self):
        draw = self.display.get_draw()
        draw.rectangle((0, 0, config.DISPLAY_WIDTH, config.DISPLAY_HEIGHT), fill=config.COLOR_BG)
        
        if not self.game_over:
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
        else:
            # Game Over Screen
            draw.text((60, 100), "GAME OVER", font=self.display.draw.font, fill=config.COLOR_WARNING) # Use default font if needed
            draw.text((70, 140), f"Score: {self.score}", fill=config.COLOR_TEXT)
            draw.text((40, 180), f"High: {highscore.get_highscore('snake')}", fill=config.COLOR_ACCENT)
            draw.text((50, 240), "Press Select to Restart", fill=(100, 100, 100))
            draw.text((60, 260), "Hold Back to Exit", fill=(100, 100, 100))

    def stop(self):
        self.running = False

    def run(self):
        self.input.on('left', self.turn_left)
        self.input.on('right', self.turn_right)
        self.input.on('select', lambda: self.reset_game() if self.game_over else None)
        self.input.on('back', self.stop)
        
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
            
            time.sleep(self.speed)
