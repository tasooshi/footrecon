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
    blocksize = 16384

    def __init__(self, *args):
        super().__init__(*args)
        self.queue = queue.Queue()

    def setup(self):
        self.device = sounddevice.default.device[0]
        found = True
        try:
            result = sounddevice.query_devices(self.device)
        except sounddevice.PortAudioError:
            found = False
        else:
            if self.device < 0:
                found = False
            else:
                if 'default_samplerate' in result:
                    self.samplerate = int(result['default_samplerate'])
        if found:
            self.device_name = '#' + str(self.device)
        else:
            logger.debug('Device not found for {}'.format(self.__class__.__name__))

    def task(self, output_file_name, stop_event):
        with soundfile.SoundFile(output_file_name, mode='x', samplerate=self.samplerate, subtype='PCM_16', channels=self.channels) as fil:
            with sounddevice.RawInputStream(samplerate=self.samplerate, blocksize=self.blocksize, dtype='int16', device=self.device, channels=self.channels) as in_stream:
                while True:
                    sounddevice.sleep(int(1000 * self.blocksize / self.samplerate))
                    in_data, _ = in_stream.read(self.blocksize)
                    fil.buffer_write(in_data, dtype=in_stream.dtype)
                    if stop_event.is_set():
                        break
