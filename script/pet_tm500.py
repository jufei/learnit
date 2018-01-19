import os, time, telnetlib
from thread import *
from petbase import *
import pettool
from pet_tm500_asc import *
from pet_tm500_script import get_tput_attach_script
from ftp_lib import download_from_ftp_to_local, upload_to_ftp_from_local

import threading
console_lock = threading.Lock()

#Keywords for TM500 Control PC,
def connect_to_tm500_control_pc():
    if not gv.tm500.conn_pc or not tm500_control_pc_conn_is_available():
        gv.tm500.conn_pc = connections.connect_to_host(gv.tm500.tm500_control_pc_lab, '23',
            gv.tm500.tm500_control_pc_username, gv.tm500.tm500_control_pc_password)
        # spv('${TM500_CONTROL_PC_CONNECTION}',gv.tm500.conn_pc)
    connections.switch_host_connection(gv.tm500.conn_pc)

def execute_command_on_tm500_control_pc(cmds):
    connect_to_tm500_control_pc()
    return pettool.execute_command_on_pc(cmds)

def run_keyword_on_tm500_control_pc(kwname, *args):
    connect_to_tm500_control_pc()
    return kw(kwname, *args)

def config_tm500_control_pc():
    kw('execute_command_on_tm500_control_pc', ['tlntadmn config timeoutactive=no', 'tlntadmn config maxconn=1000'])

# Keyword for TMA (tcp ip connection to 5003 port)
def pet_connect_to_tma():
    if not gv.tm500.conn_tma:
        gv.tm500.conn_tma = connections.connect_to_tm500(gv.tm500.tm500_control_pc_lab, gv.tm500.tm500_control_port)
        kw('execute_command_on_tm500_control_pc', 'netstat -na|grep 5003')
        spv('${TM500_CONNECTION}', gv.tm500.conn_tma)
    connections.switch_host_connection(gv.tm500.conn_tma)

def pet_disconnect_tma():
    if gv.tm500.conn_tma:
        kw('pet_tm500_disconnect')
        output = kw('execute_command_on_tm500_control_pc', 'netstat -na|grep 5003')
        connections.switch_host_connection(gv.tm500.conn_tma)
        connections.disconnect_from_host()
        gv.tm500.conn_tma = None
        output = kw('execute_command_on_tm500_control_pc', 'netstat -na|grep 5003')
        if 'ESTABLISHED' in output:
            kw('report_error', 'The TM500 connection still exist, please close it first.')

def get_tm500_mode():
    tm500_mode = 'NAS_MODE'
    tm500_mode = 'MTS_MODE' if gv.case.curr_case.domain.upper() == 'VOLTE' else tm500_mode
    tm500_mode = 'MTS_MODE' if gv.case.curr_case.case_type.upper() in ['THROUGHPUT_MUE_DL',
                            'THROUGHPUT_MUE_UL', 'MIX_MR'] else tm500_mode
    tm500_mode = 'MTS_MODE' if gv.case.curr_case.domain.upper() == 'CAP' else tm500_mode
    return tm500_mode

def get_tm500_card():
    card = 'RC1_RC2' if gv.case.curr_case.domain in ['CPK', 'VOLTE', 'CAP', 'MR'] and gv.case.curr_case.ca_type in ['2CC'] else gv.tm500_radio_card
    card = 'RC1_RC2' if gv.case.curr_case.case_type == 'MIX_CAP' and gv.case.curr_case.ca_type in ['2CC'] else card
    card = 'RC1_RC2_T2-RC-A6' if gv.case.curr_case.ca_type.upper() in ['3CC'] else card
    if gv.case.curr_case.tm in ['98X4', '94X4', '4X4']:
        card = 'RC1_RC2'
    if (gv.case.curr_case.tm in ['4X4', '4X4-4X4'] and gv.case.curr_case.ca_type in ['2CC']) or (gv.master_bts.btstype == 'FDD' and gv.case.curr_case.ca_type in ['2CC']):
        card = 'RC1_RC2_T2-RC1_T2-RC2'
    if gv.case.curr_case.is_handover and gv.case.curr_case.ca_type in ['2CC']:
        card = 'RC1_RC2_T2-RC1_T2-RC2'
    if (gv.master_bts.btstype == 'FDD' and gv.case.curr_case.ca_type not in ['2CC', '3CC']):
        card = 'RC1_T2-RC1_T2-RC2'
    if gv.case.curr_case.case_type == 'MIX_MR':
        if gv.case.curr_case.is_handover and gv.case.curr_case.ca_type in ['2CC']:
            card = 'RC1_RC2_T2-RC1_T2-RC2'
        elif gv.case.curr_case.ca_type.upper() in ['3CC']:
            card = 'RC1_RC2_T2-RC-A6'
        elif gv.case.curr_case.is_handover:
            card = 'RC1_RC2'
        else:
            card = card
    card = gv.case.curr_case.tm500_radio_card if gv.case.curr_case.tm500_radio_card.strip() else card
    return card

def get_tm500_radio_content():
    context = '0'
    if gv.case.curr_case.tm in ['98X4', '94X4', '4X4']:
        context = '1'
    return context

