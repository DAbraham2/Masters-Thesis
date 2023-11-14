from paramiko.client import SSHClient, AutoAddPolicy


class SshTransport:
    def __init__(self, hostname: str, port: int = 22):
        self.__connect = SSHClient()
        self.__connect.set_missing_host_key_policy(AutoAddPolicy)
        self.__connect.connect(hostname, port=port)
        self.__connect.get_transport()
