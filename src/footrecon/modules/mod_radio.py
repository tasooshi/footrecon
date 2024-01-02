import csv
import os
import shlex
import subprocess

from footrecon.core.logs import logger
from footrecon.core import modules


class Bluetooth(modules.Module):

    output_prefix = 'bluetooth'
    output_suffix = '.csv'

    def setup(self, interval=2):
        self.interval = int(interval)
        output = subprocess.run(shlex.split('/usr/bin/bluetoothctl list'), capture_output=True)
        try:
            self.device = output.stdout.splitlines()[0].split()[1]
        except IndexError:
            logger.debug(f'Module `{self.name}` did not find device')
        else:
            self.device_name = self.device.decode('utf8')

    def task(self):
        cmd_args = (
            '/usr/bin/btmgmt',
            'find',
        )
        with open(self.output_file_name, 'w', newline='', encoding='utf-8') as fil:
            writer = csv.writer(fil, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            for _ in self.loop:
                now = self.isodatetime()
                discoveries = list()
                lines = subprocess.run(cmd_args, capture_output=True, universal_newlines=True).stdout.splitlines()
                lines = [line.strip() for line in lines]
                for idx, line in enumerate(lines):
                    if 'dev_found' in line:
                        item = line.split()
                        baddr = item[2]
                        btype = item[4]
                        brssi = item[-3]
                        if 'name' in lines[idx + 1]:
                            bname = lines[idx + 1].partition(' ')[2]
                        else:
                            bname = ''
                        discoveries.append((baddr, bname, btype, brssi))
                for item in discoveries:
                    output = list(item)
                    output.insert(0, now)
                    writer.writerow(output)
                logger.debug(f'Module `{self.name}` saved output to {self.output_file_name}')
                fil.flush()
                os.fsync(fil)


class Wireless(modules.Module):

    output_prefix = 'wireless'
    output_suffix = '.csv'

    def setup(self, interval=2):
        self.interval = int(interval)
        output = subprocess.run(shlex.split('ls /sys/class/net/'), capture_output=True)
        wlans = [dev.decode('utf8') for dev in output.stdout.split() if dev.startswith(b'wl')]
        try:
            self.device = wlans[0]
        except IndexError:
            logger.debug(f'Module `{self.name}` did not find device')
        else:
            self.device_name = self.device

    def task(self):
        cmd_args = (
            '/usr/sbin/iwlist',
            self.device,
            'scan',
        )
        with open(self.output_file_name, 'w', newline='', encoding='utf-8') as fil:
            writer = csv.writer(fil, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            for _ in self.loop:
                proc = subprocess.run(cmd_args, capture_output=True, universal_newlines=True)
                lines = [line.strip() for line in proc.stdout.split('\n')]
                indexes = [i for i, s in enumerate(lines) if 'Cell ' in s]
                if indexes:
                    rows = list()
                    now = self.isodatetime()
                    for i in range(len(indexes) - 1):
                        data = lines[indexes[i]:indexes[i + 1]]
                        data.insert(0, now)
                        rows.append(data)
                    writer.writerows(rows)
                logger.debug(f'Module `{self.name}` saved output to {self.output_file_name}')
                fil.flush()
                os.fsync(fil)
