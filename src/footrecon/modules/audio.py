import queue
import sounddevice
import soundfile

from footrecon.core.logs import logger
from footrecon.core import modules


__all__ = ['Audio']


class Audio(modules.Module):

    output_prefix = 'audio'
    output_suffix = '.wav'
    samplerate = 16000
    channels = 1

    def __init__(self, *args):
        super().__init__(*args)
        self.queue = queue.Queue()

    def setup(self):
        self.device = sounddevice.default.device[0]
        result = sounddevice.query_devices(self.device)
        if 'default_samplerate' in result:
            self.samplerate = int(result['default_samplerate'])
        if self.device < 0:
            logger.debug('Device not found for {}'.format(self.__class__.__name__))
        else:
            self.device_name = '#' + str(self.device)

    def task(self, output_file_name, stop_event):

        def callback(indata, frames, time, status):
            self.queue.put(bytes(indata))

        with soundfile.SoundFile(output_file_name, mode='x', samplerate=self.samplerate, subtype='PCM_16', channels=self.channels) as fil:
            with sounddevice.RawInputStream(samplerate=self.samplerate, blocksize=16384, dtype='int16', device=self.device, channels=self.channels, callback=callback) as in_stream:
                while not self.queue.empty():
                    indata = self.queue.get()
                    fil.buffer_write(indata, dtype=in_stream.dtype)
                    if stop_event.is_set():
                        break
