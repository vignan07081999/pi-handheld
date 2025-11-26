import time
import RPi.GPIO as GPIO
from PIL import Image
import st7789
import config
import spidev

def test():
    print("Testing Display Hardware V2...")
    
    # 1. Setup GPIO
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(config.PIN_DISPLAY_BL, GPIO.OUT)
    GPIO.setup(config.PIN_DISPLAY_RST, GPIO.OUT)
    
    # 2. Hard Reset
    print("Performing Hard Reset...")
    GPIO.output(config.PIN_DISPLAY_RST, GPIO.HIGH)
    time.sleep(0.1)
    GPIO.output(config.PIN_DISPLAY_RST, GPIO.LOW)
    time.sleep(0.1)
    GPIO.output(config.PIN_DISPLAY_RST, GPIO.HIGH)
    time.sleep(0.1)
    
    # 3. Turn on Backlight
    print("Turning on Backlight...")
    GPIO.output(config.PIN_DISPLAY_BL, GPIO.HIGH)
    
    # 4. Try Modes
    modes = [3, 0, 2, 1]
    
    for mode in modes:
        print(f"\nTrying SPI Mode {mode}...")
        try:
            # Re-init display
            disp = st7789.ST7789(
                port=0,
                cs=0 if config.PIN_DISPLAY_CS == 8 else 1,
                dc=config.PIN_DISPLAY_DC,
                rst=config.PIN_DISPLAY_RST,
                backlight=config.PIN_DISPLAY_BL,
                rotation=config.DISPLAY_ROTATION,
                spi_speed_hz=24000000
            )
            
            # Manually set mode if library allows access to internal spi
            if hasattr(disp, '_spi'):
                disp._spi.mode = mode
            
            disp.begin()
            
            print("Drawing Colors...")
            # Red
            img = Image.new('RGB', (config.DISPLAY_WIDTH, config.DISPLAY_HEIGHT), color=(255, 0, 0))
            disp.display(img)
            time.sleep(1)
            
            # Green
            img = Image.new('RGB', (config.DISPLAY_WIDTH, config.DISPLAY_HEIGHT), color=(0, 255, 0))
            disp.display(img)
            time.sleep(1)
            
            print(f"Did you see colors with Mode {mode}?")
            
        except Exception as e:
            print(f"Error in Mode {mode}: {e}")

    print("\nTest Complete.")
    GPIO.cleanup()

if __name__ == "__main__":
    test()
