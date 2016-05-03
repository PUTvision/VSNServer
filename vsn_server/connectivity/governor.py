import socket

from docker import Client


class DockerGovernor:
    def __init__(self, daemon_url: str, hostname: str):
        self._client = Client(daemon_url)
        self._client_hostname = hostname
        self._container_id = None

    def run(self):
        if len(self._client.images('rivi/vsn')) != 0:
            print('image exists')
            # Image exists
            self._container_id = self._client.create_container(
                image='rivi/vsn:armv6h', command='VSNClientCV',
                host_config=self._client.create_host_config(devices=[
                    '/dev/video0:/dev/video0:rwm'
                ]), hostname=self._client_hostname, environment={
                    'SERVER_ADDRESS': socket.gethostbyname(socket.getfqdn())
                }
            ).get('Id')
            print('Before start')
            response = self._client.start(container=self._container_id)
            print('After start')
        else:
            print('image does not exist')
            print(self._client.pull('rivi/vsn', 'armv6h'))
            print('pull complete')

    def stop(self):
        self._container.stop()
        self._container.remove()
