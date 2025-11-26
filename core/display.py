import time
import sys
import spidev
from PIL import Image, ImageDraw
from gpiozero import OutputDevice
import config

class DisplayManager:
    def __init__(self, simulate=False):
        self.width = config.DISPLAY_WIDTH
        self.height = config.DISPLAY_HEIGHT
        self.simulate = simulate
        
        # Create a blank image for drawing
        self.image = Image.new("RGB", (self.width, self.height), config.COLOR_BG)
        self.draw = ImageDraw.Draw(self.image)
        
        if not self.simulate:
            try:
                self._init_hardware()
            except Exception as e:
                print(f"Display Init Failed: {e}")
                if "busy" in str(e).lower():
                    print("HINT: 'GPIO busy' usually means the background service is running.")
                    print("Try running: sudo systemctl stop pi-handheld.service")
                self.simulate = True
                self._init_simulation()
        else:
            self._init_simulation()

    def _init_hardware(self):
        print("Initializing Display (SPI via spidev)...")
        
        # SPI Setup
        self.bus = 0
        self.device = 0
        self.spi = spidev.SpiDev()
        self.spi.open(self.bus, self.device)
        self.spi.max_speed_hz = 40000000
        self.spi.mode = 0b00

        # GPIO Setup (using gpiozero)
        self.rst = OutputDevice(config.PIN_DISPLAY_RST, active_high=True, initial_value=False)
        self.dc  = OutputDevice(config.PIN_DISPLAY_DC, active_high=True, initial_value=False)
        self.bl  = OutputDevice(config.PIN_DISPLAY_BL, active_high=True, initial_value=True)

        self._init_display_sequence()

    def _command(self, cmd):
        self.dc.off() # Command
        self.spi.writebytes([cmd])

    def _data(self, val):
        self.dc.on() # Data
        self.spi.writebytes([val])

    def _init_display_sequence(self):
        # Reset
        self.rst.on()
        time.sleep(0.01)
        self.rst.off()
        time.sleep(0.01)
        self.rst.on()
        time.sleep(0.15)

        # Init Commands
        self._command(0x36); self._data(0x00) # MADCTL
        self._command(0x3A); self._data(0x05) # COLMOD (16-bit)
        self._command(0x21) # INVON
        self._command(0x11) # SLPOUT
        time.sleep(0.12)
        self._command(0x29) # DISPON

    def _set_window(self, x_start, y_start, x_end, y_end):
        self._command(0x2A)
        self.dc.on() # Data Mode for parameters
        self.spi.writebytes([x_start >> 8, x_start & 0xFF, x_end >> 8, x_end & 0xFF])
        
        self._command(0x2B)
        self.dc.on() # Data Mode for parameters
        self.spi.writebytes([y_start >> 8, y_start & 0xFF, y_end >> 8, y_end & 0xFF])
        
        self._command(0x2C)

    def _init_simulation(self):
        print("Initializing Pygame Simulation...")
        import pygame
        pygame.init()
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Pi Handheld OS Simulator")

    def get_draw(self):
        return self.draw

    def get_image(self):
        return self.image

    def clear(self, color=config.COLOR_BG):
        self.draw.rectangle((0, 0, self.width, self.height), fill=color)

    def show(self):
        if not self.simulate:
            self._update_display()
        else:
            self._update_simulation()

    def _update_display(self):
        # Resize if needed
        img = self.image
        if img.width != self.width or img.height != self.height:
            img = img.resize((self.width, self.height))
        
        # Fast PIL to Bytes conversion (RGB888)
        image_bytes = img.convert("RGB").tobytes()
        buffer = []
        
        # Manual RGB888 -> RGB565 conversion (Slow but proven working)
        for i in range(0, len(image_bytes), 3):
            r = image_bytes[i]
            g = image_bytes[i+1]
            b = image_bytes[i+2]
            rgb = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
            buffer.append(rgb >> 8)
            buffer.append(rgb & 0xFF)

        # Write to SPI
        self._set_window(0, 0, self.width-1, self.height-1)
        self.dc.on()
        
        # Chunked write
        chunk_size = 4096
        for i in range(0, len(buffer), chunk_size):
            self.spi.writebytes(buffer[i:i+chunk_size])

    def _update_simulation(self):
        import pygame
        mode = self.image.mode
        size = self.image.size
        data = self.image.tobytes()
        py_image = pygame.image.fromstring(data, size, mode)
        self.screen.blit(py_image, (0, 0))
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
