#!/usr/bin/env bash

if [ "$(id -u)" != "0" ]; then
    echo 'Must be run as root!' 1>&2
    exit 1
fi

# Enable autostart
dietpi-autostart 17
mkdir /var/lib/dietpi/dietpi-autostart
tee /var/lib/dietpi/dietpi-autostart/custom.sh > /dev/null << EOF
#!/bin/bash
/usr/local/share/footrecon/venv/bin/footrecon --headless --config /usr/local/src/footrecon/footrecon.ini
exit 0
EOF
chmod a+x /var/lib/dietpi/dietpi-autostart/custom.sh
