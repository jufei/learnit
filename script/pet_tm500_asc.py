from petbase import *

class asc_manager(IpaMmlItem):

    def __init__(self, tm500 = None):
        self.tm500 = tm500
        self.conn = None
        self.logger = logging.getLogger(__file__)

    def connect(self):
        if not self.conn:
            gv.logger.info('Setup SSH connection for ASC: '+ self.tm500.tm500_control_pc_lab)
            self.conn = connections.connect_to_ssh_host(self.tm500.tm500_control_pc_lab, '22', 'switch', 'switch',':')
        else:
            connections.switch_ssh_connection(self.conn)

    def execute_command(self, cmds):
        self.connect()
        if isinstance(cmds, list):
            output = ''
            for command in cmds:
                output += connections.execute_ssh_command_without_check(command)
            return output
        else:
            return connections.execute_ssh_command_without_check(cmds)


    def power_on(self):
        output = self.execute_command(['username "%s"'%(self.tm500.asc_user),'setpower ON "%s"'%(self.tm500.asc_group)])

    def power_off(self):
        output = self.execute_command(['username "%s"'%(self.tm500.asc_user), 'setpower OFF "%s"'%(self.tm500.asc_group)])

    def lock_resource(self):
        output = self.execute_command(['username "%s"'%(self.tm500.asc_user), 'lockgroup "%s"'%(self.tm500.asc_group)])

    def unlock_resource(self):
        output = self.execute_command(['username "%s"'%(self.tm500.asc_user),'unlockgroup "%s"'%(self.tm500.asc_group)])

    def disconnect(self):
        if self.conn:
            connections.switch_ssh_connection(self.conn)
            connections.disconnect_from_ssh()
            self.conn = None

    def onBeforeTm500Restart(self):
        self.power_off()
        self.unlock_resource()

    def onAfterTm500Restart(self):
        self.lock_resource()
        self.power_on()
        self.disconnect()


if __name__ == '__main__':

    gv.team = 'PET1'
    # gv.case = IpaMmlItem()
    # from pettool import get_case_config
    # gv.case.curr_case = get_case_config('529817')
    # from petcasebase import re_organize_case
    # re_organize_case()
    # print gv.case.curr_case

    # from pet_tm500 import read_tm500_config

    # gv.tm500 = read_tm500_config(88)
    # print gv.tm500
    # power_off_unlock_res_ASC(gv.tm500)
    # power_on_lock_res_ASC(gv.tm500)
    pass