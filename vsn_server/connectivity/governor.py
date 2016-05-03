import socket

from docker import Client


class DockerGovernor:
    def __init__(self, daemon_url: str):
        self._client = Client(daemon_url)
        self._container = None

    def run(self):
        print(socket.gethostbyname(socket.getfqdn()))
        if len(self._client.images('rivi/vsn')) != 0:
            print('image exists')
            # Image exists
            container = self._client.create_container(
                image='rivi/vsn', command='VSNClientPiCamera',
                host_config=self._client.create_host_config(binds={
                    '/dev/video0': {
                        'bind': '/dev/video0',
                        'mode': 'rw',
                    }
                }),
                environment={
                    'SERVER_ADDRESS': socket.gethostbyname(socket.getfqdn())
                }
            )
            print('Before start')
            container.start()
            print('After start')

            self._container = container
        else:
            print('image does not exist')
            print(self._client.pull('rivi/vsn', 'armv6h'))
            print('pull complete')

    def stop(self):
        self._container.stop()
        self._container.remove()
