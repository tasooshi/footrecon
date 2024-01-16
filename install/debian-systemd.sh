#!/usr/bin/env bash

if [ "$(id -u)" != "0" ]; then
    echo 'Must be run as root!' 1>&2
    exit 1
fi

# Enable systemd
tee /etc/systemd/system/footrecon.service > /dev/null << EOF
[Unit]
Description=footrecon

[Service]
Type=simple
Restart=always
RestartSec=5
User=root
Group=root
WorkingDirectory=/root
ExecStart=/usr/local/share/footrecon/venv/bin/footrecon --headless --config /usr/local/src/footrecon/footrecon.ini --log /var/log/footrecon.log

[Install]
WantedBy=multi-user.target
EOF
systemctl enable footrecon
systemctl daemon-reload
systemctl start footrecon
