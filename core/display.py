import time
import sys
import os
from PIL import Image, ImageDraw, ImageFont
import config

# Try to import hardware libraries
try:
    try:
        import ST7789
    except ImportError:
        import st7789 as ST7789
    import RPi.GPIO as GPIO
    HARDWARE_AVAILABLE = True
except ImportError as e:
    HARDWARE_AVAILABLE = False
    print(f"Hardware libraries not found ({e}). Running in Simulation Mode.")

class DisplayManager:
    def __init__(self, simulate=False):
        self.width = config.DISPLAY_WIDTH
        self.height = config.DISPLAY_HEIGHT
        self.simulate = simulate or not HARDWARE_AVAILABLE
        
        # Create a blank image for drawing
        self.image = Image.new("RGB", (self.width, self.height), config.COLOR_BG)
        self.draw = ImageDraw.Draw(self.image)
        
        if not self.simulate:
            self._init_hardware()
        else:
            self._init_simulation()

    def _init_hardware(self):
        print("Initializing ST7789 Display...")
        
        # Explicitly turn on Backlight first
        try:
            GPIO.setup(config.PIN_DISPLAY_BL, GPIO.OUT)
            GPIO.output(config.PIN_DISPLAY_BL, GPIO.HIGH)
        except:
            pass

        # CS=0 for CE0 (GPIO8), CS=1 for CE1 (GPIO7)
        # We assume standard SPI0 based on pins.
        spi_cs = 0 if config.PIN_DISPLAY_CS == 8 else 1
        
        self.disp = ST7789.ST7789(
            port=0,
            cs=spi_cs, # Pass SPI CE Index, not Pin Number
            dc=config.PIN_DISPLAY_DC,
            rst=config.PIN_DISPLAY_RST,
            backlight=config.PIN_DISPLAY_BL,
            rotation=config.DISPLAY_ROTATION,
            spi_speed_hz=config.DISPLAY_BAUDRATE
        )
        self.disp._spi.mode = 3
        self.disp.begin()
        self.disp.clear()

    def _init_simulation(self):
        print("Initializing Pygame Simulation...")
        import pygame
        pygame.init()
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Pi Handheld OS Simulator")
        self.clock = pygame.time.Clock()

    def get_draw(self):
        """Returns the PIL ImageDraw object to draw on."""
        return self.draw

    def get_image(self):
        """Returns the PIL Image object."""
        return self.image

    def clear(self, color=config.COLOR_BG):
        """Clears the display with a color."""
        self.draw.rectangle((0, 0, self.width, self.height), fill=color)

    def show(self):
        """Updates the physical display or simulation window."""
        if not self.simulate:
            self.disp.display(self.image)
        else:
            import pygame
            # Convert PIL image to Pygame surface
            mode = self.image.mode
            size = self.image.size
            data = self.image.tobytes()
            py_image = pygame.image.fromstring(data, size, mode)
            self.screen.blit(py_image, (0, 0))
            pygame.display.flip()
            
            # Handle window close event
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()

    def set_backlight(self, value):
        """Sets backlight brightness (0-100)."""
        if not self.simulate:
            # Not all libraries support this directly, might need PWM on the pin
            # For now, assuming the library handles it or it's just on/off
            pass 
        else:
            pass
