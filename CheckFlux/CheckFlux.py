import os
import sys

import paramiko


class CheckFlux(object):
    '''Class check flux.
    It connect to src server (via ssh) and
    check if the connection to dst:port is allowed
    parameters:
        src : IP address or hostname
        dst : IP address or hostname
        port : TCP port (int)
    '''
    def __init__(self, src, dst, port):
        self.src = src
        self.dst = dst
        self.port = port

    def ssh_connect(self, user, pwd):
        try:
            with paramiko.SSHClient.connect(hostname=self.src,
                                            username=user,
                                            password=pwd,
                                            timeout=3) as client:
                return client
        except paramiko.SSHException:
            print("Check if %s is UP".format(self.src))

    def ssh_exec_command(self, client, user, password, cmd):
        pass

    def check_flux(src, dst, port):
        pass

if __name__ == "__main__":
    pass
