import threading, datetime, select
from robot.utils import timestr_to_secs
from thread import *
from petbase import *
import zipfile
import tempfile
import logging

def updateZip(zipname, filename, data):
    tmpfd, tmpname = tempfile.mkstemp(dir=os.path.dirname(zipname))
    os.close(tmpfd)
    with zipfile.ZipFile(zipname, 'r') as zin:
        with zipfile.ZipFile(tmpname, 'w') as zout:
            zout.comment = zin.comment # preserve the comment
            for item in zin.infolist():
                if item.filename != filename:
                    zout.writestr(item, zin.read(item.filename))

class c_prisma_ssh(object):
    def __init__(self, ip, port='22', username='user', password='user', prompt = '/home/user$'):
        self.ip = ip
        self.port = port
        self.username = username
        self.password = password
        self.prompt = prompt
        self.conn = None
        self.monitor_buffer = ''
        self.monitor = False
        self.logfilename = ''
        self.nickname = ''
        self.logger     = logging.getLogger(__name__)


    def set_logfile(self, filename):
        self.logfilename = filename

    def connect(self):
        if self.nickname:
            self.logger.info('Switch to : '+ self.nickname)
        if not self.conn:
            self.conn = connections.connect_to_ssh_host(self.ip, self.port, self.username, self.password, self.prompt)
        connections.switch_ssh_connection(self.conn)

    def start(self):
        self.connect()
        start_new_thread(self.readoutput_thread, ())

    def disconnect(self):
        if self.conn:
            connections.switch_ssh_connection(self.conn)
            connections.disconnect_from_ssh()
            self.conn = None

    def save_log(self, output):
        if self.logfile:
            now = datetime.datetime.now()
            with open(self.logfile, 'a') as f:
                for line in [x for x in output.splitlines()]:
                    if line.strip():
                        f.write('%s  %-100s\n' %(now.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3], line.replace('\n', '')))
        else:
            self.logger.info("No System Manager output file name")


    def execute_command(self, cmds):
        self.connect()
        connections.set_ssh_timeout('120')
        if isinstance(cmds, list):
            output = ''
            for command in cmds:
                output += connections.execute_ssh_command_without_check(command)
            return output
        else:
            return connections.execute_ssh_command_without_check(cmds)

    def execute_command_bare(self, cmds):
        self.connect()
        if isinstance(cmds, list):
            output = ''
            for command in cmds:
                output += connections.execute_ssh_command_bare(command)
            return output
        else:
            return connections.execute_ssh_command_bare(cmds)

    def execute_long_time_command(self, command):
        self.connect()
        self.start_monitor()
        self.execute_command_bare(command+'\n')

    def readoutput_thread(self):
        while True:
            if self.conn:
                try:
                    ret = self.conn.read()
                    if ret.strip():
                        if self.monitor:
                            self.monitor_buffer += ret
                            self.logger.debug(ret)
                            self.save_log(ret)
                    time.sleep(1)
                except:
                    pass
            else:
                return 0

    def start_monitor(self):
        self.start()
        self.monitor_buffer = ''
        self.monitor = True

    def stop_monitor(self):
        self.monitor = False



