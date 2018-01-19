import os, time, re
import ftp_lib
import subprocess
import datetime
import paramiko

from petbase import *
from pet_ta_config import all_cases

#Some keyword for case, these keyword will be used in kw, if not it can be implemented in petbase.py
def report_error(error_info):
    raise Exception, error_info

def run_keyword_and_record_error(keyword_name='', *args):
    gv.case.keyword_group.append(keyword_name, *args)

def execute_command_on_pc(cmds):
    if isinstance(cmds, list):
        output = ''
        for command in cmds:
            print command
            output += connections.execute_shell_command_without_check(command)
        return output
    else:
        return connections.execute_shell_command_without_check(cmds)

def restart_port_forword_service():
    execute_command_on_bts_control_pc(['net stop "PassPort (port forwarding)"',
                                       'net start "PassPort (port forwarding)"'])

#Other common keyword:

def clean_all_connections():
    import os
    gv.logger.info('Before Close connections:')
    for line in os.popen('netstat -na |grep %s' %(gv.master_bts.bts_control_pc_lab)).readlines():
        gv.logger.info(line)
    connections.disconnect_all_hosts()
    connections.disconnect_all_ssh()
    # kw('disconnect_all_hosts')
    # kw('disconnect_all_ssh')
    gv.logger.info('After Close connections:')
    for line in os.popen('netstat -na |grep %s' %(gv.master_bts.bts_control_pc_lab)).readlines():
        gv.logger.info(line)
    for bts in gv.allbts:
        bts.conn_pc = None
        bts.conn_bts = None
    if gv.env.use_tm500:
        if gv.tm500:
            gv.tm500.conn_pc = None


def initlize_all_connections():
    clean_all_connections()
    kw('connect_to_tm500_control_pc')
    kw('pet_connect_to_tma')
    kw('pet_connect_all_bts')
    kw('pet_connect_all_bts_control_pc')


#BTS software part:
def get_env_variables():
    #define the DEBUG_MODE environment variable, possable values:
    # 1. DEV, used for development, the throughput will be 20 ms, others are same as RUN
    # 2. RUN, used for normal RUN,
    # 3. DEBUG, used for debug, not restart BTS and TM500

    def _get_env_with_default(envname, default):
        return pv(envname.upper()) if var_exist(envname.upper()) else default

    gv.debug_mode = pv('DEBUG_MODE').upper() if var_exist('DEBUG_MODE') else 'RUN'
    gv.tm500_radio_card = pv('TM500_RADIO_CARD') if var_exist('TM500_RADIO_CARD') else 'RC1'

    if not var_exist('ADJUST_PA'):
        spv('ADJUST_PA', 'Y')
    if not var_exist('MASTER_BTS'):
        kw('report_error', 'Could not find the variable: MASTER_BTS')

    gv.counterfile = os.path.sep.join([resource_path(), 'config', 'case', 'counterdef_16A.xlsx'])
    gv.env.restart_tm500_for_each_case = pv('RESTART_TM500_FOR_EACH_CASE').upper() == 'Y' if var_exist('RESTART_TM500_FOR_EACH_CASE') else False
    gv.env.restart_bts_for_each_case = pv('RESTART_BTS_FOR_EACH_CASE').upper() == 'Y' if var_exist('RESTART_BTS_FOR_EACH_CASE') else False
    gv.env.use_infomodel = pv('USE_INFOMODEL').strip() == 'Y' if var_exist('USE_INFOMODEL') else False

    gv.env.loadtool = IpaMmlItem()
    gv.env.loadtool.name, gv.env.loadtool.id = pv('LOADTOOL').split('-')[0], pv('LOADTOOL').split('-')[1]
    gv.env.use_tm500  = gv.env.loadtool.name.upper() == 'TM500'
    gv.env.use_prisma = gv.env.loadtool.name.upper() == 'PRISMA'
    gv.env.use_artiza = gv.env.loadtool.name.upper() == 'ARTIZA'

    gv.env.release = pv('RELEASE').upper() if var_exist('RELEASE') else 'TL16A'
    gv.team = pv('TEAM').lower() if var_exist('TEAM') else ''
    gv.team = '' if gv.team.upper() == 'PET1' else gv.team
    gv.dbfile = os.path.sep.join([resource_path(), 'config', 'case', 'database%s.xlsx' %(gv.team)])
    gv.env.use_single_oam = pv('SINGLE_OAM').upper() == 'Y' if var_exist('SINGLE_OAM') else False
    gv.env.need_upgrade_tm500 = pv('UPGRADE_TM500').upper() == 'Y' if var_exist('UPGRADE_TM500') else False
    gv.need_upgrade_tma = pv('RESTART_TMA_FOR_EACH_CASE').upper() == 'Y' if var_exist('RESTART_TMA_FOR_EACH_CASE') else False
    gv.env.use_ixia = pv('USE_IXIA').upper() == 'Y' if var_exist('USE_IXIA') else False
    gv.env.use_catapult = pv('USE_CATAPULT').upper() == 'Y' if var_exist('USE_CATAPULT') else False
    gv.env.bts_version = pv('BTS_VERSION').upper() if var_exist('BTS_VERSION') else ''
    gv.env.reboot_bts_by_pb = pv('REBOOT_BTS_BY_PB').upper() == 'Y' if var_exist('REBOOT_BTS_BY_PB') else False
    gv.env.tm500_path = '"%s"' %(pv('TM500_PATH')) if var_exist('TM500_PATH') else ''
    gv.env.upload_result = pv('UPLOAD_RESULT').upper() == 'Y' if var_exist('UPLOAD_RESULT') else False

    if gv.env.upload_result:
        kw('log', 'Need to upload result to QC.')
    print gv.env
    # raise Exception, 'Stop by jufei'
    import pet_db
    pet_db.initlize_db()


