import csv
import os
import shlex
import subprocess
import time

from footrecon.core.logs import logger
from footrecon.core import modules


__all__ = ['Wireless']


class Wireless(modules.Module):

    output_prefix = 'wireless'
    output_suffix = '.csv'
    interval = 2

    def setup(self):
        output = subprocess.run(shlex.split('ls /sys/class/net/'), capture_output=True)
        wlans = [dev.decode('utf8') for dev in output.stdout.split() if dev.startswith(b'wl')]
        try:
            self.device = wlans[0]
        except IndexError:
            logger.debug('Device not found for {}'.format(self.__class__.__name__))
        else:
            self.device_name = self.device

    def task(self, output_file_name, stop_event):
        cmd_args = (
            '/usr/sbin/iwlist',
            self.device,
            'scan',
        )
        with open(output_file_name, 'w', newline='') as fil:
            writer = csv.writer(fil, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            while True:
                if stop_event.is_set():
                    break
                proc = subprocess.run(cmd_args, capture_output=True, universal_newlines=True)
                lines = proc.stdout.split('\n')
                lines = [line.strip() for line in lines]
                indexes = [i for i, s in enumerate(lines) if 'Cell ' in s]
                if indexes:
                    rows = list()
                    now = self.isodatetime()
                    for i in range(len(indexes) - 1):
                        data = lines[indexes[i]:indexes[i + 1]]
                        data.insert(0, now)
                        rows.append(data)
                    writer.writerows(rows)
                    logger.debug(f'Saved output to {output_file_name}')
                fil.flush()
                os.fsync(fil)
                time.sleep(self.interval)
