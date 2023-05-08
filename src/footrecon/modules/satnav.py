import csv
import os
import subprocess
import time

import gps

from footrecon.core.logs import logger
from footrecon.core import modules


__all__ = ['Satnav']


class Satnav(modules.Module):

    output_prefix = 'satnav'
    output_suffix = '.csv'
    interval = 2

    def setup(self):
        self.device = gps.gps(mode=gps.WATCH_ENABLE | gps.WATCH_NEWSTYLE)
        self.device_name = self.device.host + ':' + str(self.device.port)

    def task(self, output_file_name, stop_event):
        cmd_args = (
            '/usr/bin/gpscsv',
            '--header',
            '0',
            '--count',
            '1',
        )
        with open(output_file_name, 'w', newline='') as fil:
            writer = csv.writer(fil, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            while True:
                if stop_event.is_set():
                    break
                lines = subprocess.run(cmd_args, capture_output=True, universal_newlines=True).stdout.splitlines()
                lines = [line.strip() for line in lines]
                writer.writerow(lines)
                logger.debug(f'Saved output to {output_file_name}')
                fil.flush()
                os.fsync(fil)
                time.sleep(self.interval)