def pet_stop_site_manager():
    kw('run_keyword_and_ignore_error', 'pet_clear_process', 'java.exe')
    kw('run_keyword_and_ignore_error', 'pet_clear_process', 'javaw.exe')

def pet_clear_process(processname):
    for i in range(100):
        output = kw('kill_process', processname)
        if 'not found'.upper() in output.upper():
            break

def get_snapshot_log():
    kw('connect_to_bts_control_pc')
    kw('pet_stop_site_manager')
    # path = r'C:\\Python27\\Lib\\site-packages\\BtsShell\\resources\\tools\\TA_exe_src\\out_field\\Remotely_exe'
    path = '"D:\\snapshot"'
    path = r'"C:\Program Files\NSN\Managers\BTS Site\BTS Site Manager"'
    path = gv.master_bts.site_manager_path if has_attr(gv.master_bts, 'site_manager_path' ) else path
    kw('set_shell_timeout', '300')
    connections.execute_shell_command_without_check('cd '+ path)
    filename = 'sp_%s.zip' %(time.strftime("%Y_%m_%d__%H_%M_%S"))
    # exe_path = r'collectfiles -ne 192.168.255.129 -pw Nemuadmin:nemuuser -ssh toor4nsn:oZPS0POrRieRtu  -techlogs -zip'
    exe_path = r'BTSSiteManager.bat -ne 192.168.255.129 -pw Nemuadmin:nemuuser -savesnapshot -snapshotfilename %s -logcoverage all' %(filename)
    connections.execute_shell_command_without_check(exe_path)
    # connections.execute_shell_command_without_check(r'copy sp.zip d:\\temp\\sp.zip')
    # import ftp_lib as ftplib
    # url = 'ftp://%s/Temp/sp.zip' %(gv.master_bts.bts_control_pc_lab)
    # ftplib.download_from_ftp_to_local(url, case_file('snapshot.zip'), 'bin', 'filed', 'filed')

