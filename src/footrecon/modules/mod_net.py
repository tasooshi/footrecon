import shlex
import subprocess

import requests

from footrecon.core.logs import logger
from footrecon.core import modules


class Ssh(modules.Module):

    interval = 60

    def setup(self, interval=60, host='127.0.0.1', port=22, remote_port=0, username=None, key=None):
        self.interval = int(interval)
        self.host = host
        self.port = int(port)
        self.remote_port = int(remote_port)
        self.username = username
        self.key = key
        if not all((self.username, self.key)):
            raise RuntimeError('Both `username` and `key` must be defined for Ssh module')

    def task(self):
        for _ in self.loop:
            failed = True
            ps = subprocess.Popen(shlex.split('netstat -ntap'), stdout=subprocess.PIPE)
            try:
                output = subprocess.check_output(shlex.split(fr'grep -E "{self.host}:{self.port}\s+ESTABLISHED\s+[0-9]+/ssh"'), stdin=ps.stdout)
            except subprocess.CalledProcessError:
                pass
            else:
                ps.wait()
                if output:
                    failed = False
                else:
                    logger.debug(f'Module `{self.name}` believes connection is established with {self.host}:{self.port}')
            if failed:
                logger.debug(f'Module `{self.name}` establishing SSH connection to {self.host}:{self.port}')
                subprocess.run(shlex.split(f'ssh -f -N -i {self.key} -o StrictHostKeyChecking=no -R{self.remote_port}:localhost:{self.port} {self.username}@{self.host}'))


class Healthcheck(modules.Module):

    timeout = 5

    def setup(self, interval=60, endpoint='http://127.0.0.1/?id='):
        self.interval = int(interval)
        self.endpoint = endpoint

    def task(self):
        for counter in self.loop:
            logger.debug(f'Module `{self.name}` sending GET request to {self.endpoint}')
            requests.get(self.endpoint + str(counter), timeout=self.timeout)