# Keyword for TM500 (The real TM500 device, use special TM500 commands, to run these command, we use TMA connection)
def pet_tm500_connect():
    pet_connect_to_tma()
    kw('pet_tm500_disconnect')
    if gv.case.curr_case.tm500_attach_file:
        gv.logger.info('Used Fixed TM500 script, check if need connect')
        filename = bts_source_file(gv.master_bts.bts_id, gv.case.curr_case.tm500_attach_file)
        script = open(filename, 'r').read()
        if '$$CONNECT' in open(filename, 'r').read().upper():
            gv.logger.info('Fould CONNECT command, TA will not connect.')
            return 0

    mode = get_tm500_mode()
    card = get_tm500_card()
    context = get_tm500_radio_content()
    # ca_group = '1' if gv.case.curr_case.domain in ['VOLTE'] and gv.case.curr_case.ca_type in ['2CC'] else '0'
    ca_group = '0 1' if gv.case.curr_case.ca_type in ['2CC'] else '0'
    ca_group = '0 1 2' if gv.case.curr_case.ca_type in ['3CC'] and gv.case.curr_case.domain in ['CAP'] else ca_group
    ca_group = '0 1 2' if (gv.master_bts.btstype == 'FDD' and gv.case.curr_case.ca_type not in ['2CC', '3CC']) else ca_group
    ca_group = '0 1 2 3' if gv.master_bts.btstype == 'FDD' and gv.case.curr_case.ca_type in ['2CC'] else ca_group
    ca_group = '0 1 2 3' if gv.case.curr_case.is_handover and gv.case.curr_case.ca_type in ['2CC'] else ca_group
    ca_group = '0 1 2' if 'T2-RC-A6' in card else ca_group

    if ca_group == '0 1 2 3' or hasattr(gv.tm500, 'asc_powerbreaks'):
        output = kw('tm500_connect', card, context, '1', mode, ca_group)
    else:
        output = kw('tm500_connect', card, context, '0', mode, ca_group)
    if 'DL : 2570.0 - 2620.0 MHz' in output:
        gv.env.card_band = 'narrow-band'
    else:
        gv.env.card_band = 'wide-band'
    record_tm500log(output)
    fail_keywords = ['FAILURE', 'ERROR', 'LEAVE', 'DISCONNECTION']
    errorlines = contain_keywords(output, fail_keywords)
    # if len(errorlines) > 0:
    #     kw('report_error', 'Found eror: ' + ';'.join(errorlines))

def pet_tm500_disconnect():
    pet_connect_to_tma()
    connections.execute_tm500_command_without_check('#$$DISCONNECT')

def run_keyword_on_tm500(kwname, *args):
    pet_connect_to_tma()
    return kw(kwname, *args)

def update_tm500_ftp_server_config(version):
    filename = case_file('ftpserver.xml')
    if has_attr(gv.tm500, 'filezilla_path'):
        if gv.tm500.filezilla_path:
            url = 'ftp://%s/%s/FileZilla Server.xml' %(gv.tm500.tm500_control_pc_lab, gv.tm500.filezilla_path)
    else:
        url = 'ftp://%s//Program Files/FileZilla Server/FileZilla Server.xml' %(gv.tm500.tm500_control_pc_lab)
    print url
    download_from_ftp_to_local(url, filename, 'bin', 'filec', 'filec')
    if hasattr(gv.tm500, 'asc_filezilla_user'):
        user = gv.tm500.asc_filezilla_user
    else:
        user = 'tm500'
    if filezilla_server_check_tma_version_new(to_winpath(version), filename, user):
        upload_to_ftp_from_local(url, filename, 'bin', 'filec', 'filec')
        filezilla_server_restart(gv.tm500.conn_pc)



def pet_restart_tm500(interval='10'):
    # gv.logger.info(gv.tm500)
    tm500_version_dir = _get_tma_path()
    # if gv.env.tm500_path:
    #     tm500_version_dir = gv.env.tm500_path
    # else:
    #     gv.case.curr_case.tm500_version = 'K' if gv.case.curr_case.tm500_version == '' else gv.case.curr_case.tm500_version
    #     version = 'TM500_APPLICATION_%s_VERSION_DIR' %(gv.case.curr_case.tm500_version)
    #     tm500_version_dir = getattr(gv.tm500, version.lower())
    #     kw('log', version)
    kw('update_tm500_ftp_server_config', tm500_version_dir)
    gv.tmapath = tm500_version_dir.replace('"', '') + 'Test Mobile Application/TMA.exe'
    kw('run_keyword_and_ignore_error', 'try_to_disconnect_connection_to_apc', gv.tm500.tm500_powerbreak_port)
    if gv.tm500.use_asc:
        kw('setup_asc_before_tm500_restart')
        if hasattr(gv.tm500, 'asc_powerbreaks'):
            for pbconfig in gv.tm500.asc_powerbreaks:
                kw('pet_restart_device_by_power_break_apc', pbconfig, interval)
    kw('pet_restart_device_by_power_break_apc', gv.tm500.tm500_powerbreak_port, interval)
    kw('pet_disconnect_tma')

def tm500_suite_setup():
    pass

def tm500_suite_teardown():
    pass

def tm500_case_setup():
    gv.tm500.output = []
    kw('pet_tm500_firmware_upgrade_if_needed')
    if gv.need_upgrade_tma:
        kw('restart_tma')
    else:
        kw('start_tma_if_needed')
    if gv.case.case_index > 1 and not gv.env.restart_tm500_for_each_case:
        kw('sleep', '60')
    if gv.tm500.use_asc:
        kw('setup_asc_after_tm500_restart')
    kw('pet_tm500_connect')

def tm500_case_teardown():
    save_log(gv.tm500.output, case_file('tm500output.log'))
    kw('pet_disconnect_tma')

def prepare_ue_attach():
    kw('pet_bts_cells_should_be_ok')

def pet_ue_attach():
    kw('pet_bts_read_scf_file', gv.master_bts.bts_id, gv.master_bts.scf_filename)
    pet_connect_to_tma()
    #kw('sleep', '10')
    lines = get_tput_attach_script(gv.master_bts)
    lines = [line.replace('\n', '') for line in lines if not re.match('(^(\r|\n|\s+)$)|(^$)|^#', line)] # remove all the unnecessary lines including comment
    save_log(lines, case_file('real_attach.txt'), 'N')
    output = ''
    for line in lines[:-1]:
        output += connections.execute_tm500_command_without_check(line, '2048', '0')
    output += connections.execute_tm500_command_without_check(lines[-1], '2048', '10', 'Mode: PS')
    save_log(output.splitlines(), case_file('attach_result.log'))
    record_tm500log(output)

    if (not 'L2 RANDOM ACCESS COMPLETE' in output) or (not 'ACCESS POINT NAME' in output):
        kw('report_error', 'Attach failed, Please check it.')
    gv.logger.info(output)
    gv.service.ue_ip = get_ue_ip(output)
    # try:
    #     connections.execute_tm500_command_without_check('forw mte getstats [6]', '2048', '0')
    # except:
    #     pass

