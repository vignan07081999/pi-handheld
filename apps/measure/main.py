import time
from PIL import ImageDraw
import config
from core.ui import Menu

class App:
    def __init__(self, display, input_manager):
        self.display = display
        self.input = input_manager
        self.running = True
        self.mode = "menu" # menu, stopwatch, ruler
        
        self.menu = Menu([
            {'label': 'Stopwatch', 'action': lambda: self.set_mode('stopwatch')},
            {'label': 'Ruler', 'action': lambda: self.set_mode('ruler')}
        ], title="Measure")
        
        self.stopwatch_start = 0
        self.stopwatch_running = False
        self.stopwatch_elapsed = 0

    def set_mode(self, mode):
        self.mode = mode
        # Reset controls for the new mode
        self.input.callbacks['left'] = []
        self.input.callbacks['right'] = []
        self.input.callbacks['select'] = []
        
        if mode == 'stopwatch':
            self.input.on('select', self.toggle_stopwatch)
            self.input.on('back', lambda: self.set_mode('menu')) # Short press back to menu? 
            # Wait, 'back' is long press usually. 
            # We can use 'left' to go back or specific button logic.
            # Let's use 'back' (long press) to exit app, so we need another way to go back to menu?
            # Maybe 'left' on stopwatch? Or just 'back' exits the whole app.
            # Let's make 'back' go to menu if in tool, and exit app if in menu.
            self.input.on('back', self.go_back)
            
        elif mode == 'ruler':
            self.input.on('back', self.go_back)
            
        elif mode == 'menu':
            self.input.on('left', lambda: self.menu.move_selection(-1))
            self.input.on('right', lambda: self.menu.move_selection(1))
            self.input.on('select', self.menu.select_current)
            self.input.on('back', self.stop)

    def go_back(self):
        if self.mode == 'menu':
            self.stop()
        else:
            self.set_mode('menu')

    def toggle_stopwatch(self):
        if self.stopwatch_running:
            self.stopwatch_running = False
            self.stopwatch_elapsed += time.time() - self.stopwatch_start
        else:
            self.stopwatch_running = True
            self.stopwatch_start = time.time()

    def stop(self):
        self.running = False

    def run(self):
        self.set_mode('menu')
        
        while self.running:
            draw = self.display.get_draw()
            draw.rectangle((0, 0, config.DISPLAY_WIDTH, config.DISPLAY_HEIGHT), fill=config.COLOR_BG)
            
            if self.mode == 'menu':
                self.menu.update()
                self.menu.draw(draw)
                
            elif self.mode == 'stopwatch':
                current = self.stopwatch_elapsed
                if self.stopwatch_running:
                    current += time.time() - self.stopwatch_start
                
                text = f"{current:.1f}s"
                draw.text((80, 140), text, font=self.menu.title_font, fill=config.COLOR_TEXT)
                draw.text((60, 200), "Press to Start/Stop", fill=(100, 100, 100))
                
            elif self.mode == 'ruler':
                # Draw Ruler
                # 240px width. Assuming 2 inch screen width? No, 2 inch is diagonal.
                # 240x320. 
                # If 2.0 inch diagonal 4:3, width is approx 1.2 inches = 30mm.
                # PPI = sqrt(240^2 + 320^2) / 2 = 200 PPI.
                # Pixels per mm = 200 / 25.4 = 7.87 px/mm.
                ppmm = 7.87
                
                for mm in range(0, 40): # 40mm
                    y = mm * ppmm
                    if y > config.DISPLAY_HEIGHT: break
                    
                    length = 20 if mm % 10 == 0 else 10
                    if mm % 5 == 0: length = 15
                    
                    draw.line((0, y, length, y), fill=config.COLOR_TEXT, width=2)
                    draw.line((config.DISPLAY_WIDTH, y, config.DISPLAY_WIDTH - length, y), fill=config.COLOR_TEXT, width=2)
                    
                    if mm % 10 == 0:
                        draw.text((30, y - 5), f"{mm/10:.0f}cm", fill=config.COLOR_TEXT)

            self.display.show()
            
            if self.input.simulate:
                import pygame
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False
                    self.input.handle_pygame_event(event)
            
            time.sleep(0.05)
