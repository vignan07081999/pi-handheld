import time
from PIL import ImageDraw
import config
from core.ui import Menu

class App:
    def __init__(self, display, input_manager):
        self.display = display
        self.input = input_manager
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

    def toggle_stopwatch(self):
        if self.stopwatch_running:
            self.stopwatch_running = False
            self.stopwatch_elapsed += time.time() - self.stopwatch_start
        else:
            self.stopwatch_running = True
            self.stopwatch_start = time.time()

    def update(self):
        if self.mode == 'menu':
            self.menu.update()

    def draw(self):
        draw = self.display.get_draw()
        draw.rectangle((0, 0, config.DISPLAY_WIDTH, config.DISPLAY_HEIGHT), fill=config.COLOR_BG)
        
        if self.mode == 'menu':
            self.menu.draw(draw)
            
        elif self.mode == 'stopwatch':
            current = self.stopwatch_elapsed
            if self.stopwatch_running:
                current += time.time() - self.stopwatch_start
            
            text = f"{current:.1f}s"
            # Centering text
            bbox = draw.textbbox((0, 0), text, font=self.menu.title_font)
            w = bbox[2] - bbox[0]
            draw.text(((config.DISPLAY_WIDTH - w)//2, 140), text, font=self.menu.title_font, fill=config.COLOR_TEXT)
            
            msg = "Press Select to Start/Stop"
            bbox2 = draw.textbbox((0, 0), msg)
            w2 = bbox2[2] - bbox2[0]
            draw.text(((config.DISPLAY_WIDTH - w2)//2, 200), msg, fill=(100, 100, 100))
            
        elif self.mode == 'ruler':
            # Draw Ruler
            ppmm = 7.87 # Calculated previously
            
            for mm in range(0, 40): # 40mm
                y = mm * ppmm
                if y > config.DISPLAY_HEIGHT: break
                
                length = 20 if mm % 10 == 0 else 10
                if mm % 5 == 0: length = 15
                
                draw.line((0, y, length, y), fill=config.COLOR_TEXT, width=2)
                draw.line((config.DISPLAY_WIDTH, y, config.DISPLAY_WIDTH - length, y), fill=config.COLOR_TEXT, width=2)
                
                if mm % 10 == 0:
                    draw.text((30, y - 5), f"{mm/10:.0f}cm", fill=config.COLOR_TEXT)

    def handle_input(self, event):
        if self.mode == 'menu':
            if event == 'left': self.menu.move_selection(-1)
            elif event == 'right': self.menu.move_selection(1)
            elif event == 'select': self.menu.select_current()
            elif event == 'back': return False # Exit App
            
        elif self.mode == 'stopwatch':
            if event == 'select': self.toggle_stopwatch()
            elif event == 'back': self.set_mode('menu')
            
        elif self.mode == 'ruler':
            if event == 'back': self.set_mode('menu')
            
        return True
