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

class Menu:
    def __init__(self, items, title="Menu"):
        self.items = items 
        self.title = title
        self.selected_index = 0
        self.scroll_offset = 0
        self.target_scroll_offset = 0
        
        self.font = load_font(config.FONT_SIZE_NORMAL)
        self.title_font = load_font(config.FONT_SIZE_TITLE, bold=True)

    def move_selection(self, delta):
        # Accumulate steps to prevent too fast scrolling
        if not hasattr(self, 'scroll_accumulator'):
            self.scroll_accumulator = 0
            
        self.scroll_accumulator += delta
        
        # Only move every 2 steps
        if abs(self.scroll_accumulator) >= 2:
            move_dir = 1 if self.scroll_accumulator > 0 else -1
            self.scroll_accumulator = 0 
            
            self.selected_index = (self.selected_index + move_dir) % len(self.items)
            self.target_scroll_offset = self.selected_index * config.DISPLAY_WIDTH

    def select_current(self):
        item = self.items[self.selected_index]
        if 'action' in item and item['action']:
            item['action']()

    def update(self):
        diff = self.target_scroll_offset - self.scroll_offset
        if abs(diff) > 1:
            self.scroll_offset += diff * 0.2 # Faster animation
        else:
            self.scroll_offset = self.target_scroll_offset

    def draw(self, draw, target_image=None):
        draw.rectangle((0, 0, config.DISPLAY_WIDTH, config.DISPLAY_HEIGHT), fill=config.COLOR_BG)
        
        # Draw Carousel Items
        for i, item in enumerate(self.items):
            x = (i * config.DISPLAY_WIDTH) - self.scroll_offset
            
            # Optimization: Only draw if visible
            if x < -config.DISPLAY_WIDTH or x > config.DISPLAY_WIDTH:
                continue
                
            margin = 10
            card_x = x + margin
            card_y = margin
            card_w = config.DISPLAY_WIDTH - 2 * margin
            card_h = config.DISPLAY_HEIGHT - 2 * margin
            
            is_selected = (i == self.selected_index)
            bg_color = (30, 30, 30) if not is_selected else (50, 50, 50)
            outline_color = config.COLOR_ACCENT if is_selected else (100, 100, 100)
            
            draw.rectangle((card_x, card_y, card_x + card_w, card_y + card_h), fill=bg_color, outline=outline_color, width=3)
            
            # Draw Icon
            icon_center_x = card_x + card_w // 2
            icon_center_y = card_y + card_h // 2 - 20
            self._draw_icon(draw, item['label'], icon_center_x, icon_center_y, target_image)
            
            # Draw Label
            label = item['label']
            bbox = draw.textbbox((0, 0), label, font=self.title_font)
            text_w = bbox[2] - bbox[0]
            draw.text((icon_center_x - text_w // 2, card_y + card_h - 40), label, font=self.title_font, fill=config.COLOR_TEXT)

    def _draw_icon(self, draw, name, cx, cy, target_image=None):
        # Check for custom icon first
        import os
        icon_name = name.lower().replace(" ", "_")
        icon_path = f"assets/icons/{icon_name}.png"
        
        if os.path.exists(icon_path) and target_image:
            try:
                icon = Image.open(icon_path).convert("RGBA")
                icon.thumbnail((60, 60))
                w, h = icon.size
                # Paste centered
                target_image.paste(icon, (int(cx - w/2), int(cy - h/2)), icon)
                return
            except Exception as e:
                print(f"Error loading icon {icon_path}: {e}")

        # Fallback to procedural icons
        name = name.lower()
        color = config.COLOR_ACCENT
        
        if "setting" in name:
            # Gear
            draw.ellipse((cx-30, cy-30, cx+30, cy+30), outline=color, width=5)
            draw.ellipse((cx-10, cy-10, cx+10, cy+10), fill=color)
        elif "torch" in name:
            # Lightbulb / Circle
            draw.ellipse((cx-25, cy-35, cx+25, cy+15), fill="yellow")
            draw.rectangle((cx-10, cy+15, cx+10, cy+35), fill="gray")
        elif "snake" in name:
            # S shape
            draw.arc((cx-20, cy-30, cx+20, cy), 180, 0, fill="green", width=5)
            draw.arc((cx-20, cy, cx+20, cy+30), 0, 180, fill="green", width=5)
        elif "pong" in name:
            # Paddles and Ball
            draw.rectangle((cx-30, cy-20, cx-25, cy+20), fill="white")
            draw.rectangle((cx+25, cy-20, cx+30, cy+20), fill="white")
            draw.ellipse((cx-5, cy-5, cx+5, cy+5), fill="white")
        elif "racing" in name:
            # Car
            draw.rectangle((cx-20, cy-10, cx+20, cy+10), fill="red")
            draw.ellipse((cx-15, cy+5, cx-5, cy+15), fill="white")
            draw.ellipse((cx+5, cy+5, cx+15, cy+15), fill="white")
        elif "breakout" in name:
            # Bricks
            draw.rectangle((cx-30, cy-30, cx+30, cy-10), fill="orange")
            draw.rectangle((cx-10, cy+20, cx+10, cy+25), fill="white") # Paddle
            draw.ellipse((cx-3, cy, cx+3, cy+6), fill="white") # Ball
        elif "lander" in name:
            # Triangle
            draw.polygon([(cx, cy-20), (cx-20, cy+20), (cx+20, cy+20)], outline="white", width=3)
        elif "space" in name:
            # Alien
            draw.rectangle((cx-20, cy-10, cx+20, cy+10), fill="green")
            draw.rectangle((cx-10, cy-20, cx+10, cy-10), fill="green")
            draw.rectangle((cx-25, cy+10, cx-15, cy+20), fill="green")
            draw.rectangle((cx+15, cy+10, cx+25, cy+20), fill="green")
        else:
            # Default Box
            draw.rectangle((cx-20, cy-20, cx+20, cy+20), outline=color, width=2)

class Keyboard:
    def __init__(self, on_done):
        self.on_done = on_done
        self.active = False
        self.text = ""
        self.caps = False
        self.selected_row = 0
        self.selected_col = 0
        
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

    def activate(self):
        self.active = True
        self.text = ""
        self.selected_row = 0
        self.selected_col = 0

    def move_selection(self, delta):
        # Flatten navigation? Or Row/Col?
        # With a knob, flat navigation is easier.
        # Count total items
        total_items = sum(len(row) for row in self.current_layout)
        
        # Calculate current flat index
        current_flat = 0
        for r in range(self.selected_row):
            current_flat += len(self.current_layout[r])
        current_flat += self.selected_col
        
        # Apply delta
        current_flat = (current_flat + delta) % total_items
        
        # Convert back to Row/Col
        temp = 0
        for r, row in enumerate(self.current_layout):
            if current_flat < temp + len(row):
                self.selected_row = r
                self.selected_col = current_flat - temp
                break
            temp += len(row)

    def select_current(self):
        key = self.current_layout[self.selected_row][self.selected_col]
        
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
        else:
            self.text += key

    def draw(self, draw):
        # Draw Background
        draw.rectangle((0, 0, config.DISPLAY_WIDTH, config.DISPLAY_HEIGHT), fill=(20, 20, 20))
        
        # Draw Text Input Area
        draw.rectangle((10, 10, config.DISPLAY_WIDTH - 10, 50), fill="white")
        draw.text((15, 15), self.text + "|", font=self.font, fill="black")
        
        # Draw Keyboard Grid
        start_y = 60
        key_width = config.DISPLAY_WIDTH // 10
        key_height = 30
        
        for r, row in enumerate(self.current_layout):
            row_width = len(row) * key_width
            start_x = (config.DISPLAY_WIDTH - row_width) // 2
            
            # Special handling for last row (buttons)
            if r == len(self.current_layout) - 1:
                key_width_special = config.DISPLAY_WIDTH // 4
                start_x = 0
            
            for c, key in enumerate(row):
                if r == len(self.current_layout) - 1:
                    x = c * key_width_special
                    w = key_width_special
                else:
                    x = start_x + c * key_width
                    w = key_width
                
                y = start_y + r * key_height
                
                # Highlight Selection
                if r == self.selected_row and c == self.selected_col:
                    draw.rectangle((x + 2, y + 2, x + w - 2, y + key_height - 2), fill=config.COLOR_ACCENT)
                    color = "white"
                else:
                    draw.rectangle((x + 2, y + 2, x + w - 2, y + key_height - 2), outline=(100, 100, 100))
                    color = (200, 200, 200)
                
                # Draw Key Label
                # Center text
                # Use simple centering estimation
                font = self.font
                if len(key) > 1: font = load_font(12) # Smaller for special keys
                
                # text_w, text_h = draw.textsize(key, font=font) # Deprecated
                # Use bbox
                bbox = draw.textbbox((0, 0), key, font=font)
                text_w = bbox[2] - bbox[0]
                text_h = bbox[3] - bbox[1]
                
                draw.text((x + (w - text_w) // 2, y + (key_height - text_h) // 2 - 2), key, font=font, fill=color)

