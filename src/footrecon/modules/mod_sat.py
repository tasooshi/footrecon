import csv
import os
import subprocess

import gps

from footrecon.core.logs import logger
from footrecon.core import modules


class Satnav(modules.Module):

    output_prefix = 'satnav'
    output_suffix = '.csv'

    def setup(self, interval=2):
        self.interval = int(interval)
        self.device = gps.gps(mode=gps.WATCH_ENABLE | gps.WATCH_NEWSTYLE)
        self.device_name = self.device.host + ':' + str(self.device.port)

    def task(self):
        cmd_args = (
            '/usr/bin/gpscsv',
            '--header',
            '0',
            '--count',
            '1',
        )
        with open(self.output_file_name, 'w', newline='') as fil:
            writer = csv.writer(fil, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            for _ in self.loop:
                lines = subprocess.run(cmd_args, capture_output=True, universal_newlines=True).stdout.splitlines()
                lines = [line.strip() for line in lines]
                writer.writerow(lines)
                logger.debug(f'Module `{self.name}` saved output to {self.output_file_name}')
                fil.flush()
                os.fsync(fil)
