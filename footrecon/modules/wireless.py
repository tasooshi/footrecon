import asyncio
import csv
import datetime
import os
import pathlib
import shlex
import subprocess
import time

from footrecon.core.logs import logger
from footrecon.core import modules


__all__ = ['Wireless']


class Wireless(modules.Module):

    bin_path = '/usr/sbin/iwlist'
    output_prefix = 'wireless'
    output_suffix = '.csv'
    interval = 2
    separator = 'Cell '

    def setup(self):
        output = subprocess.run(shlex.split('ls /sys/class/net/'), capture_output=True)
        wlans = [dev.decode('utf8') for dev in output.stdout.split() if dev.startswith(b'wl')]
        try:
            self.device = wlans[0]
        except Exception as exc:
            logger.debug('Device not found for {}'.format(self.__class__.__name__))
        else:
            self.device_name = self.device

    def _task(self):
        cmd_args = [
            self.bin_path,
            self.device,
            'scan',
        ]
        filename = self.output_file_name()
        with open(filename, 'w', newline='') as fil:
            writer = csv.writer(fil, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            while self.app.running:
                proc = subprocess.run(cmd_args, capture_output=True, universal_newlines=True)
                lines = proc.stdout.split('\n')
                lines = [line.strip() for line in lines]
                indexes = [i for i, s in enumerate(lines) if self.separator in s]
                if indexes:
                    rows = list()
                    now = self.isodatetime()
                    for i in range(len(indexes) - 1):
                        data = lines[indexes[i]:indexes[i + 1]]
                        data.insert(0, now)
                        rows.append(data)
                    writer.writerows(rows)
                fil.flush()
                os.fsync(fil)
                time.sleep(self.interval)

    async def task(self):
        await asyncio.get_running_loop().run_in_executor(self.executor, self._task)
