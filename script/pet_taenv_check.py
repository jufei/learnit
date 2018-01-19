from pet_bts import *
from pet_tm500 import *
from pettool import *

from optparse import *


class env_check():
    def __init__(self):
        self.env = IpaMmlItem()
        self.read_env_variables()

    def read_env_variables(self):
        for key in os.environ.keys():
            setattr(self.env, key.lower().replace(' ','_'), os.environ[key])

        if self.has_attr('bts_id') or self.has_attr('tm500_id'):
            return
        else:

            parser = OptionParser()
            parser.add_option("-e",  dest="bts_id",default='537',help='Sepcific the bts id, such as :BTS537 or BTS1703 and so on')
            parser.add_option("-w",  dest="tm500_id",default='233',help='Sepcific the tm500 id, such as: TM500_233 or TM500_225 and so on')

            (options, sys.argv[1:]) = parser.parse_args()

            setattr(self.env,'bts_id', options.bts_id.upper())
            setattr(self.env,'tm500_id', options.tm500_id.upper())

    def has_attr(self, attrname):
        return attrname.lower() in [x.lower().strip() for x in dir(self.env) if x[0] <> '_']

    def check_bts(self):
        print self.env.bts_id.lower().strip().replace('bts','')
        bts = read_bts_config(self.env.bts_id.lower().strip().replace('bts',''))
        print bts
        gv.master_bts = bts
        gv.allbts =[]
        gv.allbts.append(bts)
        config_bts_control_pc(bts.btsid)
        output = cpc_pre_check_tmp(bts.btsid)
        if 'fail' in output:
            raise Exception(output)
        makesure_passport_is_running(bts.conn_pc)
        start_btslog_pcap_server_if_needed_tmp(bts.btsid)
        start_tshark_on_bts_tmp(gv.master_bts.bts_id)
        start_infomodel_logging(gv.master_bts.bts_id)
        self.bts_teardown(bts)
        print '******************ok!TA env is healthy~~~********************'


    def check_tm500(self):
        gv.tm500 = read_tm500_config_tmp(self.env.tm500_id.lower().strip().replace('tm500_',''))
        start_console_server_if_needed_tmp()
        gv.tm500.conn_tm500_console = telnetlib.Telnet(gv.tm500.tm500_control_pc_lab, '30002')
        start_new_thread(console_monitor_thread ,())
        download_filezilla_file()
        try_to_disconnect_connection_to_apc_tmp(gv.tm500.tm500_powerbreak_port)
        if gv.tm500.use_asc:
            setup_asc_before_tm500_restart()
            if hasattr(gv.tm500, 'asc_powerbreaks'):
                for pbconfig in gv.tm500.asc_powerbreaks:
                    kw('pet_restart_device_by_power_break_apc', pbconfig, interval)
        # pet_restart_device_by_power_break_apc(gv.tm500.tm500_powerbreak_port, 10)
        pet_disconnect_tma()
        gv.tm500.conn_tma =True
        gv.env.use_tm500 =True
        self.tm500_teardown()
        print '******************ok!TA env is healthy~~~********************'

    def bts_teardown(self,bts):
        stop_cmdagent()
        execute_command_on_bts(bts.bts_id,'killall tcpdump')
        stop_infomodel_logging(bts.bts_id)
        self.clean_bts_conn()


    def tm500_teardown(self):
        stop_console_server_if_needed_tmp()
        stop_to_capture_all_kinds_of_logs()
        stop_to_monitor_tm500_console_output()
        self.clean_tm500_conn()

    def clean_bts_conn(self):
        import os
        gv.logger.info('Before Close connections:')
        for line in os.popen('netstat -na |grep %s' %(gv.master_bts.bts_control_pc_lab)).readlines():
            gv.logger.info(line)
        connections.disconnect_all_hosts()
        connections.disconnect_all_ssh()
        gv.logger.info('After Close connections:')
        for line in os.popen('netstat -na |grep %s' %(gv.master_bts.bts_control_pc_lab)).readlines():
            gv.logger.info(line)
        for bts in gv.allbts:
            bts.conn_pc = None
            bts.conn_bts = None

    def clean_tm500_conn(self):
        connections.disconnect_all_hosts()
        connections.disconnect_all_ssh()
        if gv.env.use_tm500:
            if gv.tm500:
                gv.tm500.conn_pc = None

    def run(self):
        if self.has_attr('tm500_id'):
            self.check_tm500()
        else:
            self.check_bts()



def download_filezilla_file():
    filename = '/home/work/temp/ftpserver.xml'
    if has_attr(gv.tm500, 'filezilla_path'):
        if gv.tm500.filezilla_path:
            url = 'ftp://%s/%s/FileZilla Server.xml' %(gv.tm500.tm500_control_pc_lab, gv.tm500.filezilla_path)
    else:
        url = 'ftp://%s//Program Files/FileZilla Server/FileZilla Server.xml' %(gv.tm500.tm500_control_pc_lab)
    print url
    download_from_ftp_to_local(url, filename, 'bin', 'filec', 'filec')

def care_bts_health(bts):
    start_to_monitor_btslog(bts.btsid)
    pet_prepare_infomodel(bts.btsid)
    start_to_monitor_infomodel(bts.btsid)
    bts.conn_bts = None