def wait_until_find_expected_string_in_tm500_output(timeout, interval, expect_str):
    from robot.utils import timestr_to_secs
    kw('pet_connect_to_tma')
    st = time.time()
    found = False
    output = ''
    while time.time() - st <= timestr_to_secs(timeout):
        ret = connections.read_tm500_output()
        if ret.strip():
            record_tm500log(ret)
            # connections.save_tm500_log(ret)
            gv.logger.info(ret)
            output += ret
            if isinstance(expect_str, list):
                if [x for x in expect_str if x.upper() in output.upper()]:
                    found = True
                    break
            else:
                if expect_str.upper() in output.upper():
                    found = True
                    break
        time.sleep(timestr_to_secs(interval))
    if not found:
        kw('report_error', 'Could not find [%s] in TM500 output in %d seconds.' %(expect_str, timestr_to_secs(timeout)))
    else:
        return output

def set_tm500_log_types():
    pet_connect_to_tma()
    version = gv.case.curr_case.tm500_version
    if version.strip() and has_attr(gv.tm500, 'tm500_log_type_file_'+ version.lower()):
        logtypefile = getattr(gv.tm500, 'tm500_log_type_file_'+ version.lower())
    else:
        logtypefile = gv.tm500.tm500_log_type_file
    log_types = gv.case.curr_case.case_info.tm500_log_types
    gv.logger.info('[%s] [%s]' %(gv.case.curr_case.ca_type.upper().strip(),
                                 gv.case.curr_case.case_type.upper().strip()))
    if gv.case.curr_case.ca_type.upper().strip() == '3CC' and gv.case.curr_case.case_type.upper().strip() == 'FTP_DOWNLOAD':
        log_types = ['L1DLRSPOWER', 'ProtocolLog', 'L1DLSTATS', 'CARRIERTHROUGHPUTTEXT']

    if gv.case.curr_case.case_type in ['FTP_UPLOAD'] and gv.case.curr_case.tm500_version in ['L']:
        log_types = ['SYSOVERVIEW', 'L1ULSTATS', 'L1CELLULOVERVIEW']

    if gv.case.curr_case.case_type in ['MIX_CAP']:
        log_types = ['L1CELLDLOVERVIEW', 'L1CELLULOVERVIEW', 'SCCSTATUS', 'L1CELLWATCH', 'SYSOVERVIEW']

    output = kw('tm500_logging_select_from_file', pathc(tm500_source_file(logtypefile)),
                log_types,'0','0.1')
    record_tm500log(output)

def pet_start_tm500_logging():
    kw('pet_bts_cells_should_be_ok')
    pet_connect_to_tma()
    output = kw('execute_tm500_command', '#$$START_LOGGING')
    record_tm500log(output)
    gv.remote_tm500_log_dir = [x for x in output.splitlines() if 'CURRENT LOGGING FOLDER IS' in x][0].split("'")[1]


def pet_start_tm500_logging_2():
    kw('pet_bts_cells_should_be_ok')
    pet_connect_to_tma()
    output = kw('execute_tm500_command', '#$$START_LOGGING','2048','60')
    record_tm500log(output)
    gv.remote_tm500_log_dir = [x for x in output.splitlines() if 'CURRENT LOGGING FOLDER IS' in x][0].split("'")[1]

def pet_stop_tm500_logging():
    pet_connect_to_tma()
    record_tm500log(kw('execute_tm500_command', '#$$STOP_LOGGING'))

def pet_stop_tm500_logging_2():
    pet_connect_to_tma()
    record_tm500log(kw('execute_tm500_command', '#$$STOP_LOGGING','2048','60'))

def pet_tm500_convert_log_to_text(timeout):
    pet_connect_to_tma()
    record_tm500log(kw('tm500_convert_to_text', '3', timeout))

def pet_tm500_download_log_to_local(logtag):
    connect_to_tm500_control_pc()
    remotepath = gv.remote_tm500_log_dir.split(':')[-1].replace('\\', '/')
    gv.logger.info(remotepath)
    local_logpath = os.sep.join([gv.case.log_directory, logtag])
    os.makedirs(local_logpath)
    kw('ftp_download_files', gv.tm500.tm500_control_pc_lab, '21', 'TA_LOG', 'TA_LOG', '.csv', pathc(remotepath), pathc(local_logpath))
    kw('run_keyword_and_ignore_error','ftp_download_files', gv.tm500.tm500_control_pc_lab, '21', 'TA_LOG', 'TA_LOG', ".log", pathc(remotepath), pathc(local_logpath))
    gv.tm500.tm500_log_dir = local_logpath

def stop_tm500_logging_and_download_logs(logtag='tmlog', timeout = '300'):
    pet_connect_to_tma()
    kw('pet_stop_tm500_logging')
    kw('pet_tm500_convert_log_to_text', timeout)
    #download converted log files from TM500 control PC to local
    kw('pet_tm500_download_log_to_local', logtag)

def stop_tm500_logging_and_download_logs_2(logtag='tmlog', timeout = '300'):
    pet_connect_to_tma()
    kw('pet_stop_tm500_logging_2')
    kw('pet_tm500_convert_log_to_text', timeout)
    #download converted log files from TM500 control PC to local
    kw('pet_tm500_download_log_to_local', logtag)

def read_tm500_config(tm500_id):
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

    case = gv.case.curr_case
    if case.codec.strip():
        tm500config.shenick_volte_group_name += '_' + case.codec.upper()
    if 'volte_load' in [x.lower().strip() for x in dir(gv.case.curr_case) if x[0] <> '_']:
        if gv.case.curr_case.volte_load:
            tm500config.shenick_volte_group_name = 'TA_VOLTE_IMS_LOAD'
    if case.case_type == 'VOLTE_CAP':
        tm500config.shenick_volte_group_name = 'TA_VOLTE_IMS_FTP_WB2385'
    if case.case_type == 'MIX_MR':
        tm500config.shenick_volte_group_name = 'TA_Mixed_UDP_FTP'
    if case.case_type.strip().upper() in ['THROUGHPUT_MUE_UL', 'THROUGHPUT_MUE_DL']:
        tm500config.shenick_volte_group_name = 'TA_MUE_UL'
    if case.case_type in ['VOLTE_PERM', 'VOLTE_MIX', 'VOLTE_CAP']:
        tm500config.shenick_volte_group_name = 'TA_VILTE_PERM' if case.volte_service =='VIDEO' or case.is_mix else 'TA_VOLTE_PERM'

    return tm500config

def pet_tm500_resource_is_free(tm500_id):
    config = read_tm500_config(tm500_id)
    conn_pc = connections.connect_to_host(config.tm500_control_pc_lab, '23',
        config.tm500_control_pc_username, config.tm500_control_pc_password)
    output = connections.execute_shell_command_without_check('netstat -na|grep 30001')
    connections.disconnect_from_host()
    return False if 'LISTENING' in output else True

