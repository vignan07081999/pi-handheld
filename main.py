import sys
import argparse
import time
import logging
from core.display import DisplayManager
from core.input import InputManager
from core.app_manager import AppManager
from core.haptic import HapticManager
import config

# Setup Logging
try:
    log_file = "pi_os.log"
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
except PermissionError:
    # Fallback to /tmp if current dir is not writable (e.g. owned by root)
    log_file = "/tmp/pi_os.log"
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
except Exception as e:
    # Fallback to stdout only
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description='Raspberry Pi Handheld OS')
    parser.add_argument('--sim', action='store_true', help='Run in simulation mode on PC')
    args = parser.parse_args()

    logger.info("Starting Pi Handheld OS...")
    
    # Initialize Core Systems
    display = DisplayManager(simulate=args.sim)
    
    # If Display failed to load hardware, force simulation for everything else
    if display.simulate and not args.sim:
        print("Display hardware unavailable. Forcing Simulation Mode for all components.")
        args.sim = True

    haptic = HapticManager(simulate=args.sim)
    input_manager = InputManager(simulate=args.sim)
    
    # Bind Haptics to Input Events
    # We want subtle clicks on rotation and bumps on selection
    input_manager.on_any_event = lambda event_type: haptic_feedback(haptic, event_type)

    # Show Boot Screen
    display.clear((0, 0, 0))
    draw = display.get_draw()
    # Simple Boot Animation
    for i in range(10):
        draw.rectangle((0, 0, 240, 320), fill=(0, 0, 0))
        draw.text((80, 140), "BOOTING...", fill=(0, 255, 213))
        draw.rectangle((70, 170, 70 + (i * 10), 180), fill=(0, 255, 213))
        display.show()
        time.sleep(0.1)
    
    # Initialize App Manager
    app_manager = AppManager(display, input_manager)
    
    # Start Main Loop
    try:
        app_manager.run()
    except KeyboardInterrupt:
        print("Shutting down...")
    except Exception as e:
        print(f"Critical Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Cleanup
        if not args.sim:
            haptic.cleanup()

def haptic_feedback(haptic, event_type):
    if event_type in ['left', 'right']:
        haptic.vibrate(config.HAPTIC_DURATION_SHORT, 0.4) # Subtle click
    elif event_type == 'select':
        haptic.vibrate(config.HAPTIC_DURATION_SHORT, 0.8) # Stronger click
    elif event_type == 'back':
        haptic.vibrate(config.HAPTIC_DURATION_LONG, 1.0) # Long vibration

if __name__ == "__main__":
    main()
