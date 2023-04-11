import csv
import datetime
import os
import select

import bluetooth

from footrecon.core.logs import logger
from footrecon.core import modules


__all__ = ['Bluetooth']


class CustomDiscoverer(bluetooth.DeviceDiscoverer):

    def __init__(self, output_file_name, /, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.output_file_name = output_file_name
        self.fil = open(output_file_name, 'w', newline='')
        self.writer = csv.writer(self.fil, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)

    def pre_inquiry(self):
        self.done = False

    def isodatetime(self):
        return datetime.datetime.utcnow().isoformat() + 'Z'

    def device_discovered(self, address, device_class, rssi, name):
        output = list(address, device_class, rssi, name)
        output.insert(0, self.isodatetime())
        self.writer.writerow(output)
        logger.debug(f'Saved output to {self.output_file_name}')
        self.fil.flush()
        os.fsync(self.fil)

    def inquiry_complete(self):
        self.done = True


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
        discoverer = CustomDiscoverer(output_file_name)
        discoverer.find_devices(lookup_names=True)
        readfiles = [discoverer, ]
        while True:
            rfds = select.select(readfiles, [], [])[0]
            if discoverer in rfds:
                discoverer.process_event()
            if discoverer.done:
                break
            if stop_event.is_set():
                return