def pet_occupy_tm500_resource(timeout = '1800'):
    connect_to_tm500_control_pc()
    connections.execute_shell_command_without_check('psexec -u %s -p %s -i -d c:\\python27\\python c:\\python27\\resmgr.py -t ' + timeout %(gv.tm500.tm500_control_pc_username, gv.tm500.tm500_control_pc_password))
    print 'Start to occupy TM500 , timeout: [%s]' %(timeout)

def pet_release_tm500_resource():
    if not gv.smart_device:
        return
    output =  kw('execute_command_on_tm500_control_pc', 'netstat -a -o|grep 30001')
    print output
    line = [x for x in output.splitlines() if 'LISTENING' in x]
    if line:
        kw('execute_command_on_tm500_control_pc', 'taskkill /F /PID ' + line[0].split()[-1])
    print 'Stop to occupy TM500 '


def restart_tm500_if_needed():
    if (gv.debug_mode not in ['DEBUG']) or gv.env.restart_tm500_for_each_case:
        if gv.case.case_index == 1 or gv.env.restart_tm500_for_each_case:
            # if gv.case.curr_case.tm500_version <> gv.tm500.version and gv.case.curr_case.case_type.strip().upper() not in ['PING_DELAY_32','PING_DELAY_1400']:
            write_to_console('\nRestart TM500...')
            gv.logger.info('New case use different TM500 version, need to restart TM500 first')
            kw('pet_restart_tm500')
            gv.tm500.tm500_restarted = True
            gv.tm500_version = gv.case.curr_case.tm500_version
            if gv.case.case_index > 1:
                kw('wait_until_tm500_startup_succeed')
                if gv.tm500.use_asc:
                    kw('setup_asc_after_tm500_restart')
    else:
        gv.logger.info('TM500 does not need to restart.')

def _tma_is_alive():
    pet_connect_to_tma()
    print run_local_command_gracely('netstat -na|grep 5003')
    output = connections.execute_tm500_command_without_check('HELP', '2048', '0', '', 10)
    return 'TMA NO RESPONSE' not in output

def _start_tma():
    connect_to_tm500_control_pc()
    tmapath = to_winpath(_get_tma_path().replace('"', ''))  + 'Test Mobile Application\\\\TMA.exe'
    # if gv.env.tm500_path:
    #     tmapath = to_winpath(gv.env.tm500_path) + 'Test Mobile Application\\\\TMA.exe'
    # else:
    #     version = 'TM500_APPLICATION_%s_VERSION_DIR' %(gv.case.curr_case.tm500_version)
    #     tm500_version_dir = getattr(gv.tm500, version.lower())
    #     tmapath = to_winpath(tm500_version_dir.replace('"', '')) + 'Test Mobile Application\\\\TMA.exe'
    client = r'C:\\Python27\\lib\\site-packages\\BtsShell\\resources\\tools\\Server_Client\\client.exe'
    cmd  = r'"%s" localhost "%s" /u \\"Default User\\" /c y /p 5003 /a n\r\n' %(client, tmapath)
    kw('execute_shell_command_bare', cmd)
    kw('sleep', '5s')
    kw("execute_shell_command_without_check", '\x03')
    kw('wait_until_port_is_listening', '5003', '40')
    gv.tm500.conn_tma = None

def _kill_tma():
    connect_to_tm500_control_pc()
    output = connections.execute_shell_command_without_check('tasklist |grep TmaApplication')
    for line in output.splitlines():
        if 'TmaApplication.exe'.lower() in line.lower():
            pid = line.split()[1]
            connections.execute_shell_command_without_check('taskkill /PID %s /F' %(pid))
    if gv.tm500.conn_tma:
        output = connections.execute_shell_command_without_check('netstat -na|grep 5003')
        connections.switch_host_connection(gv.tm500.conn_tma)
        connections.disconnect_from_host()
        gv.tm500.conn_tma = None

def _tma_is_running():
    connect_to_tm500_control_pc()
    output = connections.execute_shell_command_without_check('tasklist |grep TmaApplication')
    for line in output.splitlines():
        if 'TmaApplication.exe'.lower() in line.lower():
            return True
    return False

def _tma_is_listening():
    connect_to_tm500_control_pc()
    found = False
    output = connections.execute_shell_command_without_check('netstat -na|grep 5003')
    return 'LISTEN' in output

def _get_tma_path():
    if gv.env.tm500_path:
        return gv.env.tm500_path
    else:
        version = 'TM500_APPLICATION_%s_VERSION_DIR' %(gv.case.curr_case.tm500_version)
        return getattr(gv.tm500, version.lower())


def start_tma_if_needed():
    if _tma_is_running():
        #TODO Check the running TMA version, if is not match, kill TMA and restart it.
        running_version = get_running_tma_version()
        config_version  = parse_tma_version(_get_tma_path())
        gv.logger.info('Running TMA: [%s] vs Needed TMA [%s]' %(running_version, config_version))
        if running_version <> config_version:
            _kill_tma()
            _start_tma()
        else:
            kw('log', 'TMA is Running and version is matched.')

        if _tma_is_listening():
            kw('log', 'TMA is listening.')
            if _tma_is_alive():
                kw('log', 'TMA is Alive, everything is OK.')
            else:
                kw('log', 'TMA is not Alive')
                _kill_tma()
                _start_tma()
        else:
            kw('log', 'TMA is not listening.')
            _kill_tma()
            _start_tma()
    else:
        kw('log', 'TMA is not running, TA will start it')
        _start_tma()

def restart_tma():
    _kill_tma()
    _start_tma()

def console_server_is_on():
    connect_to_tm500_control_pc()
    output = connections.execute_shell_command_without_check('netstat -na|grep 30002')
    if 'LISTENING' in output:
        return True
    else:
        return False

def start_console_server_if_needed():
    connect_to_tm500_control_pc()
    kw('stop_console_server_if_needed')
    kw("kill_process", ['hypertrm.exe', 'SecureCRT.exe', 'PUTTY.exe', 'HBTE Power Creator V6.0.0.8.exe', 'ProgrammableAttenuatorMatrix.exe'])
    connections.execute_shell_command_without_check('psexec -u %s -p %s -i -d c:\\python27\\python c:\\python27\\serial_server.py -r %s' %(gv.tm500.tm500_control_pc_username, gv.tm500.tm500_control_pc_password, gv.tm500.console_rate))
    kw('wait_until_port_is_listening', '30002', '5')

