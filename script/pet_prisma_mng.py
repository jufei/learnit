import threading, datetime, select
from robot.utils import timestr_to_secs
from thread import *
from petbase import *
import zipfile
import tempfile

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

    def set_logfile(self, filename):
        self.logfilename = filename

    def connect(self):
        if self.nickname:
            gv.logger.info('Switch to : '+ self.nickname)
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
                            gv.logger.debug(ret)
                            save_log(ret.splitlines(), self.logfilename)
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


class c_lsu(c_prisma_ssh):
    def reboot_lsu(self):
        self.execute_command(['lsustop', 'lsuclean', 'lsustart'])

class c_lsu_uu(c_lsu):
    def create_cell(self, cellid = '1'):
        self.execute_command(['./cr_cell%s' %(cellid)])

    def wait_until_cell_is_available(self, timeout = '300', interval = '10', cellid = '1'):
        start_time = time.time()
        total_time = timestr_to_secs(timeout)
        while time.time() < start_time + total_time:
            ret = self.execute_command('./ct_cell%s' %(cellid))
            if 'PDSCHMCS31                  = 0 0.00' in ret:
                gv.logger.info('LSU Cell status is OK')
                return 0
            else:
                gv.logger.info('LSU Cell status is NOT OK, wait for next check.')
            time.sleep(int(interval))
        kw('report_error', 'CELL %s is not availble in specific time' %(cellid))

class c_tstm(c_prisma_ssh):
    def __init__(self, ip, port='22', username='user', password='user', prompt = '[user@tstm ~]'):
        super(c_tstm, self).__init__(ip, port, username, password, prompt)

    def stop_all_tstm(self):
        self.execute_command(['stopAllTstms'])



class c_cpc(c_prisma_ssh):
    def __init__(self, ip, port='22', username='root', password='root', prompt = '#'):
        super(c_cpc, self).__init__(ip, port, username, password, prompt)


class c_prisma(object):
    def __init__(self, id):
        self.id = id
        self.lsu_uu = None
        self.lsu_s1 = None
        self.tstm_uu = None
        self.tstm_epc = None
        self._read_config()
        self._setup_connections()

    def prisma_file(self, filename):
        return os.path.sep.join([resource_path(), 'config', 'prisma', 'prisma%s' %(self.id), filename])

    def _read_config(self):
        path = self.prisma_file('')
        import sys, importlib
        sys.path.append(path)
        model = importlib.import_module('config')
        self.config = IpaMmlItem()
        for key in model.config:
            setattr(self.config, key.lower(), model.config[key])

    def _setup_connections(self):
        self.lsu_s1 = c_lsu(self.config.lsu_s1_ip, self.config.lsu_s1_port, self.config.lsu_s1_username, self.config.lsu_s1_password)
        self.lsu_s1.nickname = 'LSU-S1'
        self.lsu_s1.connect()
        self.lsu_uu = c_lsu_uu(self.config.lsu_uu_ip, self.config.lsu_uu_port, self.config.lsu_uu_username, self.config.lsu_uu_password)
        self.lsu_uu.nickname = 'LSU-UU'
        self.lsu_uu.connect()
        self.tstm_uu = c_tstm(self.config.tstm_uu_ip, self.config.tstm_uu_port, self.config.tstm_uu_username, self.config.tstm_uu_password)
        self.tstm_uu.nickname = 'TSTM_UU'
        self.tstm_uu.logfilename = case_file('tstmuu.log')
        self.tstm_uu.connect()
        self.tstm_epc = c_tstm(self.config.tstm_epc_ip, self.config.tstm_epc_port, self.config.tstm_epc_username, self.config.tstm_epc_password)
        self.tstm_epc.nickname = 'TSTM-EPC'
        self.tstm_epc.logfilename = case_file('tstmepc.log')
        self.tstm_epc.connect()

    def prepare_lsu(self):
        self.lsu_uu.reboot_lsu()
        self.lsu_s1.reboot_lsu()
        for cellid in self.config.cell_list.split(','):
            self.lsu_uu.create_cell(cellid)

    def prepare_tstm(self):
        self.tstm_uu.stop_all_tstm()
        self.tstm_uu.execute_long_time_command('./startUU')
        self.tstm_epc.execute_long_time_command('./startepc')
        self.wait_until_tstm_uu_is_available()
        self.wait_until_tstm_epc_is_available()

    def wait_until_tstm_uu_is_available(self, timeout = '30', interval = '1'):
        start_time = time.time()
        total_time = timestr_to_secs(timeout)
        while time.time() < start_time + total_time:
            if 'IsServerMode=1, tcpPort=' in self.tstm_uu.monitor_buffer:
                gv.logger.info('StartUU successfully!')
                return 0
            else:
                gv.logger.info('StartUU is not complted, go on checking....')
            time.sleep(int(interval))
        kw('report_error', 'Failed to StartUU')

    def wait_until_tstm_epc_is_available(self, timeout = '60', interval = '1'):
        start_time = time.time()
        total_time = timestr_to_secs(timeout)
        while time.time() < start_time + total_time:
            if 'to schedule LTE_EPC' in self.tstm_epc.monitor_buffer:
                gv.logger.info('StartEPC successfully!')
                return 0
            else:
                gv.logger.info('StartEPC is not complted, go on checking....')
            time.sleep(int(interval))
        kw('report_error', 'Failed to StartEPC')

    def wait_until_s1_is_up(self, timeout = '300', interval = '1'):
        start_time = time.time()
        total_time = timestr_to_secs(timeout)
        while time.time() < start_time + total_time:
            if 'S1 Setup Successful (EPC side' in self.tstm_epc.monitor_buffer:
                gv.logger.info('S1 Connect to eNB successfully!')
                return 0
            else:
                gv.logger.info('S1 is not availble, go on checking....')
            time.sleep(int(interval))
        kw('report_error', 'Failed to check S1 on line')

    def wait_until_all_cells_are_available(self):
        for cellid in self.config.cell_list.split(','):
            self.lsu_uu.wait_until_cell_is_available('300', '5', cellid)

    def setup(self):
        self.prepare_lsu()
        self.prepare_tstm()

    def teardown(self):
        if self.lsu_s1:
            self.lsu_s1.disconnect()
        if self.lsu_uu:
            self.lsu_uu.disconnect()
        if self.tstm_uu:
            self.tstm_uu.disconnect()
        if self.tstm_epc:
            self.tstm_epc.disconnect()

    def wait_until_prisma_is_ready(self):
        self.wait_until_all_cells_are_available()
        self.wait_until_s1_is_up()

