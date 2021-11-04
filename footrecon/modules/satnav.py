import asyncio
import csv
import os

import gps

from footrecon.core.logs import logger
from footrecon.core import modules


__all__ = ['Satnav']


class Satnav(modules.Module):

    output_prefix = 'satnav'
    output_suffix = '.csv'

    def setup(self):
        try:
            self.device = gps.gps(mode=gps.WATCH_ENABLE|gps.WATCH_NEWSTYLE) 
        except Exception as exc:
            logger.debug('Device not found for {}'.format(self.__class__.__name__))
        else:
            self.device_name = self.device.host + ':' + str(self.device.port)

    def _task(self):
        filename = self.output_file_name()
        with open(filename, 'w', newline='') as fil:
            writer = csv.writer(fil, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            while self.app.running:
                report = self.device.next()
                if report['class'] == 'TPV':
                    writer.writerow([
                        getattr(report,'time', ''),
                        getattr(report,'lat', 0.0),
                        getattr(report,'lon', 0.0),
                        getattr(report,'alt', 'nan'),
                        getattr(report,'epv', 'nan'),
                        getattr(report,'ept', 'nan'),
                        getattr(report,'speed', 'nan'),
                        getattr(report,'climb', 'nan'),
                    ])
                fil.flush()
                os.fsync(fil)

    async def task(self):
        await asyncio.get_running_loop().run_in_executor(self.executor, self._task)
