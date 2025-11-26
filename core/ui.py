import time
from PIL import Image, ImageDraw, ImageFont
import config
import math

def load_font(size, bold=False):
    fonts = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf" if bold else "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
        "arial.ttf"
    ]
    
    for font_path in fonts:
        try:
            return ImageFont.truetype(font_path, size)
        except OSError:
            continue
    
    # Fallback to default
    print(f"Warning: No fonts found. Using default.")
    return ImageFont.load_default()

class BaseMenu:
    def __init__(self, items, title="Menu"):
        self.items = items 
        self.title = title
        self.selected_index = 0
        self.font = load_font(config.FONT_SIZE_NORMAL)
        self.title_font = load_font(config.FONT_SIZE_TITLE - 4, bold=True) # Smaller title

    def move_selection(self, delta):
        self.selected_index = (self.selected_index + delta) % len(self.items)

    def select_current(self):
        item = self.items[self.selected_index]
        self.on_done = on_done
        self.active = False
        self.text = ""
        self.caps = False
        self.selected_index = 0 # Linear index
        
        self.font = load_font(config.FONT_SIZE_NORMAL)
        self.font_large = load_font(config.FONT_SIZE_LARGE, bold=True)
        
        self.layout_lower = [
            list("1234567890"),
            list("qwertyuiop"),
            list("asdfghjkl"),
            list("zxcvbnm,."),
            ["SPACE", "DEL", "DONE", "CAPS"]
        ]
        
        self.layout_upper = [
            list("1234567890"),
            list("QWERTYUIOP"),
            list("ASDFGHJKL"),
            list("ZXCVBNM,."),
            ["SPACE", "DEL", "DONE", "CAPS"]
        ]
        
        self.current_layout = self.layout_lower
        self._flatten_layout()

    def _flatten_layout(self):
        self.flat_keys = []
        for r, row in enumerate(self.current_layout):
            for c, key in enumerate(row):
                self.flat_keys.append({'key': key, 'r': r, 'c': c})

    def activate(self):
        self.active = True
        self.text = ""
        self.selected_index = 0

    def move_selection(self, delta):
        self.selected_index = (self.selected_index + delta) % len(self.flat_keys)

    def select_current(self):
        key = self.flat_keys[self.selected_index]['key']
        
        if key == "SPACE":
            self.text += " "
        elif key == "DEL":
            self.text = self.text[:-1]
        elif key == "DONE":
            self.active = False
            self.on_done(self.text)
        elif key == "CAPS":
            self.caps = not self.caps
            self.current_layout = self.layout_upper if self.caps else self.layout_lower
            # Re-flatten but try to keep index relative? 
            # Or just reset index? Keeping index is safer if layouts match shape.
            # They do match shape exactly.
            self._flatten_layout()
        else:
            self.text += key

    def draw(self, draw):
        draw.rectangle((0, 0, config.DISPLAY_WIDTH, config.DISPLAY_HEIGHT), fill=(20, 20, 20))
        draw.rectangle((10, 10, config.DISPLAY_WIDTH - 10, 50), fill="white")
        draw.text((15, 15), self.text + "|", font=self.font, fill="black")
        
        start_y = 60
        key_width = config.DISPLAY_WIDTH // 10
        key_height = 30
        
        # Draw all keys
        for i, item in enumerate(self.flat_keys):
            r = item['r']
            c = item['c']
            key = item['key']
            
            # Calculate Position
            row_len = len(self.current_layout[r])
            row_width = row_len * key_width
            start_x = (config.DISPLAY_WIDTH - row_width) // 2
            
            if r == len(self.current_layout) - 1: # Bottom row
                key_width_special = config.DISPLAY_WIDTH // 4
                start_x = 0
                x = c * key_width_special
                w = key_width_special
            else:
                x = start_x + c * key_width
                w = key_width
            
            y = start_y + r * key_height
            
            # Highlight
            if i == self.selected_index:
                draw.rectangle((x + 2, y + 2, x + w - 2, y + key_height - 2), fill=config.COLOR_ACCENT)
                color = "white"
            else:
                draw.rectangle((x + 2, y + 2, x + w - 2, y + key_height - 2), outline=(100, 100, 100))
                color = (200, 200, 200)
            
            font = self.font
            if len(key) > 1: font = load_font(12)
            
            bbox = draw.textbbox((0, 0), key, font=font)
            text_w = bbox[2] - bbox[0]
            text_h = bbox[3] - bbox[1]
            
            draw.text((x + (w - text_w) // 2, y + (key_height - text_h) // 2 - 2), key, font=font, fill=color)