class c_pet_prisma():
    def __init__(self, id):
        self.id         = id
        self.logger     = logging.getLogger(__name__)
        self.config     = self.read_config()
        self.conn_cpc   = None
        self.case       = None
        self.bts_list   = None
        self.files      = IpaMmlItem()
        self.workdire   = '/home/work/temp'
        self.lsu        = c_prisma_ssh(self.config.lsu_uu_ip,
                                       self.config.lsu_uu_port,
                                       self.config.lsu_uu_username,
                                       self.config.lsu_uu_password)

        self.tstm       = c_prisma_ssh(self.config.tstm_uu_ip,
                                       self.config.tstm_uu_port,
                                       self.config.tstm_uu_username,
                                       self.config.tstm_uu_password, '$')


    def read_config(self):
        artizapath = os.path.sep.join([resource_path(), 'config', 'prisma', 'prisma%s' %(self.id)])
        import sys, importlib
        sys.path.append(artizapath)
        model = importlib.import_module('config')
        artizaconfig = IpaMmlItem()
        for key in model.config:
            setattr(artizaconfig, key.lower(), model.config[key])
        return artizaconfig

    def prisma_file(self, filename):
        return os.path.sep.join([resource_path(), 'config', 'prisma', 'prisma%s' %(self.id), filename])

    def connect_to_cpc(self):
        if not self.conn_cpc:
            self.conn_cpc = connections.connect_to_host( self.config.cpc_ip,
                                                        self.config.cpc_port,
                                                        self.config.cpc_username,
                                                        self.config.cpc_password)
        connections.switch_host_connection(self.conn_cpc)

    def disconnect_cpc(self):
        if self.conn_cpc:
            connections.switch_host_connection(self.conn_cpc)
            connections.disconnect_from_host()
            self.conn_cpc = None

    def execute_command_on_cpc(self, command):
        self.connect_to_cpc()
        return connections.execute_shell_command_without_check(command)

    def prepare_lsu_uu(self):
        self.lsu.execute_command(['lsustop', 'lsuclean', 'lsustart'])

    def prepare_tstm_uu(self):
        self.tstm.execute_long_time_command('./start_tstm')
        start_time = time.time()
        total_time = 60
        while time.time() < start_time + total_time:
            if 'IsServerMode=1, tcpPort=' in self.tstm.monitor_buffer:
                self.logger.info('Start TSTM successfully!')
                return 0
            else:
                self.logger.info('Start TSTM is not complted, go on checking....')
            time.sleep(1)
        raise Exception, 'Failed to Start TSTM'

    def create_cell(self, cellid, prisma_cell_script):
        script = './'+ prisma_cell_script if not '/' in prisma_cell_script else prisma_cell_script
        self.lsu.execute_command(script)

    def wait_until_cell_is_available(self, timeout = '300', interval = '10', cellid = '1'):
        start_time = time.time()
        total_time = timestr_to_secs(timeout)
        while time.time() < start_time + total_time:
            ret = self.lsu.execute_command('./ct_cell%s' %(cellid))
            if 'PDSCHMCS31                  = 0 0.00' in ret:
                self.logger.info('LSU Cell status is OK')
                return 0
            else:
                self.logger.info('LSU Cell status is NOT OK, wait for next check.')
            time.sleep(int(interval))
        raise Exception, 'CELL %s is not availble in specific time' %(cellid)

    def prepare_cells(self):
        for bts in self.bts_list:
            self.create_cell(bts.prisma_cell_id, bts.prisma_cell_script)
            self.wait_until_cell_is_available(cellid = bts.prisma_cell_id)

    def move_file_to_cpc(self, localfile, remotefile):
        cmd = 'sshpass -p %s scp %s %s@%s:%s' %(self.config.cpc_password,
                                                localfile,
                                                self.config.cpc_username,
                                                self.config.cpc_ip,
                                                remotefile)
        run_local_command_gracely(cmd)

    def execute_command_on_cpc_linux(self, command):
        cmd = 'sshpass -p %s ssh %s@%s %s' %(self.config.cpc_password,
                                            self.config.cpc_username,
                                            self.config.cpc_ip, command)
        run_local_command_gracely(cmd)

    def deal_with_scenario_file(self):
        scenario_file = os.sep.join([resource_path(), 'config', 'prisma', 'prisma%s' %(self.id), self.case.prisma_file_scenario])
        self.dest_scenario_file = case_file(os.path.basename(self.case.prisma_file_scenario))
        scenario = c_scenario_file(scenario_file, self.dest_scenario_file)
        scenario.update_radio_condition(138)
        self.move_file_to_cpc(self.dest_scenario_file, os.sep.join([self.config.workspace_for_ta, os.path.basename(self.dest_scenario_file)]))

    def deal_with_counter_file(self):
        src_file = os.sep.join([resource_path(), 'config', 'prisma', 'prisma%s' %(self.id), self.case.prisma_file_counter])
        # dst_file = case_file(os.path.basename(src_file))
        dst_file = '/home/work/temp/a.zip'
        os.system('cp %s %s' %(src_file, dst_file))
        f = zipfile.ZipFile(dst_file)
        configfile = [x.filename for x in f.filelist if 'modulecounters.properties' in x.filename][0]
        lines = f.read(configfile).splitlines()
        newlines = []
        for line in lines:
            if 'loggingPath=' in line:
                gv.logger.info('update log path: ' + self.config.workspace_for_prisma)
                newlines.append('loggingPath=%s' %(self.config.workspace_for_prisma))
            else:
                newlines.append(line)
        for line in newlines:
            print line
        f.close()
        updateZip(dst_file, 'config/Preferences/com/prisma/modulecounters.properties', '\n'.join(newlines))
        self.move_file_to_cpc(dst_file, os.sep.join([self.config.workspace_for_ta, os.path.basename(dst_file)]))


    def prepare_files(self):
        self.execute_command_on_cpc_linux('rm -rf '+ self.config.workspace_for_ta)
        self.execute_command_on_cpc_linux('mkdir '+ self.config.workspace_for_ta)

        for attr in [x for x in dir(self.case) if x.startswith('prisma_file')]:
            local_file = os.sep.join([resource_path(), 'config', 'prisma', 'prisma%s' %(self.id), getattr(self.case, attr)])
            remote_file = os.sep.join([self.config.workspace_for_ta, os.path.basename(local_file)])
            self.move_file_to_cpc(local_file, remote_file)
        self.deal_with_scenario_file()
        self.deal_with_counter_file()

    def clear_app(self):
        appname = os.path.basename(self.config.cpc_am_bin_path.replace('\\', '/'))
        output = [x for x in self.execute_command_on_cpc('tasklist |grep ' + appname).splitlines() if not 'grep' in x]
        for line in output:
            if appname in line.lower():
                pid = line.split()[1]
                connections.execute_shell_command_without_check('taskkill /PID %s /F' %(pid))

    def run_scenario(self):
        self.clear_app()
        def _wfile(filename):
            return '/'.join([self.config.workspace_for_prisma, filename])
        cmds = [self.config.cpc_am_bin_path]
        cmds += ['--nosplash', '--nogui']
        cmds += ['-J-Dcli.mode=true']
        cmds += ['--sidfilename', _wfile(self.case.prisma_file_sid)]
        cmds += ['--scefilename', _wfile(self.case.prisma_file_scenario)]
        cmds += ['--preferencesfilename', _wfile(self.case.prisma_file_counter)]
        cmds += ['--bugreportfolder', self.config.workspace_for_prisma]
        cmd = ' '.join((cmds))
        self.logger.info(cmd)
        self.execute_command_on_cpc(cmd)

    def wait_until_scenario_is_done(self, timeout = '300', interval = '10'):
        start_time = time.time()
        total_time = timestr_to_secs(timeout)
        appname = os.path.basename(self.config.cpc_am_bin_path.replace('\\', '/'))
        while time.time() < start_time + total_time:
            output = [x for x in self.execute_command_on_cpc('tasklist |grep ' + appname).splitlines() if not 'grep' in x]
            if appname in ''.join(output):
                self.logger.info('Wait for scenario done.')
                time.sleep(int(interval))
            else:
                return
        raise Exception, 'Scenario has not been done.'

    def setup(self):
        # self.prepare_lsu_uu()
        # self.prepare_cells()
        # self.prepare_tstm_uu()
        self.prepare_files()
        raise Exception, 'Stop'
        pass

    def teardown(self):
        pass

    def calc_packet_loss_ratio(self, filename):
        lines = open(filename).readlines()
        fields = [x.split('->')[-1].replace(' ', '_').replace('-', '_').lower() for x in lines[0].split(',') if x.strip()]
        print fields
        result = []
        for line in lines[1:]:
            if line.strip():
                item = IpaMmlItem()
                data = line.split(',')
                for i in range(len(fields)):
                    setattr(item, fields[i], data[i])
                result.append(item)
        loss = float(sum([float(item.dl_dropped_packets) for item in result]))
        total = loss + sum([float(item.dl_handled_packets) for item in result])
        print loss, total
        return loss/total


