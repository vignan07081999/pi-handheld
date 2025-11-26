import time
import threading
import config

try:
    from gpiozero import PWMOutputDevice
    HARDWARE_AVAILABLE = True
except ImportError:
    HARDWARE_AVAILABLE = False

class HapticManager:
    def __init__(self, simulate=False):
        self.simulate = simulate or not HARDWARE_AVAILABLE
        self.motor = None
        
        if not self.simulate:
            try:
                self.motor = PWMOutputDevice(config.PIN_HAPTIC, frequency=100)
            except Exception as e:
                print(f"Haptic Init Failed: {e}")
                self.simulate = True
        else:
            print("Haptic Manager running in Simulation Mode")

    def vibrate(self, duration=0.05, intensity=1.0):
        if self.simulate:
            return

        threading.Thread(target=self._vibrate_thread, args=(duration, intensity)).start()

    def _vibrate_thread(self, duration, intensity):
        if self.motor:
            self.motor.value = min(1.0, max(0.0, intensity))
            time.sleep(duration)
            self.motor.off()

    def cleanup(self):
        if self.motor:
            self.motor.close()
