import csv
import os
import shlex
import subprocess
import time

from footrecon.core.logs import logger
from footrecon.core import modules


__all__ = ['Bluetooth']


class Bluetooth(modules.Module):

    output_prefix = 'bluetooth'
    output_suffix = '.csv'
    interval = 2

    def setup(self):
        output = subprocess.run(shlex.split('/usr/bin/bluetoothctl list'), capture_output=True)
        try:
            self.device = output.stdout.splitlines()[0].split()[1]
        except IndexError:
            logger.debug('Device not found for {}'.format(self.__class__.__name__))
        else:
            self.device_name = self.device.decode('utf8')

    def task(self, output_file_name, stop_event):
        cmd_args = (
            '/usr/bin/btmgmt',
            'find',
        )
        with open(output_file_name, 'w', newline='') as fil:
            writer = csv.writer(fil, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            while True:
                if stop_event.is_set():
                    break
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
                    logger.debug(f'Saved output to {output_file_name}')
                fil.flush()
                os.fsync(fil)
                time.sleep(self.interval)
