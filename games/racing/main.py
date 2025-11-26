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

    def update(self):
        if self.game_over: return

        # Auto-accelerate
        if self.speed < self.max_speed:
            self.speed += 1
            
        # Move forward
        self.track_pos += self.speed
        self.score = int(self.track_pos / 100)
        
        # Handle Curvature
        self.curve_timer += 1
        if self.curve_timer > 200: # Change curve every few seconds
            self.target_curvature = random.uniform(-2, 2)
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
            self.next_obstacle_z += random.randint(500, 1500)
            
        # Clean Obstacles
        self.obstacles = [o for o in self.obstacles if o['z'] > self.track_pos - 100]
        
        # Check Collisions
        player_z = self.track_pos + 100 # Player is effectively at z=100 relative to camera? 
        # Actually, let's say camera is at track_pos, player is at track_pos + offset.
        # Let's simplify: World Z coordinates.
        # Camera is at self.track_pos.
        # Player is fixed on screen, but logically at self.track_pos.
        # Obstacles are at absolute Z.
        
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
            # Project segments
            # We draw from back to front? No, front to back is easier for painters algo? 
            # Actually back to front is better to overlay.
            
            # Horizon Y
            horizon_y = config.DISPLAY_HEIGHT // 2
            
            # Draw Road Segments
            # We simulate strips.
            # Z distance from camera.
            # y = horizon_y + (screen_height / z) * scale
            # w = (road_width / z) * scale
            
            # We'll draw 10 segments
            num_segments = 20
            draw_dist = 2000
            
            # Current segment offset
            segment_offset = self.track_pos % 100
            
            # Accumulate X offset for curvature
            dx = 0
            
            for i in range(num_segments, 0, -1):
                z = i * (draw_dist / num_segments) - segment_offset
                if z < 1: continue
                
                # Perspective Projection
                scale = 150 / z
                
                # Curvature effect on X
                # dx += self.curvature * (z / 1000) # Simple skew
                # Actually, curvature accumulates with Z
                curve_x = self.curvature * (z * z) / 100000
                
                screen_y = horizon_y + 4000 / z
                screen_w = 20000 / z
                screen_x = config.DISPLAY_WIDTH // 2 - curve_x * screen_w
                
                # Alternate colors
                color = (105, 105, 105) if ((self.track_pos + z) // 200) % 2 == 0 else (128, 128, 128)
                grass_color = (34, 139, 34) if ((self.track_pos + z) // 200) % 2 == 0 else (50, 205, 50)
                
                # Draw Grass Strip (Full width)
                # draw.rectangle((0, screen_y, config.DISPLAY_WIDTH, screen_y + 10), fill=grass_color)
                
                # Draw Road Strip
                # We need trapezoids.
                # Calculate next (closer) segment for trapezoid
                # But simple rectangles work for retro feel if dense enough.
                # Let's use lines or rects.
                
                # Better: Calculate Top and Bottom of segment
                z_far = z + 100
                z_near = z
                
                y_far = horizon_y + 4000 / z_far
                y_near = horizon_y + 4000 / z_near
                
                scale_far = 150 / z_far
                scale_near = 150 / z_near
                
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
            # Sort obstacles by Z (descending)
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
            # Fixed at bottom center (visually), but moves relative to road via player_x
            # Actually, we move the road (camera), so player is visually center?
            # No, user asked for "cart is controller using the knob".
            # Usually in these games, the car moves Left/Right on screen.
            
            car_y = config.DISPLAY_HEIGHT - 30
            car_w = 40
            car_h = 20
            
            # Player X on screen
            # 0 -> Center. -1 -> Left Edge of Road.
            # Road width at bottom is approx display width.
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
            # print(f"DEBUG: Left. Pos: {self.player_x}")
        elif event == 'right':
            self.player_x += 0.2
            # print(f"DEBUG: Right. Pos: {self.player_x}")
        elif event == 'back':
            return False
            
        return True