def get_alarm_list():
    # pet_bts_alarm_path = {
    #     '55': ['/MRBTS-*/RAT-*/LNBTS-*/ALARM_L-*',         '/MRBTS-*/RAT-*/LNBTS-*/LNCEL-*/ALARM_L-*'],
    #     '65': ['/MRBTS-*/RAT-*/BTS_L-*/LNBTS-*/ALARM_L-*', '/MRBTS-*/RAT-*/BTS_L-*/LNBTS-*/LNCEL-*/ALARM_L-*']
    # }
    # alarm_list = []
    # if gv.infomodel:
    #     alarm_path =  pet_bts_alarm_path['55'] if is_rl55() else pet_bts_alarm_path['65']
    #     for path in alarm_path:
    #         try:
    #             alarms = gv.infomodel.query_infomodel('get list ' + path, timeout=3, alias=gv.btsip)
    #         except:
    #             alarms = []
    #         alarm_list += alarms
    # alarminfo = [(x.alarmInformation.alarmText.alarmDetailNbr,
    #               x.alarmInformation.alarmText.faultDescription) for x in alarm_list]
    # print alarminfo
    # if alarminfo:
    #     for alarm in alarminfo:
    #         kw('log', alarm)
    # return alarminfo
    return None

def check_alarm_during_case():
    # gv.case_end_alarm_list = kw('get_alarm_list')
    # curr_alarm_text = [x.alarmText.faultDescription for x in gv.case_end_alarm_list]
    # print curr_alarm_text
    # orig_alarm_text = [x.alarmText.faultDescription for x in gv.case_begin_alarm_list]
    # new_alarms = [x for x in curr_alarm_text if x not in orig_alarm_text]
    # if new_alarms:
    #     kw('log', new_alarms)
    #     kwg('report_error', 'Found new alarms during the case running. ')
    pass

def get_current_case_config():
    tags = kw('create list', '@{Test Tags}')
    # qc_test_instance_id = [x for x in tags if 'qc_test_instance_id' in x][0].split(':')[-1]
    qc_test_instance_id = [x for x in tags if x.startswith('QC_')][0].split('_')[-1]
    kw('log', qc_test_instance_id)
    return get_case_config(qc_test_instance_id)

def get_case_config(qc_test_instance_id):
    from pet_db import read_all_case_db
    all_case = read_all_case_db(gv.team)
    acase = [x for x in all_case if x.qc_test_instance_id == qc_test_instance_id and x.ready]
    acase = [x for x in all_case if x.qc_test_instance_id == qc_test_instance_id]
    if acase:
        acase = acase[0]
        gv.logger.info('Found case in DB.')
    else:
        gv.logger.info('Could not found case in DB.')
        import xlrd
        bk = xlrd.open_workbook(gv.dbfile)
        shxrange = range(bk.nsheets)
        sh = bk.sheet_by_name("cases")
        nrows, ncols = sh.nrows, sh.ncols
        titles = sh.row_values(0)
        for i in range(1, nrows):
            line = ['%s' % (x) for x in sh.row_values(i)]
            acase = IpaMmlItem()
            if line[0].strip():
                for j in range(len(titles)):
                    if titles[j].strip():
                        value = line[j].strip()
                        if value.endswith('.0'):
                            value = value.replace('.0', '')
                        setattr(acase, titles[j].lower().strip(), '%s' % (value))
                acase.qc_test_instance_id = acase.qc_test_instance_id.replace('.0', '')
                if acase.qc_test_instance_id == qc_test_instance_id:
                    for attr in ['format', 'uldl', 'ssf', 'tm', 'pipe', 'band']:
                        setattr(acase, attr, getattr(acase, attr).replace('.0',''))
                    gv.logger.info('Found case in Excel')
                    break
                else:
                    continue
    if not acase:
        kw('report_error', 'Could not find the case for qc_test_instance_id: [%s], please check it.' %(qc_test_instance_id))
    acase.format = '0' if acase.format.strip() == '' else str(acase.format)
    acase.tm500_version = 'K' if acase.tm500_version == '' else acase.tm500_version
    if hasattr(acase, 'ue_count'):
        acase.real_ue_count = acase.ue_count
    if acase.case_type.upper() == 'VOLTE_CALL_DROP':
        acase.kpi += ';kpi_volte_call_drop_ratio:0'
    if acase.case_type.upper() == 'VOLTE_CALL_SETUP':
        acase.kpi += ';kpi_volte_call_setup_ratio:0'
    if acase.case_type.upper() == 'VOLTE_CAP':
        acase.kpi += ';kpi_volte_cap:%s' %(acase.ue_count)
    if acase.case_type.upper() == 'MIX_MR':
        acase.kpi += ';kpi_cap:20;kpi_duration:%2.2f' %(int(acase.case_duration)/60)
    if acase.case_type.upper() in ['MIX_CAP', 'VOLTE_PERM'] or acase.team.upper() == 'PET2' or acase.domain == 'PRF':
        pass
    else:
        acase.kpi += ';kpi_cpuload:70'

    if gv.team.upper() == 'PET2':
        acase.kpi += ';kpi_errlog_ratio:60'

    cid = acase.case_type.replace(' ', '_').upper()
    if cid in all_cases.keys():
        acase.case_info = all_cases[cid]
    else:
        kw('report_error', 'Invalid Case ID: [%s], please check it.' %(cid))
    return acase


