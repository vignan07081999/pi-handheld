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
        if 'action' in item and item['action']:
            item['action']()

    def update(self):
        pass

    def draw(self, draw, target_image=None):
        pass

    def _draw_icon(self, draw, name, cx, cy, size=60, target_image=None):
        # Check for custom icon first
        import os
        
        # Check Config Mapping first
        key = name.lower().replace(" ", "_")
        if "]" in key: key = key.split("]")[-1].strip()
        
        icon_filename = config.ICONS.get(key, None)
        
        if not icon_filename:
            # Default lookup
            icon_filename = f"{key}.png"
            
        if not icon_filename.endswith('.png'):
            icon_filename += ".png"
            
        icon_path = f"assets/icons/{icon_filename}"
        
        if os.path.exists(icon_path) and target_image:
            try:
                icon = Image.open(icon_path).convert("RGBA")
                icon.thumbnail((size, size))
                w, h = icon.size
                target_image.paste(icon, (int(cx - w/2), int(cy - h/2)), icon)
                return
            except Exception as e:
                print(f"Error loading icon {icon_path}: {e}")

        # Fallback to procedural icons
        name = name.lower()
        color = config.COLOR_ACCENT
        
        # Scale drawing based on size (assuming 60 is base)
        s = size / 60.0
        
        if "setting" in name:
            draw.ellipse((cx-30*s, cy-30*s, cx+30*s, cy+30*s), outline=color, width=int(5*s))
            draw.ellipse((cx-10*s, cy-10*s, cx+10*s, cy+10*s), fill=color)
        elif "torch" in name:
            draw.ellipse((cx-25*s, cy-35*s, cx+25*s, cy+15*s), fill="yellow")
            draw.rectangle((cx-10*s, cy+15*s, cx+10*s, cy+35*s), fill="gray")
        elif "snake" in name:
            draw.arc((cx-20*s, cy-30*s, cx+20*s, cy), 180, 0, fill="green", width=int(5*s))
            draw.arc((cx-20*s, cy, cx+20*s, cy+30*s), 0, 180, fill="green", width=int(5*s))
        elif "pong" in name:
            draw.rectangle((cx-30*s, cy-20*s, cx-25*s, cy+20*s), fill="white")
            draw.rectangle((cx+25*s, cy-20*s, cx+30*s, cy+20*s), fill="white")
            draw.ellipse((cx-5*s, cy-5*s, cx+5*s, cy+5*s), fill="white")
        elif "racing" in name:
            draw.rectangle((cx-20*s, cy-10*s, cx+20*s, cy+10*s), fill="red")
            draw.ellipse((cx-15*s, cy+5*s, cx-5*s, cy+15*s), fill="white")
            draw.ellipse((cx+5*s, cy+5*s, cx+15*s, cy+15*s), fill="white")
        elif "breakout" in name:
            draw.rectangle((cx-30*s, cy-30*s, cx+30*s, cy-10*s), fill="orange")
            draw.rectangle((cx-10*s, cy+20*s, cx+10*s, cy+25*s), fill="white")
            draw.ellipse((cx-3*s, cy, cx+3*s, cy+6*s), fill="white")
        elif "lander" in name:
            draw.polygon([(cx, cy-20*s), (cx-20*s, cy+20*s), (cx+20*s, cy+20*s)], outline="white", width=int(3*s))
        elif "space" in name:
            draw.rectangle((cx-20*s, cy-10*s, cx+20*s, cy+10*s), fill="green")
            draw.rectangle((cx-10*s, cy-20*s, cx+10*s, cy-10*s), fill="green")
            draw.rectangle((cx-25*s, cy+10*s, cx-15*s, cy+20*s), fill="green")
            draw.rectangle((cx+15*s, cy+10*s, cx+25*s, cy+20*s), fill="green")
        elif "tools" in name:
            draw.rectangle((cx-5*s, cy-20*s, cx+5*s, cy+10*s), fill="gray")
            draw.rectangle((cx-15*s, cy-30*s, cx+15*s, cy-20*s), fill="gray")
        elif "games" in name:
            draw.rectangle((cx-25*s, cy-15*s, cx+25*s, cy+15*s), fill="purple")
            draw.ellipse((cx-15*s, cy, cx-5*s, cy+10*s), fill="black")
            draw.ellipse((cx+5*s, cy-5*s, cx+15*s, cy+5*s), fill="black")
        elif "apps" in name:
            draw.rectangle((cx-20*s, cy-20*s, cx-5*s, cy-5*s), fill="blue")
            draw.rectangle((cx+5*s, cy-20*s, cx+20*s, cy-5*s), fill="blue")
            draw.rectangle((cx-20*s, cy+5*s, cx-5*s, cy+20*s), fill="blue")
            draw.rectangle((cx+5*s, cy+5*s, cx+20*s, cy+20*s), fill="blue")
        else:
            draw.rectangle((cx-20*s, cy-20*s, cx+20*s, cy+20*s), outline=color, width=int(2*s))

