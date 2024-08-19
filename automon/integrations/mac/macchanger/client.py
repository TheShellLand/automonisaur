import sys
import random

from automon import log, Run

logger = log.logging.getLogger(__name__)
logger.setLevel(log.DEBUG)


class MacChanger(object):

    def __init__(self):
        self.mac_fixed = None
        self.mac_new = None

        self._run = Run()

    async def args_expansion(self, args: tuple) -> str:
        return ' '.join(args)

    async def ifconfig(self, *args, **kwargs):
        args = await self.args_expansion(args)
        return self._run.run(f'ifconfig {args}', **kwargs)

    @property
    async def is_ready(self):
        logger.debug(sys.platform)
        if sys.platform == 'darwin':
            return True

    async def random_mac(self) -> str:
        """return random mac address

        Example:
            return 3c:a6:f6:16:da:66
        """
        mac = []

        while len(mac) < 6:
            mac.append(
                random.choice(range(0, 255))
            )

        mac = [hex(x) for x in mac]
        mac = [str(x).split('x') for x in mac]
        mac = [list(x)[1] for x in mac]
        mac = ':'.join(mac)

        logger.debug(mac)

        return mac

    async def set_mac(self, mac: str, **kwargs):
        return await self.ifconfig('en0', 'link', mac, **kwargs)

    async def set_mac_random(self, **kwargs):
        return await self.set_mac(mac=await self.random_mac(), **kwargs)

    async def stdout(self):
        logger.debug(self._run.stdout)
        return self._run.stdout

    async def stderr(self):
        logger.debug(self._run.stderr)
        return self._run.stderr

    async def sudo_ifconfig(self, *args, stdin: str = None, **kwargs) -> bool:
        args = await self.args_expansion(args)
        return self._run.run(f'sudo -S ifconfig {args}', shell=True, stdin=stdin, **kwargs)
