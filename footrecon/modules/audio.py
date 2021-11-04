import asyncio

import sounddevice
import soundfile

from footrecon.core.logs import logger
from footrecon.core import modules


__all__ = ['Audio']


class Audio(modules.Module):

    output_prefix = 'audio'
    output_suffix = '.wav'
    samplerate = 44100
    channels = 1

    def __init__(self, *args):
        super().__init__(*args)
        self.queue = asyncio.Queue()

    def setup(self):
        try:
            self.device = sounddevice.default.device[0]
        except Exception as exc:
            logger.debug('Device not found for {}'.format(self.__class__.__name__))
        else:
            self.device_name = '#' + str(self.device)

    async def task(self):
        loop = asyncio.get_event_loop()

        def callback(indata, frames, time, status):
            loop.call_soon_threadsafe(self.queue.put_nowait, (indata.copy(), status))

        filename = self.output_file_name()
        with soundfile.SoundFile(filename, mode='x', samplerate=self.samplerate, channels=self.channels) as file:
            with sounddevice.InputStream(samplerate=self.samplerate, device=self.device, channels=self.channels, callback=callback):
                while self.app.running:
                    indata, status = await self.queue.get()
                    file.write(indata)
