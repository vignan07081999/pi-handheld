#!/bin/bash

# Raspberry Pi Handheld OS Installer

echo "Installing Dependencies..."
sudo apt-get update
sudo apt-get install -y python3-pip python3-pil python3-numpy python3-rpi.gpio python3-spidev python3-smbus libopenjp2-7 libtiff5

# Install Python Libraries
pip3 install -r requirements.txt

# Create Systemd Service
echo "Creating Systemd Service..."
SERVICE_FILE=/etc/systemd/system/pi-handheld.service
CURRENT_DIR=$(pwd)

sudo bash -c "cat > $SERVICE_FILE" <<EOL
[Unit]
Description=Pi Handheld OS
After=multi-user.target

[Service]
Type=simple
User=pi
WorkingDirectory=$CURRENT_DIR
ExecStart=/usr/bin/python3 $CURRENT_DIR/main.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOL

# Enable Service
echo "Enabling Service..."
sudo systemctl daemon-reload
sudo systemctl enable pi-handheld.service
sudo systemctl start pi-handheld.service

echo "Installation Complete! The OS should be running now."
