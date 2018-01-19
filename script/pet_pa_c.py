import time
import logging
import telnetlib

class c_rf_device(object):
    def __init__(self, ip, port, inport_count, outport_count):
        self.ip = ip
        self.port = port
        self.inport_count = inport_count
        self.outport_count = outport_count
        self.conn = None
        self.logger = logging.getLogger(__file__)
        self.logger.info('PA [%s] Beginning' %(self.ip))

    def connect(self, retry = 'Y'):
        times = 60 if retry == 'Y' else 1
        self.logger.info('Try to connect to : %s:%s' %(self.ip, self.port))
        for i in range(times):
            try:
                self.conn = telnetlib.Telnet(self.ip, self.port)
                self.logger.info('Successfully connected to : %s:%s' %(self.ip, self.port))
                break
            except:
                self.logger.info('Connect to PA failed, I will try after 5 seconds')
                if times > 1:
                    time.sleep(5)
        if not self.conn:
            raise Exception, 'Could not connect to PA, case will failed!'


    def disconnect(self):
        if self.conn:
            self.conn.close()
            self.conn = None
            self.logger.info('Disconnect from : %s:%s' %(self.ip, self.port))

    def execute_commands(self, cmdlist = [], delay =0.5):
        if not self.conn:
            self.connect()
            time.sleep(1)
            response = self.conn.read_very_eager()
            self.logger.info('Get Response : ' +response)

        if self.conn:
            cmdlist = [cmdlist] if not isinstance(cmdlist, list) else cmdlist
            for cmd in cmdlist:
                self.conn.write(cmd+'\r\n')
                self.logger.info('Send command: ' +cmd)
                time.sleep(delay)
                response = self.conn.read_very_eager()
                self.logger.info('Get Response : ' +response)

    def change_signal(self, inport, outport, signal):
        pass

class c_jx_pa(c_rf_device):
    def clear_all(self):
        cmds = ['set %d, 120' %(x) for x in range(1, int(self.inport_count)+1)]
        self.execute_commands(cmds)

    def change_signal(self, inport, outport, signal):
        cmds = ['set %s, %s' %(inport, signal)]
        self.execute_commands(cmds)

class c_hb_pa(c_rf_device):
    def clear_all(self):
        cmds = ['$TA,C,%0.2dFE*' %(x) for x in range(1, int(self.inport_count)+1)]
        self.execute_commands(cmds, 0.2)

    def change_signal(self, inport, outport, signal):
        cmds = ['$TA,C,%0.2d%0.2X*' %(int(inport), int(signal)*2)]
        self.execute_commands(cmds, 0.2)

class c_jx_matrix(c_rf_device):
    def get_port_number(self, inport, outport):
        self.logger.info('A%sB%s' %(inport, outport))
        return (int(inport)-1)*int(self.outport_count) + int(outport)

    def clear_all(self, rfconnections):
        cmdlist1 = []
        scmd = 'set' if self.inport_count == 32 else 'SET'
        for rfconnection in rfconnections:
            for i in range(1, int(self.outport_count)+1):
                cmdlist1.append('%s:%d:93' %(scmd, self.get_port_number(rfconnection.inport, i)))
            for i in range(1,int(self.inport_count)+1):
                cmdlist1.append('%s:%d:93' %(scmd, self.get_port_number(i, rfconnection.outport)))
        self.execute_commands(cmdlist1, 0.1)

    def change_signal(self, inport, outport, signal):
        cmdlist1 = []
        cmdlist2 = []
        scmd = 'set' if self.inport_count == 32 else 'SET'
        cmdlist2.append('%s:%d:%d' %(scmd, self.get_port_number(inport, outport), int(signal)))
        cmdlist1 = list(set(cmdlist1))
        cmdlist1.sort()
        for cmd in cmdlist1 + cmdlist2:
            self.logger.info(cmd)
        self.execute_commands(cmdlist1 + cmdlist2, 0.1)

class c_hb_matrix(c_rf_device):
    def clear_all(self, rfconnections):
        for rfconnection in rfconnections:
            cmdlist = []
            self.logger.info('Adjust HB Matrix signal for %s 60'  %(rfconnection.inport))
            empty_row = 'FF'*(int(rfconnection.inport)-1) + '78'+'FF' * (int(self.inport_count) - int(rfconnection.inport))
            cmdlist.append('$TA,G,%s*' %(empty_row*int(self.outport_count)))

            self.logger.info('Adjust HB Matrix signal for %s 60'  %(rfconnection.outport))
            empty_col = 'FF'*int(self.inport_count)
            empty_col2 = empty_col*(int(self.outport_count) - int(rfconnection.outport))
            cmdlist.append('$TA,G,%s%s%s*' %(empty_col*(int(rfconnection.outport)-1),'78'* int(self.inport_count), empty_col2))
            self.execute_commands(cmdlist)

    def change_signal(self, inport, outport, signal):
        from pet_hbte_pam import RowOperate, ColumnOperate, OnePortOperate

        cmdlist = []
        # self.logger.info('Adjust HB Matrix signal for %s 60'  %(inport))
        # empty_row = 'FF'*(int(inport)-1) + '78'+'FF' * (int(self.inport_count) - int(inport))
        # cmdlist.append('$TA,G,%s*' %(empty_row*int(self.outport_count)))
        # # RowOperate(self.ip, str(int(inport)), '60')

        # self.logger.info('Adjust HB Matrix signal for %s 60'  %(outport))
        # # ColumnOperate(self.ip, str(int(outport)), '60')
        # empty_col = 'FF'*int(self.inport_count)
        # empty_col2 = empty_col*(int(self.outport_count) - int(outport))
        # cmdlist.append('$TA,G,%s%s%s*' %(empty_col*(int(outport)-1),'78'* int(self.inport_count), empty_col2))

        port = str((int(outport)-1)*int(self.inport_count)+ int(inport))
        self.logger.info('Adjust HB Matrix signal for signal port %s '  %(port))
        # OnePortOperate(self.ip, port, str(int(signal)))
        cmdlist.append('$TA,A,%0.2d%0.2d%0.2X*' %(int(inport), int(outport), 2*int(signal)))
        self.execute_commands(cmdlist)



if __name__ == '__main__':
    c = c_jx_pa('10.69.82.163', '23', 8, 2)
    try:
        c.connect()
        print 'connected'
        rfconnections = []
        from pet_ipalib import IpaMmlItem
        line = IpaMmlItem()
        line.inport = 1
        line.outport = 1
        rfconnections.append(line)
        c.clear_all()
    finally:
        c.disconnect()


    pass


