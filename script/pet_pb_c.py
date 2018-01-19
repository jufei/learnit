from petbase import *
import os, time
import logging
import telnetlib

class c_pet_pb(IpaMmlItem):
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port

class c_pet_pb_facom(c_pet_pb):

    def power_op(self, op):
        import socket
        import binascii
        POWER_ON_PORT = ["01050000FF008C3A", "01050001FF00DDFA", "01050002FF002DFA", "01050003FF007C3A", "01050004FF00CDFB", "01050005FF009C3B"]
        POWER_OFF_PORT = ["010500000000CDCA", "0105000100009C0A", "0105000200006C0A", "0105000300003DCA", "0105000400008C0B", "010500050000DDCB"]
        try:
            p_Socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            p_Socket.connect((self.ip, 4001))
            portconfig = POWER_ON_PORT if op.upper() == 'ON' else POWER_OFF_PORT
            if p_Socket.send(binascii.a2b_hex(portconfig[int(port)-1])):
                gv.logger.info("Send message POWER_OFF_PORT_%s %s over socke success!" % (self.port, portconfig[int(self.port)-1]))
            else:
                raise Exception, "Send message POWER_OFF_PORT_%s %s over socke failed!" % (self.port, portconfig[int(self.port)-1])
        finally:
            p_Socket.close()

    def poweroff(self):
        slf.power_op('OFF')

    def poweron(self):
        slf.power_op('ON')

class c_pet_pb_apc(c_pet_pb):
    def _connect(self):
        self.prompt = '<ENTER>- Refresh, <CTRL-L>- Event Log'
        self.prompt_do = "Enter 'YES' to continue or <ENTER> to cancel"
        output = ''
        connected = False
        self.conn = None
        for i in range(60):
            try:
                self.logger.info('Try to connect APC for %d times: ' %(i+1))
                self.conn = telnetlib.Telnet(self.ip, 23)
                output += self.conn.read_until('User Name :', 5)
                self.conn.write('apc\n\r')
                output += self.conn.read_until('Password  :', 5)
                self.conn.write('apc\n\r')
                output += self.conn.read_until(prompt, 5)
                connected = True
                break
            except:
                self.logger.debug('Connect to APC failed, maybe connection is occupied by another process, I will try 5 seconds later.')
                time.sleep(5)
        self.logger.info(output)
        if not connected:
            raise Exception, 'Connect to APC Failed.'

    def send_commands(self, cmdlist, lastprompt):
        if self.conn :
            ret = ''
            for cmd in cmdlist:
                self.conn.write(cmd+'\n\r')
                prompt = lastprompt if lastprompt else self.prompt
                ret += self.conn.read_until(prompt)
            return ret

    def _disconnect(self):
        if self.conn:
            self.conn.close()

    def poweroff(self):
        output = ''
        output += self.send_commands([chr(27)*8])
        output += self.send_commands(['1', '2', '1', outlet, '1'])
        output += self.send_commands(['2'], self.prompt_do)
        output += self.send_commands(['YES'], 'Press <ENTER> to continue...')
        output += self.send_commands([''])
        self.logger.info(output)

    def poweron(self):
        output = ''
        output += self.send_commands(['1'], self.prompt_do)
        output += self.send_commands(['YES'], 'Press <ENTER> to continue...')
        output += self.send_commands([''])
        self.logger.info(output)

    def reboot():
        self._connect()
        self.poweroff()
        time.sleep(10)
        self.poweron()
        self._disconnect()





if __name__ == '__main__':
    pb = c_pet_pb_facom('10.69.2.134', '10')
    print pb
    # bts.connect_pc()