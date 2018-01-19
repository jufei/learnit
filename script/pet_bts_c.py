from petbase import *
import os, time
import logging
from pet_pc_c import c_control_pc
from pet_pb_c import c_pet_pb_facom
from pet_im_c import c_pet_im
from pet_btslog_c import c_pet_btslogger
from pet_xml import *
from robot.libraries import BuiltIn
from robot.utils import timestr_to_secs

earfcn_band = {
    '38':['37900', '38100'],
    '39':['38400', '38500'],
    '40':['38770', '38970', '39170'],
    '41':['40540', '40740', '40940'],
    '42':['42490', '42690', '42890'],
}

class c_pet_bts(IpaMmlItem):
    def __init__(self, btsid):
        self.btsid = btsid
        self.role = 'MASTER'
        self.config = None
        self.conn_bts = None
        self.conn_pc = None
        self.logger = logging.getLogger(__file__)
        self.scf_filename = ''
        self.scftree = None
        self.im = None
        self.btslogger = None
        self.work_dire = ''

    def _get_source_dire(self):
        curr_path = os.path.dirname(os.path.abspath(__file__))
        return os.sep.join(curr_path.split(os.sep) + ['config', 'bts', 'BTS%s'%(self.btsid)])

    def _initlize_bts_config(self):
        bts = self.config
        bts.workcell = 1
        bts.airscale = True if bts.airscale == '1' else False
        bts.bts_fcm_ip, bts.bts_fcm_username, bts.bts_fcm_password = '192.168.255.1','toor4nsn','oZPS0POrRieRtu'
        bts.bts_ftm_ip, bts.bts_ftm_username, bts.bts_ftm_password = '192.168.255.129','Nemuadmin','nemuuser'
        bts.mr_paging_ioc, bts.mr_paging_impair_ioc         = '140', '84'
        bts.mr_call_drop_ioc, bts.mr_call_drop_impair_ioc   = '140', '84'
        bts.mr_ho_ioc, bts.mr_ho_impair_ioc                 = '140', '84'
        bts.mr_volte_ioc, bts.mr_volte_impair_ioc           = '140', '84'
        bts.conn_bts = None
        bts.conn_pc = None
        bts.config_id = ''
        bts.used = True
        bts.lock_btslog = threading.Lock()
        bts.infomodel_pid = []
        bts.new_earfcn_list = []
        bts.new_eutraCarrierInfo_list = []
        bts.pcap_interface =  r'\Device\NPF_' + bts.pcap_interface.upper().split('NPF_')[-1]
        bts.scf_filename = ''

    def read_config(self):
        from pet_db import get_table_content
        btslist = get_table_content('tblbts')
        bts = [x for x in btslist if x.btsid == self.btsid]
        if not bts:
            raise Exception, 'Could not find bts config from DB: [BTS%s]' %(self.btsid)
        self.config = bts[0]
        self.conn_pc = c_control_pc(self.config.bts_control_pc_lab, '23',
            self.config.bts_control_pc_username, self.config.bts_control_pc_password)
        self.pb = c_pet_pb_facom(self.config.bts_powerbreak_port.split(':')[0], self.config.bts_powerbreak_port.split(':')[1])
        self._initlize_bts_config()

    def source_file(self, filename):
        if filename:
            return os.path.sep.join([self._get_source_dire(), filename])
        else:
            return self._get_source_dire()

    def work_file(self, filename):
        return os.path.sep.join([self.work_dire, filename])

    def s1_is_reachable(self):
        return os.system('ping -c 1 -W 1 %s >/dev/null' % (self.config.bts_ip)) == 0

    def fct_is_reachable(self):
        output = self.conn_pc.execute_command('ping %s -n 1' % (self.config.bts_fcm_ip))
        return 'Request timed out' not in output

    def fcm_is_reachable(self):
        output = self.conn_pc.execute_command('ping %s -n 1' % (self.config.bts_ftm_ip))
        return 'Request timed out' not in output

    def ssh_is_enable(self):
        import paramiko
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            client.connect(self.config.bts_ip, 22, self.config.bts_fcm_username, self.config.bts_fcm_password)
            channel = client.invoke_shell()
            ssh_ok = True
        except:
            ssh_ok = False
        finally:
            client.close()
        return ssh_ok

    def enable_ssh(self):
        import urllib, urllib2, base64
        auth_key = base64.encodestring('%s:%s' % (self.config.bts_ftm_username, self.config.bts_ftm_password))[:-1]
        query_args = { 'Username': self.config.bts_ftm_username,
                       'Password': self.config.bts_ftm_password,
                       'Validate1':'Validate2',
                       'EncodedCreds':auth_key}

        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
        new_auth = self.config.sw_release in ['TL16A', 'TL17', 'TRUNK']

        if new_auth:
            url_login = 'https://%s/protected/login.cgi' %self.config.bts_control_pc_lab
            print url_login
            loginpage = opener.open(url_login, urllib.urlencode(query_args)).read()
            self.logger.info(loginpage)

        request = urllib2.Request('https://%s/protected/sshservice.html' %self.config.bts_control_pc_lab)
        if not new_auth:
            request.add_header('Authorization', 'Basic %s' % auth_key)
        sshpage = opener.open(request).read()
        self.logger.info(sshpage)
        stamp = [line for line in sshpage.splitlines() if "name=stamp" in line][0].split('"')[1]
        token = [line for line in sshpage.splitlines() if "name=token" in line][0].split('"')[1]

        request = urllib2.Request('https://%s/protected/enableSsh.cgi?stamp=%s&token=%s&frame=sshservice' %(self.config.bts_control_pc_lab, stamp, token))
        if not new_auth:
            request.add_header('Authorization', 'Basic %s' % auth_key)
        enablepage = opener.open(request).read()
        self.logger.info(enablepage)
        if not 'SSH Service Enabled Successfully' in enablepage:
            raise Exception, 'Enable SSH of BTS failed, please check it first.'

    def wait_until_fct_is_reachable(self, timeout, interval):
        start_time = time.time()
        total_time = timestr_to_secs(timeout)
        while time.time() < start_time + timestr_to_secs(timeout):
            if self.fct_is_reachable():
                return 0
            else:
                time.sleep(int(interval))
        raise Exception, 'FCT is not reachable in specific time'

    def wait_until_s1_is_reacable(self, timeout, interval):
        start_time = time.time()
        total_time = timestr_to_secs(timeout)
        while time.time() < start_time + timestr_to_secs(timeout):
            if self.s1_is_reachable():
                return 0
            else:
                time.sleep(int(interval))
        raise Exception, 'FCT is not reachable in specific time'

    def get_ssh_prompt(self):
        import paramiko
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        result = '>'
        try:
            client.connect(self.config.bts_ip, 22, self.config.bts_fcm_username, self.config.bts_fcm_password)
            channel = client.invoke_shell()
            import time
            while not channel.recv_ready():
                time.sleep(0.5)
            results = channel.recv(1024)
        finally:
            client.close()
        prompt = results.strip()[-1]
        return prompt

    def connect_bts(self):
        if self.s1_is_reachable():
            if not bts.conn_bts:
                self.logger.info('Setup SSH connection for BTS: '+ self.btsid)
                prompt = self.get_ssh_prompt()
                self.conn_bts = connections.connect_to_ssh_host(self.config.bts_ip, '22',
                    self.config.bts_fcm_username, self.config.bts_fcm_password, prompt)
            else:
                connections.switch_ssh_connection(self.conn_bts)
        else:
            raise Exception, 'BTS S1 ip is not reacable, please check it.'

    def execute_command(self, cmds):
        self.connect_bts()
        if isinstance(cmds, list):
            output = ''
            for command in cmds:
                output += connections.execute_ssh_command_without_check(command)
            return output
        else:
            return connections.execute_ssh_command_without_check(cmds)

    def execute_command_local(self, cmd):
        if self.s1_is_reachable():
            tcmd = 'sshpass -p %s ssh %s@%s  %s' % (self.config.bts_fcm_password, self.config.bts_fcm_username, self.config.bts_ip, cmd)
            out = run_local_command_gracely(tcmd)
            output = [x.replace('\n', '') for x in out.splitlines()]
            return output
        else:
            raise Exception, 'BTS S1 ip is not reacable, please check it.'

    def upload_file(self, localfilename, remote_filename, remote_path):
        self.logger.info('upload file:  ' + remote_path + '/' + remote_filename)
        cmd = "sshpass -p '%s' scp %s %s@%s:%s" % (self.config.bts_fcm_password,
            localfilename, self.config.bts_fcm_username, self.config.bts_ip, remote_path + '/' + remote_filename)
        self.execute_command_local(cmd)

    def download_file(self, localfilename, remote_filename, remote_path):
        self.logger.info('download file:  ' + remote_path + '/' + remote_filename)
        cmd = "sshpass -p '%s' scp %s@%s:%s %s" % (self.config.bts_fcm_password,
            self.config.bts_fcm_username, self.config.bts_ip, remote_path + '/' + remote_filename, localfilename)
        run_local_command_gracely(cmd)

    def reboot(self):
        self.connect_bts()
        connections.SSHCONNECTION._current.write('reboot\n')
        result = False
        total_time = 120
        interval = 2
        st = time.time()
        while time.time() - st <= total_time:
            if self.fcm_is_reachable():
                time.sleep(interval)
            else:
                result = True
                break
        bts.conn_bts = None
        return result

    def reboot_by_pb(self):
        self.pb.poweroff()
        time.sleep(5)
        self.pb.poweron()

    def get_bts_version(self):
        output = self.execute_command_local('ls /ffs/run/Target*.xml')
        line = [x for x in output if '.xml' in x][0]
        self.bts_version = '_'.join(line.split('/')[-1].split('.xml')[0].split('_')[1:])

    def get_bbu_version(self):
        output =  self.execute_command_local('cat /proc/device-tree/module-identity/unit-id')
        self.bbu_version = output[0]

    def switch_active_version(self, target_version):
        curr_ver = self.get_bts_version()
        if target_version:
            if curr_ver <> target_version:
                output = self.execute_command('uboot_env get|grep active_partition')
                for line in output.splitlines():
                    if 'active_partition=' in line:
                        partion = line.split('=')[1]
                        np = '1' if partion == '2' else '2'
                        self.execute_command('uboot_env set active_partition=%s' % (np))
                        self.reboot_bts()
                        self.wait_until_fct_is_reachable()
                        break
        return curr_ver

    def forcely_recovery(self):
        if not self.fct_is_reachable():
            self.reboot_by_pb()
            self.wait_until_fct_is_reachable()
        if not self.ssh_is_enable():
            self.enable_ssh()

    def setup(self):
        self.read_config()
        self.conn_pc.setup()
        self.forcely_recovery()

    def teardown(self):
        self.conn_pc.teardown()

    def earfcn_to_frequency(self, earfcn):
        frequency_base = [x*10 for x in [1900, 2010, 1850, 1930, 1910, 2570, 1880, 2300, 2496, 3400, 3600, 703, 1447]]
        fcn_base = [36000, 36200, 36350, 36950, 37550, 37750, 38250, 38650, 39650, 41590, 43590, 45590, 46590, 46790]
        basefcn = [fcn for fcn in fcn_base if fcn <= int(earfcn)][-1]
        basefre = frequency_base[fcn_base.index(basefcn)]
        return int(earfcn) - basefcn + basefre

    def get_band_name(self, earfcn):
        fcn_base = [36000, 36200, 36350, 36950, 37550, 37750, 38250, 38650, 39650, 41590, 43590, 45590, 46590, 46790]
        fcn = [fcn for fcn in fcn_base if int(earfcn) >= fcn][-1]
        return 33 + fcn_base.index(fcn)

    def parse_scf_file(self, scf_file):
        scf = IpaMmlItem()
        scf.scftree = etree.parse(scf_file)
        from pet_scf_op_c import c_scf_looker
        scf.looker = c_scf_looker(scf.scftree)

        scf.cells = scf.looker.get_cells()
        scf.cell_count = len(scf.cells)

        scf.phycellid_list = [scf.looker.get_parameter_under_node(cell, 'phyCellId')[0].text for cell in scf.cells]
        scf.earfcn_list = [node.text for node in scf.looker.get_parameters('earfcn')]
        scf.frequency_list = [self.earfcn_to_frequency(x) for x in scf.earfcn_list]
        scf.dl_frequency_pcell = scf.frequency_list[0]
        scf.dl_frequency_scell = scf.dl_frequency_pcell if scf.cell_count == 1 else scf.frequency_list[1]
        scf.dl_frequency_tcell = scf.frequency_list[2] if scf.cell_count == 3 else 0
        scf.bandname = self.get_band_name(scf.earfcn_list[0])

        if hasattr(self.config, 'bts_physical_ids'):
            scf.phycellid_list = bts.config.bts_physical_ids.replace(';', ',').split(',')

        scf.antls = scf.looker.get_mos_distname('ANTL')
        idlist = [int(x.split('-')[-1]) for x in scf.antls]
        idlist.sort()
        scf.antls = ['-'.join(scf.antls[0].split('-')[:-1]) + '-' + str(x) for x in idlist]
        scf.lcells = scf.looker.get_mos('LCELL')
        scf.btsdistName = scf.looker.get_mos_distname('LNBTS')[0]
        scf.lnhoif = scf.looker.get_mos_distname('LNHOIF')
        scf.lnhoif.sort()
        self.scf = scf

    def cleanup_files(self):
        self.execute_command_local('rm -rf /flash/Hash*')

    def start_btslogger(self, casedire):
        self.btslogger = c_pet_btslogger(bts, casedire)
        self.btslogger.setup()

    def stop_btslogger(self):
        self.btslogger.stop_to_care()
        self.btslogger.teardown()

    def start_infomodel(self, casedire):
        self.im = c_pet_im(bts, casedire)
        self.im.setup()
        self.im.start_monitor()

    def stop_infomodel(self):
        self.im.teardown()

    def _is_onair_by_infomodel(self):
        cellstr = self.im.get_cell_object_name()
        if self.im:
            self.im.infomodel.query_infomodel('count %s is >= 1' % (cellstr), alias = self.im.im_alias)
            self.im.infomodel.query_infomodel('every %s is [stateInfo.proceduralState=onAirDone]' % (cellstr),
                alias = self.im.im_alias, timeout = 1)

    def wait_until_onair_by_infomodel(self, timeout, interval):
        start_time = time.time()
        total_time = timestr_to_secs(timeout)
        while time.time() < start_time + timestr_to_secs(timeout):
            try:
                self._is_onair_by_infomodel()
                self.logger.info('BTS is on Air now.')
                return 0
            except:
                traceback.print_exc()
                self.logger.info('BTS is not on Air, wait for check.')
                time.sleep(int(interval))
        raise Exception, 'Bts cound not be onAir by infomodel in specific time.'

    def wait_until_onair_by_btslog(self, timeout, interval):
        start_time = time.time()
        total_time = timestr_to_secs(timeout)
        while time.time() < start_time + timestr_to_secs(timeout):
            if 'onAirDone'.upper()  in ''.join(self.btslogger.buffer).upper():
                self.logger.info('BTS is on Air in btslog now.')
                return 0
            else:
                self.logger.info('BTS is not on Air, wait for check.')
                time.sleep(int(interval))
        raise Exception, 'Bts cound not be onAir by btslog in specific time.'


    def start_tshark(self):
        self.execute_command('tcpdump -i eth3 sctp -w /tmp/local.pcap &')

    def stop_tshark(self):
        self.execute_command('killall tcpdump')

    def get_new_earfcn(self, cellid, index):
        earfcn = [node.text for node in self.scf.looker.get_parameters('earfcn')][int(cellid)-1]
        bandname = self.get_band_name(earfcn)
        return earfcn_band[str(bandname)][index-1]

    def prepare_for_scf_generation(self):
        self.parse_scf_file(self.source_file(case.scf_file))

    def generate_scf_file_for_case(self, case, destfile):
        case.prepare_for_scf_genration(self)
        from pet_scf import get_scf_params_change_list
        import copy
        tempbts = copy.copy(self)
        for attr in [x for x in dir(self.scf) if x[0] <> '_']:
            setattr(tempbts, attr, getattr(self.scf, attr))
        for attr in [x for x in dir(self.config) if x[0] <> '_']:
            setattr(tempbts, attr, getattr(self.config, attr))
        changes = [] if case.fixed_scf else get_scf_params_change_list(tempbts, case)
        accept_changes = [x for x in changes if not 'delete' in x]
        src_xml_file = self.source_file(case.scf_file)
        if self.role <> 'MASTER':
            if case.slave_scf_file.strip():
                src_xml_file = self.source_file(self.source_file(case.slave_scf_file))
        from PetShell.file_lib.xml_control import common_xml_operation
        for change in [x for x in changes if 'delete' in x]:
            try:
                common_xml_operation(src_xml_file, 'dest_scf', [change])
                accept_changes.append(change)
            except:
                self.logger.info('Process  [%s] error' % (change))
        from pet_scf import show_scf_change_list
        show_scf_change_list(accept_changes)
        common_xml_operation(src_xml_file, destfile, accept_changes)

    def generate_swconfig_file(self, case):
        lines = [x.replace('\n', '') for x in open(self.source_file('swconfig.txt')).readlines()]
        lines += ['0x310001=0',  '0x310002=0']
        if case.case_type.upper() == 'LATENCY':
            lines = ['0x3A0001=1',
                     '0x10041=5',
                     '0x310001=0',
                     '0x310002=0', ]
        self.swconfig_file = os.sep.join([self.work_dire, 'swconfig_new.txt'])
        with open(self.swconfig_file, 'w') as f:
            for line in lines:
                f.write(line + '\n')

    def prepare_config_file(self, case):
        self.generate_swconfig_file(case)
        self.upload_file(self.swconfig_file, 'swconfig.txt', '/ffs/run')
        directory_path = '/ffs/run' if self.config.airscale else '/flash'
        self.download_file(self.work_file('FileDirectory.xml'), 'FileDirectory.xml', directory_path)
        from lxml import etree
        scf_filename = 'SCFC' + etree.parse(self.work_file('FileDirectory.xml')).xpath('//fileElement[@name="SCFC"and@activeFlag="TRUE"]')[0].get('version')
        self.scf_generated_filename = self.work_file(scf_filename)
        self.generate_scf_file_for_case(case, self.scf_generated_filename)
        # self.upload_file(self.scf_generated_filename, scf_filename, directory_path + '/config')



if __name__ == '__main__':
    bts = c_pet_bts('1450')
    bts.read_config()
    bts.setup()
    #bts.connect_pc()
    #bts.disconnect_pc()
    # bts.parse_scf_file(bts.source_file('scfc_cap.xml'))
    # bts.execute_command('ls -la /ram')
    # bts.execute_command_local('ls -la /ram')
    #bts.btslogger = c_pet_btslogger(bts, '/home/work/temp/7/')
    #bts.btslogger.setup()
    #bts.btslogger.start_to_care()
    #time.sleep(10)
    #bts.btslogger.stop_to_care()
    #bts.btslogger.teardown()
    print 'P1 passed'
    #bts.start_infomodel('/home/work/temp/7/')
    # bts.wait_until_onair_by_infomodel('100', '5')
    #bts.stop_infomodel()

    # from pet_case_c import c_pet_case
    # case = c_pet_case('304645')
    # # bts.generate_scf_file_for_case(case, '/tmp/new.xml')
    # bts.work_dire = '/home/work/temp/7/'
    # # bts.generate_swconfig_file(case)
    # bts.prepare_config_file(case)

    bts.teardown()
