import shutil
import os

# Source is the artifact path provided by the tool output
# I need to copy it to a local temp file first or just use the absolute path if I knew it.
# Since I can't easily know the absolute path dynamically in this script without passing it,
# I will assume the user (me) will copy the file to 'placeholder.png' in the current dir first.

source = "placeholder.png"
dest_dir = "assets/icons"

if not os.path.exists(dest_dir):
    os.makedirs(dest_dir)

icons = [
    # Categories
    "games.png", "tools.png", "apps.png", "settings.png",
    # Apps
    "torch.png", "measure.png", "home_assistant.png", "weather.png",
    # Games
    "snake.png", "pong.png", "racing.png", "breakout.png", "lunar_lander.png", "space_invaders.png",
    # Status
    "wifi_on.png", "wifi_off.png", "weather_sunny.png", "weather_cloudy.png", "weather_rain.png"
]

for icon in icons:
    dest = os.path.join(dest_dir, icon)
    if not os.path.exists(dest):
        try:
            shutil.copy(source, dest)
            print(f"Created {dest}")
        except FileNotFoundError:
            print(f"Error: Source {source} not found.")
            break
