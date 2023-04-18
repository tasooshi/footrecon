#!/usr/bin/env bash

if [ "$(id -u)" != "0" ]; then
    echo 'Must be run as root!' 1>&2
    exit 1
fi

export DEBIAN_FRONTEND=noninteractive

# Install required packages
apt-get install -y -o APT::Immediate-Configure=false git build-essential python3-pip python3-dev python3-venv libportaudio2 bluetooth gpsd gpsd-clients libjpeg-dev libffi-dev ffmpeg libatlas3-base python3-pycparser

# Enable wireless devices
/boot/dietpi/func/dietpi-set_hardware wifimodules onboard_enable
/boot/dietpi/func/dietpi-set_hardware wifimodules enable
/boot/dietpi/func/dietpi-set_hardware bluetooth enable
echo "auto wlan0" >> /etc/network/interfaces

# Clone repository and install from source along with Python requirements
mkdir -p /usr/local/share/footrecon
git clone https://github.com/tasooshi/footrecon.git /usr/local/src/footrecon
python3 -m venv --system-site-packages /usr/local/share/footrecon/venv
source /usr/local/share/footrecon/venv/bin/activate
pip install --upgrade pip
pip install -e /usr/local/src/footrecon/

# Enable GPS daemon
systemctl enable gpsd.service

# Enable autostart
dietpi-autostart 17
mkdir /var/lib/dietpi/dietpi-autostart
tee /var/lib/dietpi/dietpi-autostart/custom.sh > /dev/null << EOF
#!/bin/bash
/usr/local/share/footrecon/venv/bin/footrecon --headless
exit 0
EOF
chmod u+x /var/lib/dietpi/dietpi-autostart/custom.sh

# Reboot
echo -e "\n\e[32;1;5mFinished!\e[0m (rebooting)"
reboot