def get_case_config_new(qc_test_instance_id):
    from pet_db import get_table_content, getfielddict
    case = get_table_content('tblallcase', ' where qc_test_instance_id=%s' %(qc_test_instance_id))[0]
    import json
    caseinfo =  json.loads(case.caseinfo)
    acase = IpaMmlItem()
    fieldinfo = getfielddict()
    for field in fieldinfo:
        if field.db_fieldname in caseinfo.keys():
            value = caseinfo[field.db_fieldname]
        else:
            value = field.default_value
        if field.field_type.upper() == 'BOOLEAN':
            value = True if str(value).upper() in ['YES', 'Y', 'TRUE', '1'] else False
        if field.field_type.upper() == 'INTEGER':
            if str(value).strip():
                value = int(value)
            else:
                value = 0
        setattr(acase, field.db_fieldname, value)

    for prefix in ['', 'ms_', 'sp_', 'ss_']:
        attrname = prefix + 'band'
        value = getattr(acase, attrname)
        setattr(acase, attrname, value.replace('M', ''))
        attrname = prefix + 'tm'
        value = getattr(acase, attrname)
        setattr(acase, attrname, value.replace('TM', ''))

    acase.tm500_version = 'K' if acase.tm500_version == '' else acase.tm500_version
    if hasattr(acase, 'ue_count'):
        acase.real_ue_count = acase.ue_count
    if acase.case_type.upper() == 'VOLTE_CALL_DROP':
        acase.kpi += ';kpi_volte_call_drop_ratio:0'
    if acase.case_type.upper() == 'VOLTE_CALL_SETUP':
        acase.kpi += ';kpi_volte_call_setup_ratio:0'
    if acase.case_type.upper() == 'VOLTE_CAP':
        acase.kpi += ';kpi_volte_cap:%s' %(acase.ue_count)
    if acase.case_type.upper() == 'MIX_MR':
        acase.kpi += ';kpi_duration:%2.2f' %(int(acase.case_duration)/60)
    if acase.case_type.upper() in ['MIX_CAP', 'VOLTE_PERM'] or acase.team.upper() == 'PET2' or acase.domain == 'PRF':
        pass
    else:
        acase.kpi += ';kpi_cpuload:70'

    cid = acase.case_type.replace(' ', '_').upper()
    if cid in all_cases.keys():
        acase.case_info = all_cases[cid]
    else:
        kw('report_error', 'Invalid Case ID: [%s], please check it.' %(cid))

    return acase


def select_tm500():
    gv.tm500 = kw('read_tm500_config', gv.env.loadtool.id)

def start_to_capture_all_kinds_of_logs():
    for logtype in gv.case.case_log_list:
        if logtype == 'tcpdump':
            kw('start_tshark_on_bts', gv.master_bts.bts_id)
        if logtype == 'ttitrace':
            kw('start_tti_trace', gv.master_bts.bts_id)
        if logtype == 'infomodel':
            kw('start_infomodel_logging', gv.master_bts.bts_id)

def stop_to_capture_all_kinds_of_logs():
    for logtype in gv.case.case_log_list:
        if logtype == 'tcpdump':
            kw('stop_tshark_and_parse_file', gv.master_bts.bts_id)
        if logtype == 'ttitrace':
            kw('stop_tti_trace', gv.master_bts.bts_id)
        if logtype == 'infomodel':
            kw('stop_infomodel_logging', gv.master_bts.bts_id)

