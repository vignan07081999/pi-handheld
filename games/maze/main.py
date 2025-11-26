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
        
        self.cell_size = 20
        self.cols = config.DISPLAY_WIDTH // self.cell_size
        self.rows = config.DISPLAY_HEIGHT // self.cell_size
        
        self.reset_game()

    def reset_game(self):
        self.maze = self._generate_maze(self.cols, self.rows)
        self.player_pos = [0, 0]
        self.end_pos = [self.cols - 1, self.rows - 1]
        self.game_over = False
        self.start_time = time.time()

    def _generate_maze(self, width, height):
        # Simple DFS Maze Generation
        maze = [[1 for _ in range(width)] for _ in range(height)] # 1 = Wall, 0 = Path
        
        stack = [(0, 0)]
        maze[0][0] = 0
        
        while stack:
            x, y = stack[-1]
            neighbors = []
            
            for dx, dy in [(0, -2), (0, 2), (-2, 0), (2, 0)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < width and 0 <= ny < height and maze[ny][nx] == 1:
                    neighbors.append((nx, ny, dx // 2, dy // 2))
            
            if neighbors:
                nx, ny, mx, my = random.choice(neighbors)
                maze[y + my][x + mx] = 0
                maze[ny][nx] = 0
                stack.append((nx, ny))
            else:
                stack.pop()
                
        # Ensure exit is reachable (it should be with DFS starting at 0,0)
        maze[height-1][width-1] = 0
        return maze

    def move(self, dx, dy):
        if self.game_over: return
        
        nx = self.player_pos[0] + dx
        ny = self.player_pos[1] + dy
        
        if 0 <= nx < self.cols and 0 <= ny < self.rows:
            if self.maze[ny][nx] == 0:
                self.player_pos = [nx, ny]
                
                if self.player_pos == self.end_pos:
                    self.game_over = True
                    self.score = int(time.time() - self.start_time)
                    # Lower score is better in maze usually, but let's invert it or just save time
                    # Let's save time as score (lower is better)
                    # But highscore manager assumes higher is better.
                    # Let's just save negative time? Or 1000 - time.
                    final_score = max(0, 1000 - int(time.time() - self.start_time))
                    highscore.save_highscore('maze', final_score)

    def update(self):
        pass

    def draw(self):
        draw = self.display.get_draw()
        draw.rectangle((0, 0, config.DISPLAY_WIDTH, config.DISPLAY_HEIGHT), fill=config.COLOR_BG)
        
        if not self.game_over:
            # Draw Maze
            for y in range(self.rows):
                for x in range(self.cols):
                    if self.maze[y][x] == 1:
                        draw.rectangle(
                            (x * self.cell_size, y * self.cell_size, (x + 1) * self.cell_size, (y + 1) * self.cell_size),
                            fill=(50, 50, 50)
                        )
            
            # Draw Player
            px, py = self.player_pos
            draw.rectangle(
                (px * self.cell_size + 4, py * self.cell_size + 4, (px + 1) * self.cell_size - 4, (py + 1) * self.cell_size - 4),
                fill=config.COLOR_ACCENT
            )
            
            # Draw Exit
            ex, ey = self.end_pos
            draw.rectangle(
                (ex * self.cell_size + 4, ey * self.cell_size + 4, (ex + 1) * self.cell_size - 4, (ey + 1) * self.cell_size - 4),
                fill=config.COLOR_WARNING
            )
        else:
            draw.text((60, 100), "MAZE CLEARED!", fill=config.COLOR_ACCENT)
            draw.text((70, 140), f"Time: {int(time.time() - self.start_time)}s", fill=config.COLOR_TEXT)
        deltas = [(1, 0), (0, 1), (-1, 0), (0, -1)]
        dx, dy = deltas[self.move_dir]
        self.move(dx, dy)