def stop_console_server_if_needed():
    kw('stop_to_monitor_tm500_console_output')
    connect_to_tm500_control_pc()
    output = connections.execute_shell_command_without_check('netstat -nao|grep 30002')
    for line in output.splitlines():
        if 'LISTENING' in line:
            pid = line.split()[-1]
            connections.execute_shell_command_without_check('taskkill /PID %s /F' %(pid))

def console_monitor_thread():
    while True:
        with console_lock:
            if gv.tm500.conn_tm500_console:
                ret = gv.tm500.conn_tm500_console.read_very_eager()
                if ret:
                    with open(case_file('tm500_console_output.time.log'), 'a') as f:
                        import datetime
                        now = datetime.datetime.now()
                        f.write('*****%s  %-20s *****\n' %(now.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3], ''))
                        f.write(ret)
                    with open(case_file('tm500_console_output.log'), 'a') as f:
                        f.write(ret)
                    if 'Loading... FTP transfer failed' in ret:
                        time.sleep(5)
                        gv.tm500.conn_tm500_console.write('\r\n')
                        gv.tm500.conn_tm500_console.write('@\r\n')
            else:
                return 0

def start_to_monitor_tm500_console_output():
    kw('start_console_server_if_needed')
    gv.tm500.conn_tm500_console = telnetlib.Telnet(gv.tm500.tm500_control_pc_lab, '30002')
    start_new_thread(console_monitor_thread ,())

def stop_to_monitor_tm500_console_output():
    if gv.tm500.conn_tm500_console:
        kw('run_keyword_and_ignore_error', 'execute_command_on_tm500_console', 'pca_Show')
        with console_lock:
            gv.tm500.conn_tm500_console.close()
            gv.tm500.conn_tm500_console = None

def execute_command_on_tm500_console(cmd):
    conn = telnetlib.Telnet(gv.tm500.tm500_control_pc_lab, '30002')
    try:
        conn.write(cmd + '\n')
        time.sleep(1)
        output = conn.read_very_eager()
        print output
    finally:
        conn.close()

def tm500_is_startup():
    filename = case_file('tm500_console_output.log')
    if not os.path.exists(filename) :
        kw('report_error', 'Have not found TM500 console trace file.')
    if not 'Router'.upper() in open(filename).read().upper():
        kw('report_error', 'TM500 has not startup.')

def wait_until_tm500_startup_succeed():
    if (gv.debug_mode not in ['DEBUG']) or gv.env.restart_tm500_for_each_case:
        from robot.utils import timestr_to_secs
        start_time = time.time()
        total_time = timestr_to_secs('300')
        while time.time() < start_time + total_time:
            try:
                tm500_is_startup()
                return 0
            except:
                time.sleep(5)

def restart_tm500_in_another_thread():
    start_new_thread(restart_tm500_if_needed, ())

def tm500_is_reacable():
    connect_to_tm500_control_pc()
    output = connections.execute_shell_command_without_check('ping %s -w 1 -n 1' %(gv.tm500.tm500_ip))
    if 'Lost = 0'.upper() in output.upper():
        return True
    else:
        return False

def pet_reboot_tm500():
    if not kw('tm500_is_reacable'):
        return False
    kw('run_keyword_and_ignore_error', 'execute_command_on_tm500_console', 'reboot')
    result = False
    total_time = 15
    interval = 1
    st = time.time()
    while time.time() - st <= total_time:
        if kw('tm500_is_reacable'):
            time.sleep(interval)
        else:
            result = True
            break
    return result

def pet_stop_pppoe_connection():
    connect_to_tm500_control_pc()
    kw('stop_pppoe_connection', gv.tm500.pppoe_connection)

def tm500_control_pc_conn_is_available():
    # output = run_local_command_gracely('netstat -na|grep %s:23' %(gv.tm500.tm500_control_pc_lab))
    # return 'ESTABLISHED' in output
    return True

def clear_mts():
    kw('pet_connect_to_tma')
    connections.read_tm500_output(1)
    output = connections.execute_tm500_command_without_check('FORW MTE DECONFIGRDASTOPTESTCASE')
    output += connections.execute_tm500_command_without_check('forw mte mtsclearmts')
    save_log(output.splitlines(), case_file('service_result.log'))

'''
    Follow keyword merged from BtsShell
'''

def tm500_connect(radio_card = '', radio_context = '0', chassis = '0', tm500_mode='NAS_MODE', ca_group = '0'):
    """This keyword connects to TM500.

    | Input Parameters | Man. | Description |
    | radio_card | No | if "" no card select, could be RC1 or RC2 or RC1_RC2 |
    | radio_context | No | radio card context defalut as 0 |
    | chassis | No | radio card chassis default as 0 |
    | tm500_mode | No | default as NAS_MODE, you can set as 'MTS_MODE' or others |
    Example
    | TM500 Connect |
    """

    ret = connections.execute_tm500_command_without_check('#$$CONNECT')
    # if ret.upper().find('OK') < 0 and ret.upper().find('ALREADY CONNECTED') < 0:
        # raise Exception, 'Connection to TM500 failed'
    ret += connections.execute_tm500_command('GSTS')

    if 'T2-RC-A6' in radio_card:    #added for 3CC
        ret += connections.execute_tm500_command('ABOT 0 0 1')

    if 'T2-RC1_T2-RC2' in radio_card or hasattr(gv.tm500, 'asc_powerbreaks'):
        ret += connections.execute_tm500_command('ABOT 0 0 0')
        ret += connections.execute_tm500_command('MULT 192.168.10.9')

    if ''!= radio_card:
        ret += _tm500_select_radio_card(radio_card, radio_context, chassis)

    if ca_group <> '0':
        ret += connections.execute_tm500_command('SCAG 0 %s' %(ca_group))

    # if 'T2-RC-A6' in radio_card:    #added for 3CC
    #     ret += connections.execute_tm500_command('SCAG 0 0 1 2')

    # if ca_group == '1': #Volte CA case,
    #     ret += connections.execute_tm500_command('SCAG 0 0 1')

    #connections.execute_tm500_command('EREF 0 0 0')
    ret += connections.execute_tm500_command('GETR')
    # change the pause time for 'SCFG' command in order to get the full reponse
    try:
        old_pause_time = connections.set_pause_time('10')
        # ret += connections.execute_tm500_command('SCFG %s'%tm500_mode)
        ret += connections.execute_tm500_command_without_check('SCFG %s'%tm500_mode, '2048', '10')
        ret += connections.execute_tm500_command('STRT')
        ret += connections.execute_tm500_command('GVER')
    finally:
        connections.set_pause_time(old_pause_time)
    return ret

