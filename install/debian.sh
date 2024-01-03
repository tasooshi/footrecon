#!/usr/bin/env bash

if [ "$(id -u)" != "0" ]; then
    echo 'Must be run as root!' 1>&2
    exit 1
fi

export DEBIAN_FRONTEND=noninteractive

# Install required packages
apt-get install -y -o APT::Immediate-Configure=false git build-essential python3-pip python3-dev python3-venv libportaudio2 bluetooth libjpeg-dev libffi-dev ffmpeg python3-pycparser ssh net-tools

# Clone repository and install from source along with Python requirements
mkdir -p /usr/local/share/footrecon
git clone https://github.com/tasooshi/footrecon.git /usr/local/src/footrecon
cp /usr/local/src/footrecon/install/footrecon.ini.example /usr/local/src/footrecon/footrecon.ini
python3 -m venv --system-site-packages /usr/local/share/footrecon/venv
source /usr/local/share/footrecon/venv/bin/activate
pip install --upgrade pip
pip install -e /usr/local/src/footrecon/