def try_to_disconnect_connection_to_apc(cmdstr):
    ip = cmdstr.split(':')[0]
    output = kw('execute_command_on_tm500_control_pc', 'netstat -nao |grep '+ip)
    for line in [x for x in output.splitlines() if 'ESTABLISHED' in x]:
        pid = line.split()[-1].strip()
        kw('execute_command_on_tm500_control_pc', 'taskkill /F /PID '+pid)

def pet_restart_device_by_power_break_apc(cmdstr='', times=60):
    def send_commands(conn, cmdlist, lastprompt):
        ret = ''
        for cmd in cmdlist:
            conn.write(cmd+'\n\r')
            ret += conn.read_until(lastprompt)
        return ret

    ip = cmdstr.split(':')[0]
    outlet = cmdstr.split(':')[1]
    port = 23
    if len(cmdstr.split(':')) == 3:
        port = int(cmdstr.split(':')[2])
    name_prompt='User Name :'
    pass_prompt='Password  :'
    prompt = '<ENTER>- Refresh, <CTRL-L>- Event Log'
    prompt_do = "Enter 'YES' to continue or <ENTER> to cancel"
    timeout = 2
    output = ''
    import telnetlib
    connected = False
    for i in range(60):
        try:
            gv.logger.info('Try to connect APC for %d times: ' %(i+1))
            tn = telnetlib.Telnet(ip, port)
            output += tn.read_until(name_prompt, 5)
            tn.write('apc\n\r')
            output += tn.read_until(pass_prompt, 5)
            tn.write('apc\n\r')
            output += tn.read_until(prompt, 5)
            connected = True
            break
        except:
            gv.logger.debug('Connect to APC failed, maybe connection is occupied by another process, I will try 5 seconds later.')
            time.sleep(5)
    gv.logger.info(output)
    output = ''
    if not connected:
        kw('report_error', 'Restart TM500 failed because could not connect to PB.')
    else:
        print 'Connect to PB successfully.'
    try:
        output += send_commands(tn, [chr(27)*8], prompt)
        output += send_commands(tn, ['1', '2', '1', outlet, '1'], prompt)
        output += send_commands(tn, ['2'], prompt_do)
        output += send_commands(tn, ['YES'], 'Press <ENTER> to continue...')
        output += send_commands(tn, [''], prompt)
        time.sleep(int(times))
        output += send_commands(tn, ['1'], prompt_do)
        output += send_commands(tn, ['YES'], 'Press <ENTER> to continue...')
        output += send_commands(tn, [''], prompt)
    finally:
        tn.close()
    gv.logger.info(output)


def get_ssh_prompt(host, port, username, password):
    import paramiko
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    result = '>'
    try:
        client.connect(host, port, username, password)
        channel = client.invoke_shell()
        import time
        while not channel.recv_ready():
            time.sleep(1)
        results = channel.recv(2048)
    finally:
        client.close()
    prompt = results.strip()[-1]
    if prompt not in ['#', '>']:
        gv.logger.info('Warning: Found prompt error, it is: '+ prompt)
        prompt = result
    return prompt

def ssh_is_enable(host, port, username, password):
    import paramiko
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(host, int(port), username=username, password=password, timeout=10)
        channel = client.invoke_shell()
        ssh_ok = True
    except:
        ssh_ok = False
    finally:
        client.close()
    return ssh_ok


