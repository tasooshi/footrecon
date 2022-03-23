# Footrecon

## About

A mobile all-in-one solution for the initial on-premises information gathering using wifi, bluetooth, camera, audio and GPS. Designed to work with Debian Linux, Kali Linux, DietPi and Raspberry Pi OS.

This is an early release, still in development.

![Footrecon - main view](docs/footrecon-screenshot.png)

## Installation

Using the provided installation scripts:

### Debian Linux

    user@localhost:~$ sudo /bin/bash -c "$(curl https://raw.githubusercontent.com/tasooshi/footrecon/main/install/debian.sh)"

### Kali Linux

    user@localhost:~$ sudo /bin/bash -c "$(curl https://raw.githubusercontent.com/tasooshi/footrecon/main/install/kali.sh)"

### DietPi

    dietpi@DietPi:~$ sudo /bin/bash -c "$(curl https://raw.githubusercontent.com/tasooshi/footrecon/main/install/dietpi.sh)"

#### Autoboot

You may want to start Footrecon automatically on-boot. In this case it is best to use the `dietpi-autostart` utility. Add the following to your script:

    #!/bin/bash
    /usr/local/share/footrecon/venv/bin/footrecon
    exit 0

For a headless mode and auto-start use the `--start` argument:

    #!/bin/bash
    /usr/local/share/footrecon/venv/bin/footrecon --start
    exit 0

### Raspberry Pi OS

    TODO

### Notes

* The installation script uses the `sudo` environment variable `$SUDO_USER` as the target user for which the necessary changes should be made. You may want to adjust that to your setup.

## Changelog

### 0.3 (2022-03-23)

* Updated Pillow

### 0.2 (2022-01-13)

* Updated Pillow
* Changed license

### 0.1 (2021-11-24)

* Initial release