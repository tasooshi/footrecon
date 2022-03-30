#!/usr/bin/env bash

if [ "$(id -u)" != "0" ]; then
    echo 'Must be run as root!' 1>&2
    exit 1
fi

export DEBIAN_FRONTEND=noninteractive

apt-get install -y -o APT::Immediate-Configure=false git build-essential python3-pip python3-dev python3-venv libbluetooth-dev libportaudio2 bluetooth gpsd gpsd-clients libjpeg-dev libffi-dev ffmpeg libatlas3-base

mkdir -p /usr/local/share/footrecon /usr/local/src/footrecon
chown $SUDO_USER:$SUDO_USER /usr/local/share/footrecon /usr/local/src/footrecon

sudo -u $SUDO_USER -i <<EOF
    git clone https://github.com/tasooshi/footrecon.git /usr/local/src/footrecon
    python3 -m venv --system-site-packages /usr/local/share/footrecon/venv
    source /usr/local/share/footrecon/venv/bin/activate
    pip install --upgrade pip
    pip install --only-binary numpy numpy==1.22.3
    cd /usr/local/src/footrecon
    python setup.py install
EOF

usermod -a -G dialout,audio,video,netdev $SUDO_USER
systemctl enable gpsd.service

echo -e "\n\e[32;1;5mFinished!\e[0m (reboot is recommended)"