class CarouselMenu(BaseMenu):
    def __init__(self, items, title="Menu"):
        super().__init__(items, title)
        self.scroll_offset = 0
        self.target_scroll_offset = 0
        self.scroll_accumulator = 0

    def move_selection(self, delta):
        # Accumulate steps to prevent too fast scrolling
        self.scroll_accumulator += delta
        
        # Only move every 2 steps
        if abs(self.scroll_accumulator) >= 2:
            move_dir = 1 if self.scroll_accumulator > 0 else -1
            self.scroll_accumulator = 0 
            
            self.selected_index = (self.selected_index + move_dir) % len(self.items)
            self.target_scroll_offset = self.selected_index * config.DISPLAY_WIDTH

    def update(self):
        # Snap to target (No animation for performance)
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
            self._draw_icon(draw, item['label'], icon_center_x, icon_center_y, size=60, target_image=target_image)
            
            # Draw Label
            label = item['label']
            bbox = draw.textbbox((0, 0), label, font=self.title_font)
            text_w = bbox[2] - bbox[0]
            
            text_x = icon_center_x - text_w // 2
            text_y = card_y + card_h - 40
            
            # Marquee if selected and too long
            if is_selected and text_w > card_w - 20:
                t = time.time()
                scroll_speed = 50
                scroll_dist = text_w - (card_w - 20) + 50
                period = scroll_dist / scroll_speed + 2
                phase = t % period
                
                if phase < 1: offset = 0
                elif phase < period - 1: offset = (phase - 1) * scroll_speed
                else: offset = scroll_dist - 50
                
                offset = min(offset, text_w - (card_w - 20))
                text_x = icon_center_x - (card_w - 20) // 2 - offset
                
            elif not is_selected and text_w > card_w - 20:
                 # Truncate
                 while text_w > card_w - 40 and len(label) > 3:
                     label = label[:-4] + "..."
                     bbox = draw.textbbox((0, 0), label, font=self.title_font)
                     text_w = bbox[2] - bbox[0]
                 text_x = icon_center_x - text_w // 2

            draw.text((text_x, text_y), label, font=self.title_font, fill=config.COLOR_TEXT)

class ListMenu(BaseMenu):
    def __init__(self, items, title="Menu"):
        super().__init__(items, title)
        self.visible_items = 5
        self.scroll_top = 0

    def move_selection(self, delta):
        self.selected_index = (self.selected_index + delta) % len(self.items)
        
        # Adjust scroll
        if self.selected_index < self.scroll_top:
            self.scroll_top = self.selected_index
        elif self.selected_index >= self.scroll_top + self.visible_items:
            self.scroll_top = self.selected_index - self.visible_items + 1

    def draw(self, draw, target_image=None):
        draw.rectangle((0, 0, config.DISPLAY_WIDTH, config.DISPLAY_HEIGHT), fill=config.COLOR_BG)
        
        # Title
        draw.rectangle((0, 0, config.DISPLAY_WIDTH, 40), fill=(30, 30, 30))
        draw.text((10, 5), self.title, font=self.title_font, fill=config.COLOR_ACCENT)
        
        # Items
        start_y = 50
        item_h = 40
        
        for i in range(self.visible_items):
            idx = self.scroll_top + i
            if idx >= len(self.items): break
            
            item = self.items[idx]
            y = start_y + i * item_h
            
            is_selected = (idx == self.selected_index)
            
            if is_selected:
                draw.rectangle((5, y, config.DISPLAY_WIDTH - 5, y + item_h - 5), fill=config.COLOR_ACCENT)
                text_color = "white"
            else:
                text_color = config.COLOR_TEXT
                
            # Draw Icon
            icon_size = 30
            icon_x = 25 # Center of icon area
            icon_y = y + item_h // 2
            
            self._draw_icon(draw, item['label'], icon_x, icon_y, size=icon_size, target_image=target_image)
            
            # Draw Text
            draw.text((50, y + 5), item['label'], font=self.font, fill=text_color)

# Alias for backward compatibility
Menu = ListMenu

class StatusBar:
    def __init__(self):
        self.height = 24
        self.font = load_font(12, bold=True)
        self.last_update = 0
        
    def draw(self, draw, target_image=None):
        # Draw Background
        draw.rectangle((0, 0, config.DISPLAY_WIDTH, self.height), fill="black")
        
        # Draw Time (Right)
        t_str = time.strftime("%H:%M")
        bbox = draw.textbbox((0, 0), t_str, font=self.font)
        w = bbox[2] - bbox[0]
        draw.text((config.DISPLAY_WIDTH - w - 5, 5), t_str, font=self.font, fill="white")
        
        # Draw WiFi (Left)
        # We can check config.WIFI_CONNECTED
        # For icon, we look for assets/icons/wifi_on.png or wifi_off.png
        wifi_icon_name = "wifi_on" if config.WIFI_CONNECTED else "wifi_off"
        self._draw_icon(draw, wifi_icon_name, 15, 12, size=16, target_image=target_image)
        
        # Draw Weather (Left, after WiFi)
        if config.WEATHER_TEMP:
            # Draw Temp
            temp_str = f"{config.WEATHER_TEMP}"
            draw.text((35, 5), temp_str, font=self.font, fill="white")
            
            # Draw Icon if available
            # We might need a mapping from OWM icon to our local icons
            # For now, just show temp
            pass

    def _draw_icon(self, draw, name, cx, cy, size=16, target_image=None):
        import os
        
        # Check Config Mapping first
        icon_name = config.ICONS.get(name.lower().replace(" ", "_"), None)
        
        if not icon_name:
            # Default lookup
            icon_name = name.lower().replace(" ", "_")
            if "]" in icon_name:
                icon_name = icon_name.split("]")[-1].strip()
            icon_name = f"{icon_name}.png"
            
        # Ensure extension
        if not icon_name.endswith('.png'):
            icon_name += ".png"
            
        icon_path = f"assets/icons/{icon_name}"
        
        if os.path.exists(icon_path) and target_image:
            try:
                icon = Image.open(icon_path).convert("RGBA")
                icon.thumbnail((size, size))
                w, h = icon.size
                target_image.paste(icon, (int(cx - w/2), int(cy - h/2)), icon)
            except:
                pass
        else:
            # Fallback
            if "wifi" in name:
                color = "green" if "on" in name else "red"
                draw.ellipse((cx-5, cy-5, cx+5, cy+5), fill=color)

class Keyboard:
    def __init__(self, on_done):
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
