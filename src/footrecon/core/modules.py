import datetime
import pathlib

from footrecon.core.logs import logger


class Module:

    output_prefix = 'tmp'
    output_suffix = '.tmp'

    def __init__(self):
        self.device = None
        self.device_name = ''
        self.setup()

    def output_file_name(self, dirname, idx=''):
        return str(pathlib.Path(dirname, self.output_prefix + str(idx) + self.output_suffix))

    def output_dir_create(self, dirname):
        pathlib.Path(dirname).mkdir(parents=True, exist_ok=True)

    def setup(self):
        raise NotImplementedError

    def execute(self, output_dir_name, stop_event):
        logger.info('Executing {}'.format(self.__class__.__name__))
        module_dir_name = pathlib.Path(output_dir_name, self.__class__.__name__.lower())
        self.output_dir_create(module_dir_name)
        output_file_name = self.output_file_name(module_dir_name)
        self.task(output_file_name, stop_event)

    def task(self, output_file_name):
        raise NotImplementedError

    def cleanup(self):
        pass

    def isodatetime(self):
        return datetime.datetime.utcnow().isoformat() + 'Z'