def _tm500_select_radio_card(radio_card, radio_context = '0', chassis = '0'):
    """This keyword selects TM500 radio card.

    | Input Parameters | Man. | Description |
    | radio_card       | Yes  | radio card name, such as 'RC1' or 'RC2' |
    | radio_context    | No   | the radio context to be associated with radio card, default is 0 |
    | chassis          | No   | the chassis containing the radio card, default is 0 |

    Example
    | TM500 Select Radio Card | RC1 |
    | TM500 Select Radio Card | RC2 |
    """
    rc_num = 0
    ret = ''
    if 'RC1' in radio_card.upper():
        ret += connections.execute_tm500_command('SELR %d %d RC1 COMBINED' %(rc_num,int(chassis)))
        rc_num += 1
        ret += connections.execute_tm500_command('EREF 0 0 0')
    if 'RC2' in radio_card.upper().split('_'):
        if radio_context == '0':
            ret += connections.execute_tm500_command('SELR %d %d RC2 COMBINED' %(rc_num,int(chassis)))
            rc_num += 1
            ret += connections.execute_tm500_command('EREF 1 0 0')
        else:
            ret += connections.execute_tm500_command('ADDR %d %d RC2 COMBINED' %((rc_num-1),int(chassis)))
            ret += connections.execute_tm500_command('EREF 0 0 0')
    if 'T2-RC-A6' in radio_card.upper():
        ret += connections.execute_tm500_command('SELR %d %d T2-RC-A6 COMBINED' %(rc_num,int(chassis)))
        rc_num += 1
        ret += connections.execute_tm500_command('EREF 2 0 0')

    if 'T2-RC1' in radio_card.upper():
        ret += connections.execute_tm500_command('SELR %d %d T2-RC1 COMBINED' %(rc_num,int(chassis)))
        rc_num += 1
        ret += connections.execute_tm500_command('EREF %d 0 0'%(rc_num-1))
    if 'T2-RC2' in radio_card.upper():
        if radio_context == '0':
            ret += connections.execute_tm500_command('SELR %d %d T2-RC2 COMBINED' %(rc_num,int(chassis)))
            rc_num += 1
            ret += connections.execute_tm500_command('EREF %d 0 0'%(rc_num-1))
        else:
            ret += connections.execute_tm500_command('ADDR %d %d T2-RC2 COMBINED' %((rc_num-1),int(chassis)))
            ret += connections.execute_tm500_command('EREF 0 0 0')

    # ret_tmp = ''
    # rc_number = 0
    # card_list = radio_card.upper().split('_')
    # for card in card_list:
    #     ret_tmp += connections.execute_tm500_command('SELR %d %d %s COMBINED' %(rc_number,int(chassis),card))
    #     rc_number +=1
    return ret


def tm500_get_version():
    """This keyword gets TM500 version.

    | Input Parameters | Man. | Description |

    Example
    | TM500 Get Version |
    """
    old_pause_time = connections.set_pause_time('5')
    ret = connections.execute_tm500_command_without_check('GVER', '65536')
    connections.set_pause_time(old_pause_time)
    ret = ret.upper()
    TMA_info_list = 'unkonwn'
    flag = False
    global TMA_VERSION
    Version_label_SK = re.compile('VERSION LABEL: LTE-(\w+)-\w+_\w+_\w+_\w+_(\w+)_(\w+)_(\w+)_REV(\d+)',re.M)
    Version_label_LMB = re.compile('VERSION LABEL: LTE-(\w+)-\w+_\w+_\w+_(\w+)_(\w+)_(\w+)_REV(\d+)',re.M)

    ret_SK = Version_label_SK.search(ret)
    ret_LMB = Version_label_LMB.search(ret)

    if ret_SK:
        TMA_info_list = ret_SK.groups()
        flag = True
    elif ret_LMB:
        TMA_info_list = ret_LMB.groups()
        flag = True
    if flag:
        TMA_info_list = list(TMA_info_list)
        TMA_version_title = TMA_info_list.pop(0)

        temp_str = ''
        for item in TMA_info_list:
            temp_str = temp_str + item
        TMA_version_id = int(temp_str)
        TMA_VERSION = TMA_version_title,TMA_version_id


def tm500_logging_select_from_file(log_file_path,
                                    log_option='ProtocolLog',
                                    number_of_ue='0',
                                    pause_time='0.5'):
    file_content = open(log_file_path).read()
    log_options = []
    if number_of_ue == '0':
        log_opt_cmds = ['#$$LC_CLEAR_ALL',
                        '#$$LC_UE_GROUP "" "0"',
                        '#$$LC_ITM 1 1 1 Manual']
        file_content_new = file_content.replace('UE All', 'UE 0')
    else:
        num = int(number_of_ue)-1
        log_opt_cmds = ['#$$LC_CLEAR_ALL',
                        '#$$LC_UE_GROUP "" "0-%s"' %num,
                        '#$$LC_ITM 1 1 1 Manual']
        file_content_new = file_content.replace('UE All', 'UE 0-%s'%num)
    file_content = file_content_new.splitlines()
    if not isinstance(log_option, list):
        log_options.append(str(log_option))
    else:
        log_options = log_option

    for content in file_content:
        for log in log_options:
            if log in content:
                log_opt_cmds.append(content.strip())
                break

    log_opt_cmds.append('#$$LC_ITM 0 0 0 Automatic')
    log_opt_cmds.append('#$$LC_END')
    old_pause_time = connections.set_pause_time(pause_time)

    ret = ''
    try:
        for cmd in log_opt_cmds:
            #print cmd
            ret += connections.execute_tm500_command_without_check(cmd, '2048', '0')
    finally:
        connections.set_pause_time(old_pause_time)
    return ret

