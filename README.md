# Raspberry Pi Handheld OS

A complete OS solution for a Raspberry Pi handheld device with a rotary encoder and ST7789 display.

## Features
- **Apps**: Torch, Measuring Tool, Home Assistant Controller.
- **Games**: Snake, Maze, Pong.
- **System**: WiFi Manager, Settings, Highscores.
- **UI**: Minimalist Dark AMOLED theme, Infinite scrolling menu.

## Hardware Requirements
- Raspberry Pi (Zero, 3, 4, etc.)
- ST7789 Display (SPI)
- Rotary Encoder with Push Button
- Haptic Motor (Optional)

## Installation

1. **Transfer Files**: Copy the `pi_handheld_os` folder to your Raspberry Pi (e.g., `/home/pi/pi_handheld_os`).
2. **Configure Pins**: Edit `config.py` and update the GPIO pin numbers to match your wiring (refer to your "Google Gemini.pdf").
3. **Run Installer**:
   ```bash
   cd pi_handheld_os
   chmod +x install.sh
   ./install.sh
   ```
   This script will install dependencies and set up the OS to start automatically on boot.

## Manual Usage
To run manually (for testing):
```bash
python3 main.py
```

## PC Simulation
You can test the UI and Logic on your PC without the hardware:
```bash
python3 main.py --sim
```
**Controls (Simulation):**
- **Left Arrow**: Rotate Left
- **Right Arrow**: Rotate Right
- **Enter**: Select / Push Button
- **Esc / Backspace**: Back / Long Press

## Adding New Apps
Create a new folder in `apps/` or `games/` with a `main.py` file containing an `App` class.
The system will automatically detect and load it.
