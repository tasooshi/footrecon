import csv
import os
import time

import gps

from footrecon.core.logs import logger
from footrecon.core import modules


__all__ = ['Satnav']


class Satnav(modules.Module):

    output_prefix = 'satnav'
    output_suffix = '.csv'
    interval = 2
    timeout = 10

    def setup(self):
        self.device = gps.gps(mode=gps.WATCH_ENABLE | gps.WATCH_NEWSTYLE)
        self.device_name = self.device.host + ':' + str(self.device.port)

    def task(self, output_file_name, stop_event):
        fil = open(output_file_name, 'w', newline='')
        writer = csv.writer(fil, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        while True:
            waiting = self.device.waiting(timeout=self.timeout)
            if stop_event.is_set() or not waiting:
                break
            report = self.device.next()
            if report['class'] == 'TPV':
                writer.writerow([
                    getattr(report, 'time', ''),
                    getattr(report, 'lat', 0.0),
                    getattr(report, 'lon', 0.0),
                    getattr(report, 'alt', 'nan'),
                    getattr(report, 'epv', 'nan'),
                    getattr(report, 'ept', 'nan'),
                    getattr(report, 'speed', 'nan'),
                    getattr(report, 'climb', 'nan'),
                ])
                logger.debug(f'Saved output to {output_file_name}')
            fil.flush()
            os.fsync(fil)
            time.sleep(self.interval)
        self.device.close()
        fil.close()