def tm500_convert_to_text(pause_time='3', timeout='30'):
    old_PauseTime = connections.set_pause_time(pause_time)
    try:
        start_time = time.time()
        timeout = int(timeout)
        ret_1 = ''
        ret_2 = connections.execute_tm500_command_without_check('#$$CONVERT_TO_TEXT 0', '16777216')
        ret_1_2 = ret_1 + ret_2
        # while (ret_1_2.upper().find('CONVERT_TO_TEXT 0X00 OK') < 0) and ((time.clock()- start_time) < timeout):
        while (ret_1_2.upper().find('C: CONVERT_TO_TEXT') < 0) and ((time.time()- start_time) < timeout):
            ret_1 = ret_2
            ret_2 = connections.get_recv_content(65536)
            ret_1_2 = ret_1 + ret_2
    finally:
        connections.set_pause_time(old_PauseTime)
    return ret_1_2

def filezilla_server_check_tma_version(TM500_APP_DIR, src_file):
    if 'REV' in TM500_APP_DIR:
        tmp = re.search("^.*(LTE.*REV\d{2,3}).*", TM500_APP_DIR)
    else:
        tmp = re.search("^.*(LTE.*).*", TM500_APP_DIR)
    target_version = tmp.group(1).replace('"','').replace('\\', '')
    print 'target:  ', target_version
    xml = ParseXML(src_file)
    aero_permissions = xml.find_ele_by_part_attr("Permission", "Dir", 'Aeroflex')
    modified = False
    for permission in aero_permissions:
        dire = xml.get_ele_attr(permission, "Dir")
        option, is_home_value = xml.get_ele_text_by_attr(permission, "Name", "IsHome")
        print dire, is_home_value
        newvalue = '1' if target_version in dire else '0'
        print 'newvalue         ', newvalue
        if newvalue != is_home_value:
            xml.modify_ele_text(option, newvalue)
            modified = True
            print 'Update ftp server config, need restart ftp server.'
    xml.write_xml_file(src_file)
    return modified

def filezilla_server_check_tma_version_new(TM500_APP_DIR, src_file, user = 'tm500'):
    if 'REV' in TM500_APP_DIR:
        tmp = re.search("^.*(LTE.*REV\d{2,3}).*", TM500_APP_DIR)
    else:
        tmp = re.search("^.*(LTE.*).*", TM500_APP_DIR)
    target_version = tmp.group(1).replace('"','').replace('\\', '')
    print 'target:  ', target_version
    from lxml import etree
    tree = etree.parse(src_file)
    node_list = tree.xpath('//FileZillaServer/Users/User[@Name="%s"]/Permissions/Permission' %(user))
    print node_list
    modified = False
    for node in node_list:
        node_dir = [x for x in node.get('Dir').split('\\') if 'LTE' in x][0]
        is_home_value = node.xpath('Option[@Name="IsHome"]')[0].text
        print node_dir, str(is_home_value)
        if node_dir <> target_version and is_home_value == "1":
            modified = True
            node.xpath('Option[@Name="IsHome"]')[0].text = "0"
        if node_dir == target_version and is_home_value == "0":
            modified = True
            node.xpath('Option[@Name="IsHome"]')[0].text = "1"
    tree.write(src_file)
    print modified
    return modified


file_zilla_exe_path = "C:\\Program Files\\FileZilla Server\\FileZilla server.exe"
file_zilla_xml_path = "C:\\Program Files\\FileZilla Server\\FileZilla server.xml"
def filezilla_server_restart(connection='local', path=file_zilla_exe_path):
    if 'local' == connection:
        if not os.path.exists(path):
            raise Exception, "'%s' is not exist."%path
        if 0 != os.system('\"%s\" /stop' % path):
            raise Exception, "FileZilla Server stop failed"
        time.sleep(5)
        if 0 != os.system('\"%s\" /start' % path):
            raise Exception, "FileZilla Server start failed"
        print "FileZillar restart OK!"
    else:
        connections.switch_host_connection(connection)
        ret = connections.execute_shell_command_without_check('\"%s\" /stop' % path)
        time.sleep(5)
        ret = connections.execute_shell_command_without_check('\"%s\" /start' % path)

def get_ue_ip(information):
    ue_ip = []
    import re
    IP_PATTERN = "(25[0-5]|2[0-4]\d|[01]?\d\d?)\.(25[0-5]|2[0-4]\d|[01]?\d\d?)\.(25[0-5]|2[0-4]\d|[01]?\d\d?)\.(25[0-5]|2[0-4]\d|[01]?\d\d?)"
    info_list = information.split('\n')
    try:
        for item in info_list:
            m = re.search(IP_PATTERN,item)
            if m:
                ue_ip.append(m.group())
        if  len(ue_ip) == 1:
            ue_ip = ue_ip[0]
        return ue_ip
    finally:
        if len(ue_ip) == 0:
            raise Exception, "Do not contain any IP information"

def get_ue_ip2(information):
    ue_ip = ''
    for line in information.splitlines():
        if 'IPv4 Address:' in line:
            ue_ip = line.split(':')[-1].strip()
            break
    if ue_ip:
        return ue_ip
    else:
        kw('report_error', "Do not contain any IP information")

def parse_tma_version(verstring):
    import re
    version = re.findall(r'LTE[.A-Z\d\s-]*', verstring)
    if version:
        return version[0]
    else:
        kw('report_error', "Cound not find the version info in [%s] " %(verstring))

def get_running_tma_version():
    output = execute_command_on_tm500_control_pc("wmic process where name='TmaApplication.exe' get ProcessID, ExecutablePath")
    cmdline = [line for line in output.splitlines() if r'LTE' in line.upper() and 'TM500' in line.upper()]
    if cmdline:
        kw('log', 'XXXXXX' + cmdline[0])
        return parse_tma_version(cmdline[0])
    else:
        kw('report_error', "No TMA is running!")

def execute_tm500_cmd_and_save_log(cmd = '', timeout = '0', expected_str = '', ignore_log = 'N'):
    if cmd:
        output = connections.read_tm500_output()
        output += connections.execute_tm500_command_without_check(command = cmd,
                                          delay_timer = timeout, exp_prompt = expected_str, ignore_output=ignore_log)
        save_log(['RUN COMMAND: %s\n' %(cmd)] + output.splitlines(), gv.tm500.tm500_cmd_output_file)
    else:
        output = connections.read_tm500_output()
        save_log(output.splitlines(), gv.tm500.tm500_cmd_output_file)
    return output

