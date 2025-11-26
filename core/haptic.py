import time
import threading
import config

try:
    from gpiozero import OutputDevice
    HARDWARE_AVAILABLE = True
except ImportError:
    HARDWARE_AVAILABLE = False

class HapticManager:
    def __init__(self, simulate=False):
        self.simulate = simulate or not HARDWARE_AVAILABLE
        self.motor = None
        
        if not self.simulate:
            try:
                # Revert to OutputDevice (PWM failed)
                self.motor = OutputDevice(config.PIN_HAPTIC, active_high=True, initial_value=False)
            except Exception as e:
                print(f"Haptic Init Failed: {e}")
                self.simulate = True
        else:
            print("Haptic Manager running in Simulation Mode")

    def vibrate(self, duration=0.05, intensity=1.0):
        if self.simulate:
            return

        # Intensity ignored for OutputDevice
        threading.Thread(target=self._vibrate_thread, args=(duration,)).start()

    def _vibrate_thread(self, duration):
        if self.motor:
            self.motor.on()
            time.sleep(duration)
            self.motor.off()

    def cleanup(self):
        if self.motor:
            self.motor.close()