class c_scenario_file(object):
    def __init__(self, filename, dst_filename):
        self.filename = filename
        self.dst_filename = dst_filename
        from lxml import etree
        self.tree = etree.parse(filename)

    def update_radio_condition(self, value):
        node = self.tree.xpath('/TestScenario/Groups/Group/TemplateProfileMobility')[0]
        condition_str = '"NOHO%normal%Infinite,2,0,2,0,1,1,{{rc}},0.0,0.0,0.0,None,Disabled,0.0,0.0,No Fading,Not Applicable"'
        node.set('RadioCondition', condition_str.replace('{{rc}}', str(value)))
        self.tree.write(self.dst_filename, xml_declaration=True, encoding='UTF-8')




if __name__ == '__main__':
    # gv.team = 'PET1'
    # gv.case = IpaMmlItem()
    # from pettool import get_case_config
    # gv.case.curr_case = get_case_config('472732')
    # from petcasebase import re_organize_case
    # re_organize_case()
    # print gv.case.curr_case

    conn = connections.connect_to_ssh_host('10.69.64.88', '22', 'switch', 'switch', ':')
    output = connections.execute_ssh_command_without_check('help')
    print output
    print conn

    # from pet_bts import read_bts_config
    # print read_bts_config('642')
    # a = c_pet_prisma(165)
    # a.case = gv.case.curr_case
    # a.deal_with_counter_file()
    # a.clear_app()
    # a.case = gv.case.curr_case

    # print a.run_scenario()

    # a.setup()

    # p = c_scenario_file('/home/work/temp/volte_coverage.sce')
    # p.update_radio_condition(100)

    # a.prepare_lsu_uu()
    # a.clean_all_cells()
    # a.create_cell(2, '40340')
    # a.prepare_tstm_uu()
    # a.execute_command_on_cpc('dir')
    # a.execute_commmand_on_lsu('ls -la')
    # a.execute_commmand_on_tstm('ls -la')
    # print a.config