def power_control_for_facom(op, portinfo):
    host, port = portinfo.split(':')
    import socket
    import binascii
    POWER_ON_PORT  = ["01050000FF008C3A", "01050001FF00DDFA", "01050002FF002DFA", "01050003FF007C3A", "01050004FF00CDFB", "01050005FF009C3B", "01050006FF006C3B", "01050007FF003DFB"]
    POWER_OFF_PORT = ["010500000000CDCA", "0105000100009C0A", "0105000200006C0A", "0105000300003DCA", "0105000400008C0B", "010500050000DDCB", "0105000600002DCB", "0105000700007C0B"]

    p_Socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connected = False
    for i in range(30):
        try:
            p_Socket.connect((host, 4001))
            connected = True
            break
        except:
            gv.logger.info('Connect to FACOM PB [%s] failed, TA will try after 5s.' %(portinfo))
            time.sleep(5)
    if not connected:
        raise Exception, 'Could not connect to FACOM PB [%s] after try many times, case will fail.' %(portinfo)


    try:
        # p_Socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # p_Socket.connect((host, 4001))
        portconfig = POWER_ON_PORT if op.upper() == 'ON' else POWER_OFF_PORT
        if p_Socket.send(binascii.a2b_hex(portconfig[int(port)-1])):
            gv.logger.info("Send message POWER_OFF_PORT_%s %s over socke success!" % (port, portconfig[int(port)-1]))
        else:
            raise Exception, "Send message POWER_OFF_PORT_%s %s over socke failed!" % (port, portconfig[int(port)-1])
    finally:
        p_Socket.close()

def wait_until_port_is_listening(port_num, timeout = '5'):
    for i in range(int(timeout)):
        output = connections.execute_shell_command_without_check('netstat -na|grep %s' %(str(port_num)))
        if 'LISTENING' in output:
            return 0
        else:
            time.sleep(1)
    kw('report_error', 'Cound not find port [%s] listening in [%s] seconds' %(port_num, timeout))


def common_check_for_ta_env():
    from pet_bts import read_bts_config
    gv.master_bts = read_bts_config(pv('bts'))
    print gv.master_bts
    gv.case = IpaMmlItem()
    gv.case.curr_case = IpaMmlItem()
    gv.case.curr_case.codec = ''
    gv.case.log_directory = '/tmp'
    gv.case.debug_file = pv('debug_file')
    # gv.tm500 = kw('read_tm500_config', pv('TM500'))
    # gv.datadevice = kw('read_datadevice_config', pv('Datadevice'))
    # print gv.tm500

    #BTS part
    kw('execute_command_on_bts_control_pc', '', 'dir c:\\')
    kw('config_bts_control_pc')
    kw('makesure_passport_is_running', gv.master_bts.conn_pc)
    kw('start_btslog_pcap_server_if_needed')
    try:
        kw('pet_prepare_infomodel')
        kw('bts_is_onair_by_infomodel')
    finally:
        kw('finish_infomodel')

    #TM500 part
    # kw('config_tm500_control_pc')
    # kw('start_console_server_if_needed')
    # kw('pet_occupy_tm500_resource')
    # kw('pet_release_tm500_resource')

    #Data Device
    # kw('pet_occupy_data_device')
    # kw('pet_release_data_device')

    connections.disconnect_all_hosts()
    connections.disconnect_all_ssh()

def pet_show_system_info():
    run_local_command('ps -ef|grep iperf')
    run_local_command('ps -ef|grep tti')

def get_free_port(startport, endport):
    for i in range(int(startport), int(endport)):
        if os.popen('netstat -na|grep 0.0.0.0:%s|grep LISTEN' %(i)).readlines():
           continue
        else:
           return i

def kill_process(processes):
    if isinstance(processes, list) or isinstance(processes, set):
        for process in processes:
            cmd = 'TASKKILL /F /IM "%s"' %(process)
            ret = connections.execute_shell_command_without_check(cmd)
    else:
        cmd = 'TASKKILL /F /IM  "%s"' %(processes)
        ret = connections.execute_shell_command_without_check(cmd)
    return ret

def makesure_passport_is_running(conn):
    if conn:
        connections.switch_host_connection(conn)
        servicename = '"PassPort (port forwarding)"'
        output = execute_command_on_pc('sc query ' + servicename)
        if not 'RUNNING' in output:
            return execute_command_on_pc('sc start ' + servicename)

def execute_command_on_telnet(ip = '', port='', cmdlist='', delay=0.5):
    import telnetlib
    ret = ''
    tn = None
    for i in range(60):
        try:
            tn = telnetlib.Telnet(ip, port)
            break
        except:
            gv.logger.info('Connect to %s:%s failed, I will try after 5 seconds' %(ip, port))
            time.sleep(5)

    if tn:
        try:
            cmdlist = [cmdlist] if not isinstance(cmdlist, list) else cmdlist
            for cmd in cmdlist:
                tn.write(cmd+'\r\n')
                gv.logger.info('Send command: ' +cmd)
                time.sleep(delay)
                response = tn.read_very_eager()
                gv.logger.info('Get Response : ' +response)
                ret += response
        finally:
            tn.close()
    else:
        kw('report_error', 'Connect to PA failed')
    return ret