class c_prisma_runner(object):
    def __init__(self, prisma):
        self.prisma = prisma
        self.config = prisma.config
        self.sidfilename = ''
        self.scefilename = ''
        self.preferencesfilename = ''
        self.mdlfilename = ''
        self.usrfilename = ''

        self.cpc = None
        self.prepare_cpc()

    def prepare_cpc(self):
        self.cpc = c_cpc(self.prisma.config.cpc_ip, self.prisma.config.cpc_port,
                         self.prisma.config.cpc_username, self.prisma.config.cpc_password)
        self.cpc.logfilename = case_file('cpc.log')
        # gv.logger.info(self.cpc.logfilename)
        gv.logger.info(self.cpc)
        self.cpc.connect()

    def prepare_files_for_running(self):
        self.cleanup_tmp_path()
        self.prepare_sid_file()
        self.prepare_usr_file()
        self.prepare_sce_file()
        self.prepare_mdl_file()
        self.prepare_preferences_file()

    def _tmp_file_path(self, filename):
        return os.sep.join([self.prisma.config.cpc_tmp_path, filename])

    def _directly_run_command_in_cpc(self, command):
        cmd = 'sshpass -p %s ssh %s@%s %s' %(self.config.cpc_password, self.config.cpc_username,
               self.config.cpc_ip, command)
        return run_local_command_gracely(cmd)

    def _upload_file(self, filename):
        cmd = 'sshpass -p %s scp %s %s@%s:%s/%s' %(self.config.cpc_password, filename,
               self.config.cpc_username, self.config.cpc_ip, self.config.cpc_tmp_path, os.path.basename(filename))
        run_local_command(cmd)

    def _download_file(self, filename, localdire):
        cmd = 'sshpass -p %s scp %s@%s:%s %s' %(self.config.cpc_password, self.config.cpc_username,
               self.config.cpc_ip, self._tmp_file_path(filename), os.sep.join([localdire, os.path.basename(filename)]))
        run_local_command(cmd)

    def download_case_files(self, localdire):
        for filename in self._get_counter_files():
            self._download_file(filename.split()[-1], localdire)
        for filename in self._get_bug_report_file():
            self._download_file(filename.split()[-1], localdire)

    def cleanup_tmp_path(self):
        self._directly_run_command_in_cpc('rm -rf %s/*.csv' %(self.config.cpc_tmp_path))
        self._directly_run_command_in_cpc('rm -rf %s/bugreport_*' %(self.config.cpc_tmp_path))

    def _get_file_list_in_tmp_path(self):
        return self._directly_run_command_in_cpc('ls -la ' + self.config.cpc_tmp_path).splitlines()

    def _get_counter_files(self):
        return [x for x in self._get_file_list_in_tmp_path() if '.csv' in x]

    def _get_bug_report_file(self):
        return [x for x in self._get_file_list_in_tmp_path() if 'bugreport_' in x]

    def prepare_sid_file(self):
        self.sidfilename = self._tmp_file_path('ta.sid')

    def prepare_usr_file(self):
        self.usrfilename = self._tmp_file_path('ta.usr')

    def prepare_mdl_file(self):
        self.mdlfilename = self._tmp_file_path('ta.mdl')

    def prepare_sce_file(self):
        self.scefilename = self._tmp_file_path('trafficmodel1.sce')

    def prepare_preferences_file(self):
        # filename = 'counter.zip'
        # f = zipfile.ZipFile(filename)
        # configfile = [x.filename for x in f.filelist if 'modulecounters.properties' in x.filename][0]
        # lines = f.read(configfile).splitlines()
        # newlines = []
        # for line in lines:
        #     if 'loggingPath=' in line:
        #         newlines.append('loggingPath=%s' %(self.config.cpc_tmp_path))
        #     else:
        #         newlines.append(line)
        # f.close()
        # updateZip(filename, 'config/Preferences/com/prisma/modulecounters.properties', '\n'.join(newlines))
        self.preferencesfilename = self._tmp_file_path('counter.zip')

    def build_running_command(self):
        cmds = [self.prisma.config.cpc_am_bin_path]
        cmds += ['--nosplash', '--nogui', '--ignoremsmngind', '--duration %s' %(gv.case.curr_case.case_duration)]
        cmds += ['-J-Dcli.mode=true']
        cmds += ['--sidfilename', self.sidfilename]
        cmds += ['--scefilename', self.scefilename]
        cmds += ['--preferencesfilename', self.preferencesfilename]
        cmds += ['--bugreportfolder', self.prisma.config.cpc_tmp_path]
        return ' '.join(cmds)

    def running(self):
        self.prepare_files_for_running()
        cmd = self.build_running_command()
        gv.logger.info(cmd)
        self.cpc.execute_long_time_command(cmd)

    def wait_until_completed(self, timeout, interval):
        start_time = time.time()
        total_time = timestr_to_secs(timeout) + timestr_to_secs(interval) + 60
        while time.time() < start_time + total_time + int(interval):
            if 'Shutting down' in self.cpc.monitor_buffer:
                gv.logger.info('Scenario running done!')
                self.download_case_files(case_file(''))
                return 0
            else:
                gv.logger.info('Scenario is still running, left [%d]s, go on checking....' %(int(total_time-time.time()+start_time)))
            time.sleep(int(interval))
        kw('report_error', 'Running scenario timeout')

    def teardown(self):
        if self.cpc:
            self.cpc.disconnect()