def cpc_pre_check_tmp(btsid=''):
    connect_to_bts_control_pc(btsid)
    portlist = [12345, 15003, 15007]
    if gv.env.use_single_oam:
        portlist += [12347]
    for portnum in portlist:
        output = connections.execute_shell_command_without_check('netstat -na|grep %s' %(str(portnum)))
        if 'LISTENING' not in output:
            print('Port {} is not listening, TA will fail for it. Check passport configuration.'.format(portnum))
            return 'Port {} is not listening, TA will fail for it. Check passport configuration.'.format(portnum)
    return 'PASS'

def start_btslog_pcap_server_if_needed_tmp(btsid = ''):
    from pet_bts import _get_bts
    bts = _get_bts(btsid)
    connect_to_bts_control_pc(btsid)
    output = execute_command_on_bts_control_pc_without_check(btsid, 'netstat -nao|grep 30003')
    for line in output.splitlines():
        if 'LISTENING' in line:
            pid = line.split()[-1]
            execute_command_on_bts_control_pc_without_check(btsid, 'taskkill /PID %s /F' % (pid))
    cmd = 'psexec -i -d -u %s -p %s c:\\python27\\python.exe  c:\\python27\\btslog_pcap.py' % (bts.bts_control_pc_username, bts.bts_control_pc_password)
    cmd += ' -i %s -s 51000 ' % (bts.pcap_interface)
    gv.logger.info(cmd)
    execute_command_on_bts_control_pc_without_check(btsid, cmd)
    wait_until_port_is_listening('30003', '40')
    execute_command_on_bts_control_pc_without_check(btsid, 'netstat -nao|grep 30003')



def tear_down(bts):


    stop_cmdagent()
    stop_console_server_if_needed_tmp()
    stop_to_capture_all_kinds_of_logs()
    stop_to_monitor_tm500_console_output()
    clean_all_connections()


def read_tm500_config_tmp(tm500_id):
    tm500path = os.path.sep.join([resource_path(), 'config', 'tm500'])
    import sys, importlib
    sys.path.append(tm500path)
    model = importlib.import_module('tm500_%s'%(tm500_id))
    tm500config = IpaMmlItem()
    for key in model.TOOLS_VAR:
        setattr(tm500config, key.lower(), model.TOOLS_VAR[key])

    if hasattr(tm500config, 'use_asc'):
        value = str(tm500config.use_asc).upper() in ['Y', 'YES', 'TRUE']
        setattr(tm500config, 'use_asc', value)
    else:
        setattr(tm500config, 'use_asc', False)

    tm500config.conn_pc = None
    tm500config.conn_tma = None
    tm500config.conn_shenick = None
    tm500config.version = ''
    tm500config.output = ''
    tm500config.tm500_restarted = False
    tm500config.conn_tm500_console = None
    tm500config.shenick_volte_group_name = 'TA_VOLTE_IMS_FTP'
    tm500config.asc = None

    return tm500config

def try_to_disconnect_connection_to_apc_tmp(cmdstr):
    ip = cmdstr.split(':')[0]
    output = execute_command_on_tm500_control_pc('netstat -nao |grep '+ip)
    for line in [x for x in output.splitlines() if 'ESTABLISHED' in x]:
        pid = line.split()[-1].strip()
        execute_command_on_tm500_control_pc('taskkill /F /PID '+pid)

def start_console_server_if_needed_tmp():
    connect_to_tm500_control_pc()
    stop_console_server_if_needed_tmp()
    kill_process(['hypertrm.exe', 'SecureCRT.exe', 'PUTTY.exe', 'HBTE Power Creator V6.0.0.8.exe', 'ProgrammableAttenuatorMatrix.exe'])
    connections.execute_shell_command_without_check('psexec -u %s -p %s -i -d c:\\python27\\python c:\\python27\\serial_server.py -r %s' %(gv.tm500.tm500_control_pc_username, gv.tm500.tm500_control_pc_password, gv.tm500.console_rate))
    wait_until_port_is_listening('30002', '5')

def stop_console_server_if_needed_tmp():
    stop_to_monitor_tm500_console_output_tmp()
    connect_to_tm500_control_pc()
    output = connections.execute_shell_command_without_check('netstat -nao|grep 30002')
    for line in output.splitlines():
        if 'LISTENING' in line:
            pid = line.split()[-1]
            connections.execute_shell_command_without_check('taskkill /PID %s /F' %(pid))

def start_tshark_on_bts_tmp(btsid = ''):
    from pet_bts import _get_bts
    bts = _get_bts(btsid)
    execute_command_on_bts(btsid, 'killall tcpdump')
    interface = 'br1' if bts.airscale  else 'eth3'
    execute_command_on_bts(btsid, 'tcpdump -i %s sctp -w /tmp/local.pcap &' %(interface))

def stop_to_monitor_tm500_console_output_tmp():
    if gv.tm500.conn_tm500_console:
        execute_command_on_tm500_console('pca_Show')
        with console_lock:
            gv.tm500.conn_tm500_console.close()
            gv.tm500.conn_tm500_console = None



if __name__ == '__main__':
    envcheck = env_check()
    envcheck.run()
