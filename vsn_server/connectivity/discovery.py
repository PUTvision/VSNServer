from struct import unpack

from zeroconf import ServiceBrowser, Zeroconf, ServiceInfo

from vsn_server.connectivity.governor import DockerGovernor


class DockerFinder:
    def __init__(self):
        self._zeroconf = Zeroconf()
        self._browser = ServiceBrowser(self._zeroconf, '_docker-s._tcp.local.',
                                       self)
        self._governors = {}

    def remove_service(self, zeroconf, type, name):
        info = zeroconf.get_service_info(type, name)  # type: ServiceInfo
        del self._governors[info.server]

    def add_service(self, zeroconf, type, name):
        info = zeroconf.get_service_info(type, name)  # type: ServiceInfo
        url = 'tcp://{}:{}'.format(
            '.'.join(map(str, unpack('BBBB', info.address))), info.port
        )

        governor = DockerGovernor(url)
        self._governors[info.server] = governor
        governor.run()
