#    Licensed under the Apache License, Version 2.0 (the "License"); you may

#    not use this file except in compliance with the License. You may obtain

#    a copy of the License at

#

#         http://www.apache.org/licenses/LICENSE-2.0

#

#    Unless required by applicable law or agreed to in writing, software

#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT

#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the

#    License for the specific language governing permissions and limitations

#    under the License.

import os
import sys

import unittest.mock as mock
from unittest.mock import Mock, patch
import paramiko
import pytest

sys.path.append(
    os.path.realpath(
        os.path.join(
            os.path.dirname(__file__), '../CheckFlux')))

import ssh_client


class fake_channel_file(object):

    def __init__(self, lines, channel=None):

        self.buf = iter(lines)

        self.channel = channel

    def __iter__(self):

        return self.buf


class TestSshClient(object):

    def test_init_with_hostname(self):
        flux = CheckFlux.CheckFlux('src', 'dst', 80)
        assert flux.src == 'src'
        assert flux.dst == 'dst'
        assert flux.port == 80

    def test_init_with_IP(self):
        flux = CheckFlux.CheckFlux('1.1.1.1', '2.2.2.2', 80)
        assert flux.src == '1.1.1.1'
        assert flux.dst == '2.2.2.2'
        assert flux.port == 80

    @mock.patch.object(paramiko.SSHClient, 'set_missing_host_key_policy')
    @mock.patch.object(paramiko.SSHClient, 'connect')
    def test_ssh_connect_is_ok(self, mock_conn, mock_set):
        flux = CheckFlux.CheckFlux('src', 'dst', 80)
        flux.ssh_connect('username', 'password')

        mock_conn.assert_called_with(
            hostname=flux.src, username='username',
            password='password', timeout=3)

    @mock.patch.object(paramiko.SSHClient, 'set_missing_host_key_policy')
    @mock.patch.object(paramiko.SSHClient, 'connect')
    def test_ssh_connect_is_not_ok(self, mock_conn, mock_set):
        flux = CheckFlux.CheckFlux('src', 'dst', 80)

        with pytest.raises(paramiko.ssh_exception.SSHException):
            flux.ssh_connect('username', 'password')

    @mock.patch.object(paramiko.SSHClient, 'set_missing_host_key_policy')
    @mock.patch.object(paramiko.SSHClient, 'connect')
    @mock.patch.object(paramiko.SSHClient, 'exec_command')
    def test_ssh_exec_command_is_ok(self, mock_exec, mock_conn, mock_set):

        mock_log = mock.Mock()

        mock_channel = mock.Mock()

        mock_exec.return_value = (fake_channel_file(['input']),

                                  fake_channel_file(['out_line1',

                                                     'out_line2'],

                                                    mock_channel),

                                  fake_channel_file(['err_line1',

                                                     'err_line2']))

        mock_channel.recv_exit_status.return_value = 0

        flux = CheckFlux.CheckFlux('host-src', 'host-dst', 80)
        command = 'nc ' + flux.dst + ' ' + str(flux.port)
        return_code, out, err = flux.ssh_exec_command(
                                                    flux.src,
                                                    'username',
                                                    'password',
                                                    command)
        return_code, out, err = client.ssh('fake_command')

        mock_log.debug.assert_called()

        mock_exec.assert_called()

        mock_log.info.assert_called_with('out_line1\nout_line2')

        mock_log.error.assert_called_with('err_line1\nerr_line2')

        mock_channel.recv_exit_status.assert_called_with()

        self.assertEqual(out, 'out_line1\nout_line2')

        self.assertEqual(err, 'err_line1\nerr_line2')

    @mock.patch.object(paramiko.SSHClient, 'set_missing_host_key_policy')
    @mock.patch.object(paramiko.SSHClient, 'connect')
    @mock.patch.object(paramiko.SSHClient, 'exec_command')
    def test_ssh_except(self, mock_exec, mock_conn, mock_set):

        mock_log = mock.Mock()

        mock_channel = mock.Mock()

        mock_exec.return_value = (fake_channel_file(['input']),

                                  fake_channel_file(['info'], mock_channel),

                                  fake_channel_file(['err']))

        mock_channel.recv_exit_status.return_value = -1

        client = sshclient.SSHClient('ip', 'username', password='password',

                                     log=mock_log)

        self.assertRaises(sshclient.SshExecCmdFailure,

                          client.ssh,

                          'fake_command')

    @mock.patch.object(paramiko.SSHClient, 'set_missing_host_key_policy')
    @mock.patch.object(paramiko.SSHClient, 'connect')
    @mock.patch.object(paramiko.SSHClient, 'exec_command')
    def test_ssh_allow_error_return(self, mock_exec, mock_conn, mock_set):

        mock_log = mock.Mock()

        mock_channel = mock.Mock()

        mock_exec.return_value = (fake_channel_file(['input']),

                                  fake_channel_file(['info'], mock_channel),

                                  fake_channel_file(['err']))

        mock_channel.recv_exit_status.return_value = 1

        client = sshclient.SSHClient('ip', 'username', password='password',

                                     log=mock_log)

        return_code, out, err = client.ssh('fake_command',

                                           allowed_return_codes=[0, 1])

        mock_exec.assert_called_once_with('fake_command', get_pty=True)

        mock_channel.recv_exit_status.assert_called_once()

        self.assertEqual(return_code, 1)
