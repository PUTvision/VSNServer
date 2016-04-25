from docker import Client


class DockerGovernor:
    def __init__(self, daemon_url: str):
        self._client = Client(daemon_url)

    def check_image_status(self):
        print(self._client.images())

    def run(self):
        self.check_image_status()