def updateZip(zipname, filename, data):
    tmpfd, tmpname = tempfile.mkstemp(dir=os.path.dirname(zipname))
    os.close(tmpfd)
    with zipfile.ZipFile(zipname, 'r') as zin:
        with zipfile.ZipFile(tmpname, 'w') as zout:
            zout.comment = zin.comment # preserve the comment
            for item in zin.infolist():
                if item.filename != filename:
                    zout.writestr(item, zin.read(item.filename))

    # replace with the temp archive
    os.remove(zipname)
    os.rename(tmpname, zipname)
    with zipfile.ZipFile(zipname, mode='a', compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(filename, data)



if __name__ == '__main__':
    pass
    # prisma = c_prisma('1')
    # runner = c_prisma_runner(prisma)
    # runner.prepare_files_for_running()
    # print runner.build_running_command()
    # prisma.init()
    # prisma.setup()
    # wait_until_prisma_is_ready()
    # prisma.wait_until_prisma_is_ready()
    # prisma.prepare_lsu()
    # prisma.prepare_tstm()
    # prisma.wait_until_tstm_uu_is_available()
    # # for i in range(10):
    # #     print i
    # #     time.sleep(1)
    # print '11111111111111111'
    # print prisma.tstm_uu.monitor_buffer
    # print '222222222222222222'
    # print prisma.tstm_epc.monitor_buffer
    # prisma.lsu_uu.create_cell('1')
    # prisma.lsu_uu.wait_until_cell_is_available('300', '5', '1')
    # prisma.teardown()
    # tstm = c_tstm('192.168.40.190')
    # print tstm.execute_command('ls -la')
    # tstm.disconnect()
    # print 'OK'