import queue
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
        self.queue = queue.Queue()

    def setup(self):
        self.device = sounddevice.default.device[0]
        if self.device < 0:
            logger.debug('Device not found for {}'.format(self.__class__.__name__))
        else:
            self.device_name = '#' + str(self.device)

    def task(self, output_file_name, stop_event):

        def callback(indata, frames, time, status):
            self.queue.put(indata.copy(), status)

        with soundfile.SoundFile(output_file_name, mode='x', samplerate=self.samplerate, channels=self.channels) as file:
            with sounddevice.InputStream(samplerate=self.samplerate, device=self.device, channels=self.channels, callback=callback):
                while True:
                    try:
                        indata, status = self.queue.get_nowait()
                    except queue.Empty:
                        break
                    else:
                        file.write(indata)
                    if stop_event.is_set():
                        return
