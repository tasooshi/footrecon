import time

import imageio

from footrecon.core.logs import logger
from footrecon.core import modules


__all__ = ['Camera']


class Camera(modules.Module):

    output_prefix = 'picture-'
    output_suffix = '.jpg'
    device_id = '<video0>'
    quality = 80
    interval = 2

    def setup(self):
        try:
            self.device = imageio.get_reader(self.device_id)
        except IndexError:
            logger.debug('Device not found for {}'.format(self.__class__.__name__))
        else:
            self.device_name = self.device_id

    def task(self, output_file_name, stop_event):
        idx = 1
        file_base = list(output_file_name.partition(self.output_suffix))
        while True:
            frame = self.device.get_next_data()
            img = imageio.imwrite('<bytes>', frame, plugin='pillow', format='JPEG')
            indexed_file_name = file_base[0] + str(idx) + file_base[1]
            with open(indexed_file_name, 'wb') as fil:
                fil.write(img)
            logger.debug(f'Saved image to {indexed_file_name}')
            idx += 1
            time.sleep(self.interval)
            if stop_event.is_set():
                self.device.close()
                break