def _download_filezilla_config_file(localfilename):
    if has_attr(gv.tm500, 'filezilla_path'):
        if gv.tm500.filezilla_path:
            url = 'ftp://%s/%s/FileZilla Server.xml' %(gv.tm500.tm500_control_pc_lab, gv.tm500.filezilla_path)
    else:
        url = 'ftp://%s//Program Files/FileZilla Server/FileZilla Server.xml' %(gv.tm500.tm500_control_pc_lab)
    print url
    download_from_ftp_to_local(url, localfilename, 'bin', 'filec', 'filec')

def _get_current_running_tm500_version():
    filename = case_file('ftpserver.xml')
    _download_filezilla_config_file(filename)
    from lxml import etree
    tree = etree.parse(filename)
    node = tree.xpath('//FileZillaServer/Users/User[@Name="tm500"]/Permissions/Permission/Option[@Name="IsHome" and text()="1"]')
    if node:
        return [x for x in node[0].getparent().get('Dir').split('\\') if 'LTE' in x][0]
    return ''

def pet_tm500_firmware_upgrade_if_needed():
    if gv.suite.suite_index <> 1 or gv.case.case_index <>1:
        return 0
    if not gv.env.need_upgrade_tm500:
        return 0
    running_version = _get_current_running_tm500_version()
    major_version = running_version.split(' ')[2][0]
    gv.logger.info('Current FileZillaServer tm500 version:  {}, major: {}'.format(running_version, major_version))
    if major_version.upper() == gv.case.curr_case.tm500_version.upper():
        gv.logger.info('Running TM500 major version is matched, need not upgrade firmware.')
        return 0
    gv.logger.info('!!!!!Running TM500 major version is mismatched, need upgrade firmware.')
    kw('start_to_monitor_tm500_console_output')
    kw('pet_restart_tm500')
    _kill_tma()
    _start_tma()
    kw('wait_until_tm500_startup_succeed')
    gv.tm500.tm500_cmd_output_file = case_file('tm500_cmd.log')
    gv.tm500.output = []
    kw('pet_connect_to_tma')
    kw('pet_tm500_disconnect')
    result = execute_tm500_cmd_and_save_log('#$$CONNECT')
    result += execute_tm500_cmd_and_save_log('GSTS')
    result += execute_tm500_cmd_and_save_log('ABOT 0 0 0 ')
    result += execute_tm500_cmd_and_save_log('EREF 0 0 0')
    result += execute_tm500_cmd_and_save_log('GETR')
    result += execute_tm500_cmd_and_save_log('SCFG FW_UPDATE_MODE')
    result += execute_tm500_cmd_and_save_log('STRT')
    result += execute_tm500_cmd_and_save_log('GVER')
    wait_until_find_expected_string_in_tm500_output(120, 5, 'I: CMPI FUM Firmware Update ready')
    result += execute_tm500_cmd_and_save_log('forw fum updateradio')
    wait_until_find_expected_string_in_tm500_output(60*60, 5, 'I: CMPI FUM UMBRA Update Complete')
    logfile = case_file('tm500_console_output.log')
    if os.path.exists(logfile):
        os.remove(logfile)
    kw('pet_tm500_disconnect')
    kw('pet_restart_tm500', '30')
    _kill_tma()
    _start_tma()
    kw('wait_until_tm500_startup_succeed')


def pet_get_running_throughput_from_tm500():
    pet_connect_to_tma()
    dl_tput, ul_tput = 0, 0
    output = execute_tm500_cmd_and_save_log(cmd = 'forw MTE GETSTATS [0] [combined] [combined]', ignore_log = 'Y').upper().splitlines()
    for i in range(len(output)):
        if 'DL-SCH' in output[i]:
            print output[i+2]
            dl_tput = round(float(output[i+2].split('Throughput:'.upper())[1].split()[0])/(1024*1024), 4)
        if 'UL-SCH' in output[i]:
            print output[i+1]
            ul_tput = round(float(output[i+1].split('Throughput:'.upper())[1].split()[0])/(1024*1024), 4)
    return dl_tput, ul_tput


if __name__ == '__main__':
    # from pet_tm500 import read_tm500_config

    gv.team = 'PET1'
    gv.case = IpaMmlItem()
    from pettool import get_case_config_new
    gv.case.curr_case = get_case_config_new('472700')
    from petcasebase import re_organize_case
    re_organize_case()
    gv.master_bts = IpaMmlItem()
    gv.tm500_radio_card = 'RC2'
    gv.master_bts.btstype = 'TDD'
    print get_tm500_card()
    # from petcasebase import re_organize_case
    # re_organize_case()
    # print gv.case.curr_case

    # gv.tm500 = read_tm500_config(88)
    # print gv.tm500
    # gv.logger.info(gv.tm500)
    # gv.case.curr_case.tm500_version = 'K' if gv.case.curr_case.tm500_version == '' else gv.case.curr_case.tm500_version
    # version = 'TM500_APPLICATION_%s_VERSION_DIR' %(gv.case.curr_case.tm500_version)
    # tm500_version_dir = getattr(gv.tm500, version.lower())
    # gv.logger.info(tm500_version_dir)

    # pet_restart_tm500()

    # update_tm500_ftp_server_config_new(tm500_version_dir)
    # pet_connect_to_tma()
    # lines = open('/tmp/tm500.log').readlines()
    # lines = [line.replace('\n', '') for line in lines if not re.match('(^(\r|\n|\s+)$)|(^$)|^#', line)] # remove all the unnecessary lines including comment
    # output = ''
    # for line in lines:
    #     print line
    #     output += connections.execute_tm500_command_without_check(line, '2048', '0')
    # time.sleep(10)
    # output += connections.read_tm500_output()
    # # print 'XXXXXXXXXXXXX'

    # for line in output.splitlines():
    #     print line
    # lines = output.splitlines()
    # for i in range(len(lines)):
    #     if 'Pdn Id:1' in lines[i]:
    #         ueid = lines[i-1].split('UE Id:')[-1]
    #         ipaddr = lines[i+3].split()[-1]
    #         print ueid, ipaddr