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
        
        # Game State
        self.player_x = 0 # -1 to 1 (0 is center)
        self.speed = 0
        self.max_speed = 100
        self.track_pos = 0
        self.track_length = 10000
        self.curvature = 0
        self.target_curvature = 0
        self.curve_timer = 0
        
        # Obstacles: list of (z_pos, lane) where lane is -0.5, 0, 0.5
        self.obstacles = []
        self.next_obstacle_z = 500
        
        # Level System
        self.level = 1
        self.next_level_score = 50
        self.level_up_timer = 0
        
        self.reset_game()

    def reset_game(self):
        self.player_x = 0
        self.speed = 0
        self.track_pos = 0
        self.score = 0
        self.game_over = False
        self.obstacles = []
        self.next_obstacle_z = 200
        self.curvature = 0
        self.target_curvature = 0
        self.start_time = time.time()
        
        self.level = 1
        self.next_level_score = 50
        self.max_speed = 100
        self.level_up_timer = 0

    def update(self):
        if self.game_over: return

        # Auto-accelerate
        if self.speed < self.max_speed:
            self.speed += 1
            
        # Move forward
        self.track_pos += self.speed
        self.score = int(self.track_pos / 100)
        
        # Level Up Logic
        if self.score >= self.next_level_score:
            self.level += 1
            self.next_level_score += 50
            self.max_speed += 20
            self.level_up_timer = 60 # Show message for 60 frames
            
        if self.level_up_timer > 0:
            self.level_up_timer -= 1
        
        # Handle Curvature
        self.curve_timer += 1
        if self.curve_timer > 200: # Change curve every few seconds
            # Curvature increases with level
            intensity = 2 + (self.level * 0.5)
            self.target_curvature = random.uniform(-intensity, intensity)
            self.curve_timer = 0
            
        # Smoothly interpolate curvature
        self.curvature += (self.target_curvature - self.curvature) * 0.02
        
        # Apply curvature to player (centrifugal force)
        self.player_x -= self.curvature * (self.speed / self.max_speed) * 0.02
        
        # Clamp Player
        self.player_x = max(-1.2, min(1.2, self.player_x))
        
        # Spawn Obstacles
        if self.track_pos > self.next_obstacle_z:
            lane = random.choice([-0.6, 0, 0.6])
            self.obstacles.append({'z': self.track_pos + 2000, 'x': lane})
            # Obstacles get closer with level
            gap = max(300, 1500 - (self.level * 100))
            self.next_obstacle_z += random.randint(300, gap)
            
        # Clean Obstacles
        self.obstacles = [o for o in self.obstacles if o['z'] > self.track_pos - 100]
        
        # Check Collisions
        for o in self.obstacles:
            # Check if obstacle is close to player in Z
            dist_z = o['z'] - self.track_pos
            if 0 < dist_z < 100: # Passing through player
                # Check X overlap
                if abs(self.player_x - o['x']) < 0.4: # Car width approx 0.4
                    self.game_over = True
                    highscore.save_highscore('racing', self.score)

    def draw(self):
        draw = self.display.get_draw()
        
        # Sky
        draw.rectangle((0, 0, config.DISPLAY_WIDTH, config.DISPLAY_HEIGHT // 2), fill=(100, 149, 237)) # Cornflower Blue
        # Ground
        draw.rectangle((0, config.DISPLAY_HEIGHT // 2, config.DISPLAY_WIDTH, config.DISPLAY_HEIGHT), fill=(34, 139, 34)) # Forest Green
        
        if not self.game_over:
            # Draw Road (Pseudo-3D)
            horizon_y = config.DISPLAY_HEIGHT // 2
            num_segments = 20
            draw_dist = 2000
            segment_offset = self.track_pos % 100
            
            for i in range(num_segments, 0, -1):
                z = i * (draw_dist / num_segments) - segment_offset
                if z < 1: continue
                
                # Perspective Projection
                scale = 150 / z
                
                # Curvature effect on X
                curve_x = self.curvature * (z * z) / 100000
                
                screen_y = horizon_y + 4000 / z
                screen_w = 20000 / z
                screen_x = config.DISPLAY_WIDTH // 2 - curve_x * screen_w
                
                # Alternate colors
                color = (105, 105, 105) if ((self.track_pos + z) // 200) % 2 == 0 else (128, 128, 128)
                
                # Calculate Top and Bottom of segment
                z_far = z + 100
                z_near = z
                
                y_far = horizon_y + 4000 / z_far
                y_near = horizon_y + 4000 / z_near
                
                w_far = 20000 / z_far
                w_near = 20000 / z_near
                
                # Curve offsets
                curve_far = self.curvature * (z_far * z_far) / 100000
                curve_near = self.curvature * (z_near * z_near) / 100000
                
                x_far = config.DISPLAY_WIDTH // 2 - curve_far * w_far
                x_near = config.DISPLAY_WIDTH // 2 - curve_near * w_near
                
                # Draw Trapezoid
                points = [
                    (x_far - w_far/2, y_far),
                    (x_far + w_far/2, y_far),
                    (x_near + w_near/2, y_near),
                    (x_near - w_near/2, y_near)
                ]
                draw.polygon(points, fill=color)
                
                # Draw Rumble Strips
                rumble_color = (255, 0, 0) if ((self.track_pos + z) // 200) % 2 == 0 else (255, 255, 255)
                # Left Rumble
                draw.polygon([
                    (x_far - w_far/2 - w_far*0.1, y_far),
                    (x_far - w_far/2, y_far),
                    (x_near - w_near/2, y_near),
                    (x_near - w_near/2 - w_near*0.1, y_near)
                ], fill=rumble_color)
                # Right Rumble
                draw.polygon([
                    (x_far + w_far/2, y_far),
                    (x_far + w_far/2 + w_far*0.1, y_far),
                    (x_near + w_near/2 + w_near*0.1, y_near),
                    (x_near + w_near/2, y_near)
                ], fill=rumble_color)

            # Draw Obstacles (Painters algo: Back to Front)
            sorted_obstacles = sorted(self.obstacles, key=lambda o: o['z'], reverse=True)
            for o in sorted_obstacles:
                z = o['z'] - self.track_pos
                if z < 10 or z > 2000: continue
                
                y_screen = horizon_y + 4000 / z
                w_screen = 20000 / z
                
                curve_offset = self.curvature * (z * z) / 100000
                x_screen = config.DISPLAY_WIDTH // 2 - curve_offset * w_screen + o['x'] * w_screen
                
                # Draw Car Sprite (Rectangle)
                car_w = w_screen * 0.4
                car_h = car_w * 0.6
                draw.rectangle(
                    (x_screen - car_w/2, y_screen - car_h, x_screen + car_w/2, y_screen),
                    fill=(200, 50, 50)
                )

            # Draw Player Car
            car_y = config.DISPLAY_HEIGHT - 30
            car_w = 40
            car_h = 20
            player_screen_x = config.DISPLAY_WIDTH // 2 + self.player_x * (config.DISPLAY_WIDTH // 2)
            
            draw.rectangle(
                (player_screen_x - car_w/2, car_y - car_h, player_screen_x + car_w/2, car_y),
                fill=config.COLOR_ACCENT
            )
            
            # Draw Wheels
            draw.rectangle((player_screen_x - car_w/2 - 2, car_y - 8, player_screen_x - car_w/2 + 2, car_y), fill="black")
            draw.rectangle((player_screen_x + car_w/2 - 2, car_y - 8, player_screen_x + car_w/2 + 2, car_y), fill="black")
            
            # HUD
            draw.text((10, 10), f"SCORE: {self.score}", fill="white")
            draw.text((10, 30), f"SPEED: {int(self.speed)}", fill="white")
            draw.text((config.DISPLAY_WIDTH - 80, 10), f"LEVEL: {self.level}", fill="yellow")
            
            if self.level_up_timer > 0:
                if (self.level_up_timer // 5) % 2 == 0: # Blink
                    draw.text((config.DISPLAY_WIDTH // 2 - 40, 100), "LEVEL UP!", fill="yellow", font=None) # Need large font but don't have access to Menu font easily. Default is fine.

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
            self.player_x -= 0.2
        elif event == 'right':
            self.player_x += 0.2
        elif event == 'back':
            return False
            
        return True
