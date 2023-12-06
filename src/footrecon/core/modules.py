import datetime
import pathlib
import threading

from footrecon.core.logs import logger


class Loop:

    def __init__(self, stop_event, interval):
        self.stop_event = stop_event
        self.sleep_event = threading.Event()
        self.interval = interval
        self.counter = 1

    def __iter__(self):
        while not self.stop_event.is_set():
            yield self.counter
            self.sleep_event.wait(timeout=self.interval)
            self.counter += 1


class Module:

    output_prefix = 'tmp'
    output_suffix = '.tmp'

    def __init__(self, stop_event, **config):
        self.name = self.__class__.__name__
        self.module_path = config.pop('module_path')
        self.output_dir_name = None
        self.output_file_name = None
        self.stop_event = stop_event
        self.device = None
        self.device_name = ''
        self.enabled = config.pop('enabled')
        self.config = config
        self.setup(**config)

    def output_dir_create(self, dirname):
        pathlib.Path(dirname).mkdir(parents=True, exist_ok=True)

    def setup(self):
        raise NotImplementedError

    def execute(self):
        logger.info(f'Executing {self.name}')
        module_dir_name = pathlib.Path(self.output_dir_name, self.name.lower())
        if self.interval:
            self.loop = Loop(self.stop_event, self.interval)
        self.output_dir_create(module_dir_name)
        self.output_file_name = str(pathlib.Path(module_dir_name, self.output_prefix + self.output_suffix))
        self.task()

    def task(self, output_file_name):
        raise NotImplementedError

    def isodatetime(self):
        return datetime.datetime.utcnow().isoformat() + 'Z'
