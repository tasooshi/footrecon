import asyncio
import pathlib
import subprocess

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
        except Exception as exc:
            logger.debug('Device not found for {}'.format(self.__class__.__name__))
        else:
            self.device_name = self.device_id

    def output_file_name(self, output_dir, idx=''):
        return str(pathlib.Path(output_dir, self.output_prefix + str(idx) + self.output_suffix))

    async def task(self):
        output_dir = pathlib.Path(self.session.output_dir, 'camera')
        logger.debug(f'Writing output to {output_dir}')
        self.session.output_dir_create(output_dir)
        idx = 1
        while self.app.running:
            frame = self.device.get_next_data()
            img = imageio.imwrite('<bytes>', frame, plugin='pillow', format='JPEG')
            filename = self.output_file_name(output_dir, idx)
            with open(filename, 'wb') as fil:
                fil.write(img)
            logger.debug(f'Saved image to {filename}')
            idx += 1
            await asyncio.sleep(self.interval)
        self.device.release()
