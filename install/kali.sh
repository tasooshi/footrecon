#!/usr/bin/env bash

if [ "$(id -u)" != "0" ]; then
    echo 'Must be run as root!' 1>&2
    exit 1
fi

export DEBIAN_FRONTEND=noninteractive

apt-get install -y -o APT::Immediate-Configure=false git build-essential python3-pip python3-dev python3-venv libbluetooth-dev libportaudio2 bluetooth gpsd gpsd-clients ffmpeg

mkdir -p /usr/local/share/footrecon /usr/local/src/footrecon
chown $SUDO_USER:$SUDO_USER /usr/local/share/footrecon /usr/local/src/footrecon

sudo -u $SUDO_USER -i <<EOF
    git clone https://github.com/tasooshi/footrecon.git /usr/local/src/footrecon
    python3 -m venv --system-site-packages /usr/local/share/footrecon/venv
    source /usr/local/share/footrecon/venv/bin/activate
    cd /usr/local/src/footrecon
    python setup.py install
EOF

echo "$SUDO_USER   ALL=NOPASSWD:/usr/bin/timedatectl,/usr/bin/date,/usr/sbin/hwclock" > /etc/sudoers.d/footrecon
chmod 0440 /etc/sudoers.d/footrecon
usermod -a -G dialout $SUDO_USER
systemctl enable gpsd.service

echo -e "\n\e[32;1;5mFinished!\e[0m (reboot is recommended)"
