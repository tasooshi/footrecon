import datetime
import pathlib
import asyncio

import footrecon
from footrecon.core.logs import logger


class Session:

    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.output_dir = self.output_dir_name()
        self.output_dir_create(self.output_dir)

    def output_dir_name(self):
        name_date = datetime.datetime.now().strftime('%Y%m%d_%H%M')
        name = footrecon.name_lower + '-' + name_date
        suffix = 0
        while pathlib.Path(name).exists():
            suffix += 1
            name = footrecon.name_lower + '-' + name_date + '-' + str(suffix)
        return name

    def output_dir_create(self, dirname):
        pathlib.Path(dirname).mkdir(parents=True, exist_ok=True)


class Module:

    output_prefix = 'tmp'
    output_suffix = '.tmp'

    def __init__(self, app, executor):
        self.app = app
        self.device = None
        self.device_name = ''
        self.session = None
        self.executor = executor
        self.setup()

    def output_file_name(self, idx=''):
        return str(pathlib.Path(self.session.output_dir, self.output_prefix + str(idx) + self.output_suffix))

    def setup(self):
        raise NotImplementedError

    async def execute(self, session):
        logger.info('Executing {}'.format(self.__class__.__name__))
        self.session = session
        await self.task()

    def task(self):
        raise NotImplementedError

    def isodatetime(self):
        return datetime.datetime.utcnow().isoformat() + 'Z'
