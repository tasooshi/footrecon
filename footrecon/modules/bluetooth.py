import csv
import datetime
import os
import asyncio

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

    def _task(self):
        filename = self.output_file_name()
        logger.debug(f'Writing output to {filename}')
        with open(filename, 'w', newline='') as fil:
            writer = csv.writer(fil, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            while self.app.running:
                devices = bluetooth.discover_devices(duration=self.interval, lookup_names=True, flush_cache=True, lookup_class=False)
                now = self.isodatetime()
                for dev in devices:
                    output = list(dev)
                    output.insert(0, now)
                    writer.writerow(output)
                    logger.debug(f'Saved output to {filename}')
                fil.flush()
                os.fsync(fil)

    async def task(self):
        await asyncio.get_running_loop().run_in_executor(self.executor, self._task)
