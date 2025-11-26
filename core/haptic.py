import time
import threading
import config

# Try to import hardware libraries
try:
    import RPi.GPIO as GPIO
    HARDWARE_AVAILABLE = True
except ImportError:
    HARDWARE_AVAILABLE = False

class HapticManager:
    def __init__(self, simulate=False):
        self.simulate = simulate or not HARDWARE_AVAILABLE
        self.pwm = None
        
        if not self.simulate:
            self._init_hardware()
        else:
            print("Haptic Manager running in Simulation Mode")

    def _init_hardware(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(config.PIN_HAPTIC, GPIO.OUT)
        # Initialize PWM for variable intensity if supported
        # Frequency 100Hz is usually good for ERM motors
        self.pwm = GPIO.PWM(config.PIN_HAPTIC, 100)
        self.pwm.start(0)

    def vibrate(self, duration=0.05, intensity=1.0):
        """
        Trigger a vibration.
        duration: seconds
        intensity: 0.0 to 1.0
        """
        if self.simulate:
            # print(f"*VIBRATE* ({duration}s)")
            return

        # Run in a separate thread to not block the main loop
        threading.Thread(target=self._vibrate_thread, args=(duration, intensity)).start()

    def _vibrate_thread(self, duration, intensity):
        if self.pwm:
            duty_cycle = min(100, max(0, intensity * 100))
            self.pwm.ChangeDutyCycle(duty_cycle)
            time.sleep(duration)
            self.pwm.ChangeDutyCycle(0)
        else:
            # Fallback to simple on/off if PWM fails or for simple GPIO
            GPIO.output(config.PIN_HAPTIC, GPIO.HIGH)
            time.sleep(duration)
            GPIO.output(config.PIN_HAPTIC, GPIO.LOW)

    def cleanup(self):
        if self.pwm:
            self.pwm.stop()
