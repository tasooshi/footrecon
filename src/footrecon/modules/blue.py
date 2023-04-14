import csv
import os

import bluetooth

from footrecon.core.logs import logger
from footrecon.core import modules


__all__ = ['Bluetooth']


class Bluetooth(modules.Module):

    output_prefix = 'bluetooth'
    output_suffix = '.csv'
    interval = 2

    def setup(self):
        try:
            self.device = bluetooth.bluez._bt.hci_get_route()
        except OSError:
            logger.debug('Device not found for {}'.format(self.__class__.__name__))
        else:
            self.device_name = '#' + str(self.device)

    def task(self, output_file_name, stop_event):
        with open(output_file_name, 'w', newline='') as fil:
            writer = csv.writer(fil, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            while True:
                devices = bluetooth.discover_devices(duration=self.interval, lookup_names=True, flush_cache=True, lookup_class=False)
                now = self.isodatetime()
                for dev in devices:
                    output = list(dev)
                    output.insert(0, now)
                    writer.writerow(output)
                    logger.debug(f'Saved output to {output_file_name}')
                fil.flush()
                os.fsync(fil)
                if stop_event.is_set():
                    break
