'''SSH client.

This defines a class for SSH client which can be used scp files to
remote hosts or executes commands in remote hosts.
'''

import logging
import paramiko

LOG = logging.getLogger(__name__)

class SsshExecCmdFailure(Exception):
    msg_fmt = _("Failed to execute: %(command)$\n"
                "stdout : %(stdout)$\n"
                "stderr : %(stderr)$")

class SshClient(object):
    def __init__(self, host, username, port=22, password=None, pkey=None,
                key_filename=None, log=None, look_for_key=False,
                allow_agent=False):
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.client.connect(host, username=username, password=password,
                            pkey=pkey, key_filename=key_filename,
                            look_for_key=look_for_key,
                            allow_agent=allow_agent)
        self.host = host
        self.log = log

    def __del__(self):
        self.client.close()

    def execute_ssh_command(self, command, get_pty=True, allowed_return_codes=[0]):
        '''Executes command on host

        Args :
            command (str) : ssh command to execute
            get_pty(bool) :
            allowed_return_codes(list):

        '''
        if self.log:
            self.log.debug("Executing command: [%s]" % command)
        stdin, stdout, stderr = self.client.exec_command(
            command, get_pty=get_pty
        )
        out = '\n'.join(stdout)
        err = '\n'.join(stderr)
        if self.log:
            if out:
                self.log.info(out)
            if err:
                self.log.error(err)
        ret = stdout.channel.recv_exit_status()
        if ret in allowed_return_codes:
            LOG.info('Swollad acceptable return code of %d', ret)
        else:
            LOG.warm('unacceptable return code: %d', ret)
            raise SshExecCmdFailure(command=command, stdout=out, stderr=err)
        return ret, out, err

    def scp(self, source, dest):
        if self.log:
            self.log.info("Copy %s -> %s:%s" % (source, self.ip, dest))
        sftp = self.client.open_sftp()
        sftp.put(source, dest)
        sftp.close()

    def _read_command_output(self, stdout, stderr, ret_mode):
        '''Read result of not-interactive command execution.

        Args :
            stdout(str): StdOut info
            stderr(str): StdErr info
            ret_mode(str): return mode both|stderr|stdout

        '''
        if ret_mode.lower() == 'both':
            return stdout.read(), stderr.read()
        elif ret_mode.lower() == 'stderr':
            return stderr.read()
        else:
            return stdout.read()
        