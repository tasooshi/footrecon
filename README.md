# Footrecon

## About

A mobile all-in-one solution for the initial on-premises information gathering using wifi, bluetooth, camera, audio and GPS. Designed to work with Debian-based distributions out of the box. Easily extensible with configurable modules.

![Footrecon - main view](docs/footrecon-screenshot.png)

## Installation

### Using PyPI

    $ pip install footrecon

### From sources

    $ git clone https://github.com/tasooshi/footrecon
    $ cd footrecon
    $ python3 -m venv .venv
    $ source .venv/bin/activate
    $ pip install -e .
    $ cp ./install/footrecon.ini.example ./footrecon.ini
    $ footrecon

### Using scripts

#### Generic Debian installation

    $ sudo /bin/bash -c "$(curl https://raw.githubusercontent.com/tasooshi/footrecon/main/install/debian.sh)"

The output will be stored in the `root` home directory.

#### Debian autostart with systemd

Executes in the background:

    $ sudo /bin/bash -c "$(curl https://raw.githubusercontent.com/tasooshi/footrecon/main/install/debian-systemd.sh)"

The logs will be saved in `/var/log/footrecon.log`.

#### Dietpi autostart with dietpi-autostart

Executes in a headless mode:

    $ sudo /bin/bash -c "$(curl https://raw.githubusercontent.com/tasooshi/footrecon/main/install/dietpi-autostart.sh)"

The logs will be saved in `/root/footrecon.log`.

#### Install gpsd

    $ sudo /bin/bash -c "$(curl https://raw.githubusercontent.com/tasooshi/footrecon/main/install/debian-gpsd.sh)"

## Modules

| Class      | What it does                                                                                       | Module path                              |
| :--------- | :------------------------------------------------------------------------------------------------- | :----------------------------------------|
| Microphone | Records from default audio input device and saves to a WAV file                                    | `footrecon.modules.mod_input.Microphone` |
| Camera     | Takes picture every N seconds and saves as JPEGs                                                   | `footrecon.modules.mod_input.Camera`     |
| Satnav     | Stores location data if a gpsd compatible device is available, otherwise the CSV file is empty     | `footrecon.modules.mod_sat.Satnav`       |
| Bluetooth  | Collects Blutooth addresses, device names and RSSI and stores the data in a CSV file               | `footrecon.modules.mod_radio.Bluetooth`  |
| Wireless   | Collects wireless networks details, i.a. SSIDs, encryption, signal strength and MACs in a CSV file | `footrecon.modules.mod_radio.Wireless`   |
| Healtheck  | Periodically sends GET request                                                                     | `footrecon.modules.mod_net.Healthcheck`  |
| Ssh        | Keeps SSH connection open                                                                          | `footrecon.modules.mod_net.Ssh`          |

Building your own modules is pretty simple. Here's an example, it sends GET request every 5 seconds:

    class Healthcheck(modules.Module):

        def setup(self, interval=60, endpoint='http://127.0.0.1/?id='):
            self.interval = int(interval)
            self.endpoint = endpoint

        def task(self):
            for counter in self.loop:
                logger.debug(f'Module `{self.name}` sending GET request to {self.endpoint}')
                requests.get(self.endpoint + str(counter))

## Configuration

Modules set to "1" will be enabled on start.

    [modules]
    footrecon.modules.mod_input.Camera = 0
    footrecon.modules.mod_input.Microphone = 0
    footrecon.modules.mod_radio.Bluetooth = 1
    footrecon.modules.mod_radio.Wireless = 1
    footrecon.modules.mod_sat.Satnav = 0
    footrecon.modules.mod_net.Healthcheck = 0
    footrecon.modules.mod_net.Ssh = 0

Default values can be overwritten per class-basis:

    [footrecon.modules.mod_net.Ssh]
    interval = 120
    host = 127.0.0.1
    port = 22
    local_port = 22
    remote_port = 0
    username = hello
    key = /root/.ssh/id_hello

    [footrecon.modules.mod_net.Healthcheck]
    interval = 240
    endpoint = http://localhost/healthcheck?id=

## Usage

    usage: footrecon [-h] [-c CONFIG] [--headless] [--debug]

    A mobile all-in-one solution for physical recon.

    options:
      -h, --help            show this help message and exit
      -c CONFIG, --config CONFIG
                            Configuration file (default: footrecon.ini)
      --log                 Log file (default: footrecon.log)
      --headless            Run in headless mode (default: False)
      --debug               Enable debugging mode (verbose output) (default: INFO)

## Notes

* It takes the first available device from every device group, so e.g. the first available camera if there are two.
