import time
from PIL import Image, ImageDraw, ImageFont
import config
import math

class Menu:
    def __init__(self, items, title="Menu"):
        self.items = items # List of dicts: {'label': 'Name', 'icon': 'path', 'action': callback}
        self.title = title
        self.selected_index = 0
        self.scroll_offset = 0
        self.target_scroll_offset = 0
        self.font = ImageFont.truetype("arial.ttf", config.FONT_SIZE_NORMAL) # Fallback if not found?
        self.title_font = ImageFont.truetype("arial.ttf", config.FONT_SIZE_TITLE)
        
        # Try loading a better font if available, or use default
        try:
            self.font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", config.FONT_SIZE_NORMAL)
            self.title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", config.FONT_SIZE_TITLE)
        except:
            pass # Use default PIL font or arial if on Windows

    def move_selection(self, delta):
        self.selected_index = (self.selected_index + delta) % len(self.items)
        # Target scroll keeps selected item in middle
        # Item height approx 40px
        item_height = 50
        # Center: 320/2 = 160. 
        # Position of selected item: index * height
        # Offset needed: (index * height) - (screen_center - item_half_height)
        self.target_scroll_offset = (self.selected_index * item_height) - (config.DISPLAY_HEIGHT / 2) + (item_height / 2)

    def select_current(self):
        item = self.items[self.selected_index]
        if 'action' in item and item['action']:
            item['action']()

    def update(self):
        # Smooth scroll animation
        diff = self.target_scroll_offset - self.scroll_offset
        if abs(diff) > 1:
            self.scroll_offset += diff * config.ANIMATION_SPEED
        else:
            self.scroll_offset = self.target_scroll_offset

    def draw(self, draw):
        # Draw Background
        draw.rectangle((0, 0, config.DISPLAY_WIDTH, config.DISPLAY_HEIGHT), fill=config.COLOR_BG)
        
        # Draw Title
        # draw.text((10, 10), self.title, font=self.title_font, fill=config.COLOR_ACCENT)
        
        item_height = 50
        start_y = -self.scroll_offset
        
        for i, item in enumerate(self.items):
            y = start_y + (i * item_height)
            
            # Optimization: Don't draw if off screen
            if y < -item_height or y > config.DISPLAY_HEIGHT:
                continue
                
            # Highlight selected
            if i == self.selected_index:
                # Draw selection box
                draw.rectangle((10, y, config.DISPLAY_WIDTH - 10, y + item_height - 5), fill=config.COLOR_HIGHLIGHT, outline=config.COLOR_ACCENT, width=2)
                color = config.COLOR_ACCENT
            else:
                color = config.COLOR_TEXT
            
            # Draw Text
            draw.text((20, y + 10), item['label'], font=self.font, fill=color)

class Keyboard:
    def __init__(self, on_done):
        self.on_done = on_done
        self.chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_ "
        self.selected_char_index = 0
        self.text = ""
        self.active = False
        self.font = ImageFont.truetype("arial.ttf", config.FONT_SIZE_LARGE)
        try:
            self.font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", config.FONT_SIZE_LARGE)
        except:
            pass

    def activate(self):
        self.active = True
        self.text = ""

    def move_selection(self, delta):
        self.selected_char_index = (self.selected_char_index + delta) % len(self.chars)

    def select_current(self):
        char = self.chars[self.selected_char_index]
        self.text += char

    def backspace(self):
        self.text = self.text[:-1]

    def finish(self):
        self.active = False
        self.on_done(self.text)

    def draw(self, draw):
        # Draw Overlay
        draw.rectangle((20, 60, config.DISPLAY_WIDTH - 20, config.DISPLAY_HEIGHT - 60), fill=(20, 20, 20), outline=config.COLOR_ACCENT)
        
        # Draw Current Text
        draw.text((40, 80), self.text + "|", font=self.font, fill=config.COLOR_TEXT)
        
        # Draw Wheel/Grid of characters
        # Simplified: Show current char big in middle, others small
        center_x = config.DISPLAY_WIDTH / 2
        center_y = config.DISPLAY_HEIGHT / 2 + 40
        
        # Current
        char = self.chars[self.selected_char_index]
        w, h = draw.textsize(char, font=self.font) if hasattr(draw, 'textsize') else (20, 30) # Pillow 10 deprecation
        draw.text((center_x - w/2, center_y - h/2), char, font=self.font, fill=config.COLOR_ACCENT)
        
        # Previous and Next
        prev_char = self.chars[(self.selected_char_index - 1) % len(self.chars)]
        next_char = self.chars[(self.selected_char_index + 1) % len(self.chars)]
        
        draw.text((center_x - 60, center_y), prev_char, font=self.font, fill=(100, 100, 100))
        draw.text((center_x + 60, center_y), next_char, font=self.font, fill=(100, 100, 100))

