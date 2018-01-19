from petbase import *
import os
import logging

class c_control_pc(IpaMmlItem):
    def __init__(self, ip, port, username, password):
        self.ip = ip
        self.port = port
        self.username = username
        self.password = password
        self.conn = None
        self.logger = logging.getLogger(__file__)

    def conn_is_available(self):
        output = os.popen('netstat -na|grep %s' % (self.ip)).read()
        return 'ESTABLISHED' in output

    def connect(self):
        if not self.conn or not self.conn_is_available():
            self.conn = connections.connect_to_host(self.ip, '23', self.username, self.password)
        connections.switch_host_connection(self.conn)

    def disconnect(self):
        if self.conn:
            connections.switch_host_connection(self.conn)
            connections.disconnect_from_host()

    def execute_command(self, cmds):
        if isinstance(cmds, list):
            output = ''
            for command in cmds:
                output += connections.execute_shell_command_without_check(command)
            return output
        else:
            return connections.execute_shell_command_without_check(cmds)

    def check_telnet_server(self):
        self.connect()
        self.execute_command(['tlntadmn config timeoutactive=no',
                                    'tlntadmn config maxconn=1000'])

    def check_passport(self):
        servicename = '"PassPort (port forwarding)"'
        output = self.execute_command('sc query ' + servicename)
        if not 'RUNNING' in output:
            return self.execute_command('sc start ' + servicename)

    def wait_until_port_is_listening(self, port_num, timeout = '5'):
        for i in range(int(timeout)):
            output = self.execute_command('netstat -na|grep %s' %(str(port_num)))
            if 'LISTENING' in output:
                return 0
            else:
                time.sleep(1)
        raise Exception, 'Cound not find port [%s] listening in [%s] seconds' %(port_num, timeout)

    def kill_process(processes):
        if isinstance(processes, list) or isinstance(processes, set):
            for process in processes:
                cmd = 'TASKKILL /F /IM "%s"' %(process)
                ret = self.execute_command(cmd)
        else:
            cmd = 'TASKKILL /F /IM  "%s"' %(processes)
            ret = self.execute_command(cmd)
        return ret

    def setup(self):
        self.connect()
        self.check_telnet_server()
        self.check_passport()

    def teardown(self):
        self.disconnect()

