#!/bin/bash

# Raspberry Pi Handheld OS Installer

echo "Installing Dependencies..."
sudo apt-get update
# Enable SPI Interface
sudo raspi-config nonint do_spi 0
# libtiff5 is replaced by libtiff6 in newer Debian, or provided by libtiff-dev
# python3-venv is needed for virtual environments
# swig and python3-dev are needed to build lgpio
sudo apt-get install -y python3-pip python3-pil python3-numpy python3-rpi.gpio python3-spidev python3-smbus libopenjp2-7 libtiff-dev python3-venv swig python3-dev

# Create Virtual Environment to avoid PEP 668 "externally-managed-environment" error
echo "Creating Virtual Environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

# Install Python Libraries into Virtual Environment
echo "Installing Python Libraries..."
./venv/bin/pip install -r requirements.txt

# Create Systemd Service
echo "Creating Systemd Service..."
SERVICE_FILE=/etc/systemd/system/pi-handheld.service
CURRENT_DIR=$(pwd)
PYTHON_EXEC=$CURRENT_DIR/venv/bin/python

sudo bash -c "cat > $SERVICE_FILE" <<EOL
[Unit]
Description=Pi Handheld OS
After=multi-user.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$CURRENT_DIR
ExecStart=$PYTHON_EXEC $CURRENT_DIR/main.py
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