def pet_process_exist(pid):
    return len([x for x in os.popen('ps -ef|grep '+pid).readlines() if x.split()[1] == pid]) > 0


def start_cmdagent():
    import random
    cmd_port = random.randint(20000, 50000)
    print 'current port: ', cmd_port
    cmd_port = get_free_port(cmd_port + 1, 50000)
    print 'New port: ', cmd_port
    duration_time = 300 if gv.case.curr_case.case_duration == '' else gv.case.curr_case.case_duration
    os.system('python %s/cmdagent.py -m BTS%s -p %s -t %s &' %(resource_path(),
                      gv.master_bts.bts_id, cmd_port, int(duration_time) + 900))
    server_is_ok = False
    for i in range(int(10)):
        time.sleep(1)
        output = os.popen('netstat -na|grep %s|grep LISTEN' %(cmd_port)).readlines()
        if len(output) > 0:
            server_is_ok = True
            break
    if not server_is_ok:
        kw('report_error', 'Start cmdagent failed in 10 seconds.')
    import telnetlib
    gv.conn_agent = telnetlib.Telnet('127.0.0.1', str(cmd_port))
    gv.conn_agent.read_very_eager()
    gv.conn_agent.write('log Working for BTS: %s\n' %(gv.master_bts.bts_id))

def pet_execute_command_by_agent(cmd):
    if gv.conn_agent == None:
        kw('start_cmdagent')
        time.sleep(5)
    if gv.conn_agent:
        gv.conn_agent.sock.sendall('run %s' %(cmd))
        ret = ''
        for i in range(10):
            ret += gv.conn_agent.read_very_eager()
            if 'done' in ret:
                break
            time.sleep(1)
        kw('log', 'command result: [%s]' %(ret))
        if ret.strip():
            pid = [x for x in ret.splitlines() if 'PID:' in x][0].replace('done','').split()[-1].strip()
            gv.case.cmd_list.append(pid)
            return pid
        else:
            return ''
    else:
        kw('connection to cmd server failed')

def pet_stop_command_by_agent(pid):
    gv.conn_agent.write('stop %s\n' %(pid))
    try:
        gv.case.cmd_list.remove(pid)
    except:
        pass
    if len(gv.case.cmd_list) == 0:
        kw('stop_cmdagent')

def pet_send_key_to_command_by_agent(pid, key):
    gv.conn_agent.write('sendkey %s %s\n' %(pid, key))

def stop_cmdagent():
    if gv.conn_agent:
        gv.conn_agent.write('quit\n')
        gv.conn_agent.close()
        gv.conn_agent = None

def get_cpu_usage(ip, port, username, password):
    cmd = 'sshpass -p %s ssh -p %s %s@%s  "top -n 1 -b |grep Cpu"' %(
        password, port, username, ip
        )
    output = run_local_command_gracely(cmd).splitlines()
    line = [x for x in output if x.strip() and 'Cpu(s)' in x ][0]
    return float(line.split()[1].split(r'%')[0])


def test_tool(arg):
    print 'test tool', arg









if __name__ == '__main__':
    # from BtsShell.file_lib.xml_control import common_xml_operation
    # filename = r'd:\temp\6\PM.BTS-228.20150306.040000.LTE.xml'
    # config = read_bts_config('1815')
    # get_scf_params_for_volte()
    # print get_cpu_usage('10.69.64.124', '22', 'root', 'artiza')
    # print get_case_config_new('478010')
    # gv.team = 'pet1'
    # print "XXXXXXXXXXXXXXXXXXXXXXXX",get_case_config('478010')
    # # print 'result %s' %(cmp(get_case_config_new('265174'), get_case_config('265174')))
    gv.team = r'PET1'
    case = get_case_config_new('529732')
    print case
    # case_compare('603432')
    # print case
    pass


