#!/usr/bin/env bash

if [ "$(id -u)" != "0" ]; then
    echo 'Must be run as root!' 1>&2
    exit 1
fi

export DEBIAN_FRONTEND=noninteractive

# Install required packages
apt-get install -y -o APT::Immediate-Configure=false gpsd gpsd-clients libatlas3-base

# Enable GPS daemon
systemctl enable gpsd.service
systemctl daemon-reload
