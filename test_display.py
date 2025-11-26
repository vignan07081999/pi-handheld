import time
import RPi.GPIO as GPIO
from PIL import Image, ImageDraw
import st7789
import config

def test():
    print("Testing Display Hardware...")
    
    # 1. Setup GPIO
    GPIO.setmode(GPIO.BCM)
    
    # 2. Force Backlight On
    print(f"Turning on Backlight (Pin {config.PIN_DISPLAY_BL})...")
    GPIO.setup(config.PIN_DISPLAY_BL, GPIO.OUT)
    GPIO.output(config.PIN_DISPLAY_BL, GPIO.HIGH)
    
    # 3. Initialize Display
    print(f"Initializing ST7789 (SPI CS={0 if config.PIN_DISPLAY_CS == 8 else 1})...")
    
    try:
        disp = st7789.ST7789(
            port=0,
            cs=0 if config.PIN_DISPLAY_CS == 8 else 1,
            dc=config.PIN_DISPLAY_DC,
            rst=config.PIN_DISPLAY_RST,
            backlight=config.PIN_DISPLAY_BL,
            rotation=config.DISPLAY_ROTATION,
            spi_speed_hz=24000000 # Lower speed for testing
        )
        
        disp._spi.mode = 3
        disp.begin()
        
        print("Drawing RED...")
        img = Image.new('RGB', (config.DISPLAY_WIDTH, config.DISPLAY_HEIGHT), color=(255, 0, 0))
        disp.display(img)
        time.sleep(1)
        
        print("Drawing GREEN...")
        img = Image.new('RGB', (config.DISPLAY_WIDTH, config.DISPLAY_HEIGHT), color=(0, 255, 0))
        disp.display(img)
        time.sleep(1)
        
        print("Drawing BLUE...")
        img = Image.new('RGB', (config.DISPLAY_WIDTH, config.DISPLAY_HEIGHT), color=(0, 0, 255))
        disp.display(img)
        time.sleep(1)
        
        print("Test Complete. If screen remained black, check wiring.")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        GPIO.cleanup()

if __name__ == "__main__":
    test()
