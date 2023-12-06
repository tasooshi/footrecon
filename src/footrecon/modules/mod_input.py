import imageio
import sounddevice
import soundfile

from footrecon.core.logs import logger
from footrecon.core import modules


class Microphone(modules.Module):

    output_prefix = 'audio'
    output_suffix = '.wav'

    def setup(self, interval=1, samplerate=16000, channels=1, blocksize=16384):
        self.device = sounddevice.default.device[0]
        self.interval = int(interval)
        self.samplerate = int(samplerate)
        self.channels = int(channels)
        self.blocksize = int(blocksize)
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
            logger.debug(f'Module `{self.name}` did not find device')

    def task(self):
        with soundfile.SoundFile(self.output_file_name, mode='x', samplerate=self.samplerate, subtype='PCM_16', channels=self.channels) as fil:
            with sounddevice.RawInputStream(samplerate=self.samplerate, blocksize=self.blocksize, dtype='int16', device=self.device, channels=self.channels) as in_stream:
                for _ in self.loop:
                    sounddevice.sleep(int(1000 * self.blocksize / self.samplerate))
                    in_data, _ = in_stream.read(self.blocksize)
                    fil.buffer_write(in_data, dtype=in_stream.dtype)
                    logger.debug(f'Module `{self.name}` flushed buffer to {self.output_file_name}')


class Camera(modules.Module):

    output_prefix = 'picture-'
    output_suffix = '.jpg'
    device_id = '<video0>'

    def setup(self, interval=3, quality=80):
        self.interval = int(interval)
        self.quality = int(quality)
        try:
            self.device = imageio.get_reader(self.device_id)
        except IndexError:
            logger.debug(f'Module `{self.name}` did not find device')
        else:
            self.device_name = self.device_id

    def task(self):
        file_base = list(self.output_file_name.partition(self.output_suffix))
        for counter in self.loop:
            try:
                frame = self.device.get_next_data()
            except RuntimeError:
                break
            img = imageio.imwrite('<bytes>', frame, plugin='pillow', format='JPEG')
            indexed_file_name = file_base[0] + str(counter) + file_base[1]
            with open(indexed_file_name, 'wb') as fil:
                fil.write(img)
            logger.debug(f'Module `{self.name}` saved image to {indexed_file_name}')
        self.device.close()
