import time, os, subprocess, datetime, telnetlib
from petbase import *
from thread import *
import threading
from ute_infomodel import ute_infomodel
import socket
import pettool
from pet_xml import *

def _get_bts(btsid = ''):
    if btsid == '':
        return gv.master_bts
    else:
        return [x for x in gv.allbts if x.btsid == btsid][0]

#Keywors for BTS Control PC
def connect_to_bts_control_pc(btsid = ''):
    bts = _get_bts(btsid)
    if not bts.conn_pc or not bts_control_pc_conn_is_available(btsid):
        bts.conn_pc = connections.connect_to_host(bts.bts_control_pc_lab, '23',
            bts.bts_control_pc_username, bts.bts_control_pc_password)
    connections.switch_host_connection(bts.conn_pc)

def execute_command_on_bts_control_pc(btsid = '', cmds = ''):
    connect_to_bts_control_pc(btsid)
    return pettool.execute_command_on_pc(cmds)

def execute_command_on_bts_control_pc_without_check(btsid = '', cmd = ''):
    connect_to_bts_control_pc(btsid)
    return connections.execute_shell_command_without_check(cmd)

def run_keyword_on_bts_control_pc(bstid, kwname, *args):
    connect_to_bts_control_pc(bts)
    return kw(kwname, *args)

def run_keyword_for_each_bts(btslist, kwname, *args):
    for bts in btslist:
        newargs = [bts.btsid] + list(args)
        return kw(kwname, *newargs)

def test_for_show_bts(btsid, another_args):
    print 'Show Bts id: ', btsid, another_args


def config_bts_control_pc(btsid = ''):
    execute_command_on_bts_control_pc(btsid, ['tlntadmn config timeoutactive=no',
                                              'tlntadmn config maxconn=1000'])

def pet_fct_is_reachable(btsid = ''):
    bts = _get_bts(btsid)
    output = execute_command_on_bts_control_pc_without_check(btsid, 'ping %s -n 1' % (bts.bts_fcm_ip))
    return 'Request timed out' not in output

def pet_s1_is_reachable(btsid = ''):
    bts = _get_bts(btsid)
    return os.system('ping -c 1 -W 1 %s >/dev/null' % (bts.bts_ip)) == 0

def pet_fcm_is_reachable(btsid = ''):
    bts = _get_bts(btsid)
    output = connections.execute_shell_command_without_check('ping %s -n 1' % (bts.bts_ftm_ip))
    return 'Request timed out' not in output

def forcely_recovery_bts_if_needed(btsid = ''):
    bts = _get_bts(btsid)
    kw('connect_to_bts_control_pc', btsid)
    if not pet_fct_is_reachable(btsid):
        if pet_fcm_is_reachable(btsid):
            kw('run_keyword_and_ignore_error', 'pet_disable_ethernet_port_security', btsid)
        else:
            kw('power_control_for_facom', 'OFF', bts.bts_powerbreak_port)
            kw('sleep', '5s')
            kw('power_control_for_facom', 'ON', bts.bts_powerbreak_port)
            kw('wait_until_fct_is_reachable', btsid)
    kw('try_to_enable_ssh', btsid)

# Kewyord for BTS
def pet_connect_to_bts(btsid = ''):
    if pet_s1_is_reachable(btsid):
        bts = _get_bts(btsid)
        if not bts.conn_bts:
            gv.logger.info('Setup SSH connection for BTS: '+ btsid)
            prompt = pettool.get_ssh_prompt(bts.bts_ip, 22, bts.bts_fcm_username, bts.bts_fcm_password)
            bts.conn_bts = connections.connect_to_ssh_host(bts.bts_ip, '22', bts.bts_fcm_username, bts.bts_fcm_password, prompt)
        else:
            connections.switch_ssh_connection(bts.conn_bts)
    else:
        kw('report_error', 'BTS S1 ip is not reacable, please check it.')

def pet_connect_all_bts():
    for bts in gv.allbts:
        kw('pet_connect_to_bts', bts.bts_id)

def pet_connect_all_bts_control_pc():
    for bts in gv.allbts:
        kw('connect_to_bts_control_pc', bts.bts_id)

def execute_command_on_bts(btsid = '', cmds = ''):
    pet_connect_to_bts(btsid)
    if isinstance(cmds, list):
        output = ''
        for command in cmds:
            output += connections.execute_ssh_command_without_check(command)
        return output
    else:
        return connections.execute_ssh_command_without_check(cmds)

def execute_simple_command_on_bts(btsid = '', cmd = '', keyword=''):
    # if pet_s1_is_reachable(btsid):
    bts = _get_bts(btsid)
    tcmd = 'sshpass -p %s ssh %s@%s  -o StrictHostKeyChecking=no  %s' % (bts.bts_fcm_password, bts.bts_fcm_username, bts.bts_ip, cmd)
    out = run_local_command_gracely(tcmd)
    if keyword.strip():
        for i in range(5):
            if keyword.upper() in out.upper():
                break
            # time.sleep(10)
            print 'Retry for: ', i+1
            out = run_local_command_gracely(tcmd)
    output = [x.replace('\n', '') for x in out.splitlines()]
    return output
    # else:
    #     kw('report_error', 'BTS S1 ip is not reacable, please check it.')

def run_keyword_on_bts(btsid, kwname, *args):
    pet_connect_to_bts(btsid)
    return kw(kwname, *args)

def upload_file_to_bts(btsid, localfilename, remote_filename, remote_path):
    bts = _get_bts(btsid)
    gv.logger.info('upload file:  ' + remote_path + '/' + remote_filename)
    cmd = "sshpass -p '%s' scp %s %s@%s:%s" % (bts.bts_fcm_password,
        localfilename, bts.bts_fcm_username, bts.bts_ip, remote_path + '/' + remote_filename)
    run_local_command_gracely(cmd)

def download_file_from_bts(btsid, localfilename, remote_filename, remote_path):
    bts = _get_bts(btsid)
    gv.logger.info('download file:  ' + remote_path + '/' + remote_filename)
    cmd = "sshpass -p '%s' scp %s@%s:%s %s" % (bts.bts_fcm_password,
        bts.bts_fcm_username, bts.bts_ip, remote_path + '/' + remote_filename, localfilename)
    run_local_command_gracely(cmd)

def stop_tshark_on_bts(btsid = ''):
    kw('execute_command_on_bts', btsid, 'killall tcpdump')

def start_tshark_on_bts(btsid = ''):
    bts = _get_bts(btsid)
    kw('run_keyword_and_ignore_error', 'stop_tshark_on_bts', btsid)
    interface = 'br1' if bts.airscale  else 'eth3'
    kw('execute_command_on_bts', btsid, 'tcpdump -i %s sctp -w /tmp/local.pcap &' %(interface))

def new_parse_pcap_file(pcapfilename):
    def _get_time(timestamp):
        p = [x for x in timestamp.split() if ':' in x][0].split(':')
        return float(p[0])*3600+float(p[1])*60+float(p[2])
    import subprocess
    cmd = 'tshark -r %s s1ap' %(pcapfilename)
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=open(os.devnull,'w'), shell=True)
    lines, error = p.communicate()
    lines = lines.splitlines()

    cmd = 'tshark -r %s s1ap -T fields -e frame.time' %(pcapfilename)
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=open(os.devnull,'w'), shell=True)
    timestamps, error = p.communicate()
    timestamps = timestamps.splitlines()
    timestamps = [_get_time(x) for x in timestamps]
    for i in range(len(timestamps)):
        txt = lines[i].split()
        lines[i] = ' '.join([txt[0], str(timestamps[i])]+txt[2:])
    return lines


def convert_tshark_files(btsid = ''):
    pcapfile = case_file('local.pcap')
    kw('download_file_from_bts', btsid, pathc(pcapfile), 'local.pcap', '/tmp')
    if os.path.exists(pcapfile):
        output = new_parse_pcap_file(pcapfile)
        with open(case_file('local.txt'), 'a') as f:
            for line in output:
                f.write(line.replace('\n', '') +'\n')

def stop_and_download_tshark(btsid = ''):
    stop_tshark_on_bts(btsid)
    kw('download_file_from_bts', btsid, pathc(case_file('local.pcap')), 'local.pcap', '/tmp')

def stop_tshark_and_parse_file(btsid = ''):
    stop_tshark_on_bts(btsid)
    convert_tshark_files(btsid)

def get_tti_trace(btsid='', mode = 1):
    bts = _get_bts(btsid)
    ttipath = '/data/pylib/tools/ttitrace'
    if os.path.exists(os.sep.join([ttipath, gv.env.bts_version])):
        print gv.env.bts_version
        ttipath = os.sep.join([ttipath, gv.env.bts_version])
    else:
        # version_prefix = gv.env.bts_version.split('_')[0] #To do: for each bts version
        version_prefix = bts.version.split('_')[0]
        print version_prefix
        dirlist = [dirname for dirname in os.listdir(ttipath) if version_prefix in dirname]
        if len(dirlist) == 0:
            kw('report_error', 'Could not find available ttiTrace tool')
        dirlist.sort()
        ttipath = os.sep.join([ttipath, dirlist[-1]])
    gv.logger.debug(ttipath)
    if mode == 1:
        bts.tti.stream = os.sep.join([ttipath, 'sicftp'])
    else:
        bts.tti.stream = os.sep.join([ttipath, 'ttiStream'])
    if bts.btstype == 'TDD':
        bts.tti.ttiparser = os.sep.join([ttipath, 'DevC_tti_trace_parser_64'])
    else:
        bts.tti.ttiparser = os.sep.join([ttipath, 'tti_trace_parser_wmp-linux.exe'])
    os.system('chmod +x ' + bts.tti.stream)
    os.system('chmod +x ' + bts.tti.ttiparser)
    gv.logger.debug(bts.tti.stream)
    gv.logger.debug(bts.tti.ttiparser)

def get_tti_core_info(btsid):
    bts = _get_bts(btsid)
    if bts.sw_release == 'RL55':
        bts.tti.core_info = '1231,1234'
        return
    if bts.sw_release in ['RL65', 'TL15A', 'TL16', 'TL16A'] and bts.cell_count == 1:
        bts.tti.core_info = '1232,1233'
        return
    from pettool import execute_command_on_telnet
    output = execute_command_on_telnet(bts.bts_control_pc_lab, '15007','getCellMapping @RROMexe', 0.5)
    title = [x for x in output.splitlines() if 'MACULTTI' in x][0]
    p1, p2 = title.find('MACULTTI'), title.find('MACDLTTI')
    cores = ','.join(['%s,%s' %(line[p1:p1 + 6], line[p2:p2 + 6])  for line in output.splitlines() if '0x' in line])
    bts.tti.core_info = cores.replace('0x', '')

def wait_until_get_core_info(btsid):
    kw('wait_until_keyword_succeeds', '120', '5', 'get_tti_core_info', btsid)

def start_tti_trace(btsid):
    bts = _get_bts(btsid)
    kw('get_tti_trace', btsid)
    kw('wait_until_get_core_info', btsid)
    cmd = str(' '.join([bts.tti.stream, '-c', bts.tti.core_info, '-q', '-n', bts.bts_control_pc_lab, '-o', case_file('TtiTrace')]))
    run_local_command_gracely(cmd)

def start_tti_trace2(btsid):
    bts = _get_bts(btsid)
    kw('get_tti_trace', btsid, 2)
    kw('wait_until_get_core_info', btsid)
    dest_dire = case_file('tti_%s/TtiTrace' %(btsid))
    if bts.btstype == 'FDD':
        cmd = str(' '.join([bts.tti.stream, '-c', bts.tti.core_info, '-n', bts.bts_control_pc_lab, '-m 5',  '-o', dest_dire]))
    else:
        cmd = str(' '.join([bts.tti.stream, '-c', bts.tti.core_info, '-n', bts.bts_control_pc_lab, '-m 5',  '-x 4', '-o', dest_dire]))
    kw('log', cmd)
    bts.tti.tti_process = kw('pet_execute_command_by_agent', cmd)

def stop_tti_trace(btsid):
    bts = _get_bts(btsid)

def stop_tti_trace2(btsid):
    bts = _get_bts(btsid)
    if bts.tti.tti_process:
        kw('pet_send_key_to_command_by_agent', bts.tti.tti_process, 'return')
        gv.case.cmd_list.remove(bts.tti.tti_process)
        if len(gv.case.cmd_list) == 0:
            kw('stop_cmdagent')
        bts.tti.tti_process = ''

def reboot_bts(btsid = ''):
    bts = _get_bts(btsid)
    pet_connect_to_bts(btsid)
    kw('execute_simple_command_on_bts', btsid, 'reboot')
    result = False
    total_time = 120
    interval = 2
    st = time.time()
    while time.time() - st <= total_time:
        if kw('pet_fct_is_reachable', btsid):
            time.sleep(interval)
        else:
            result = True
            break
    bts.conn_bts = None
    return result

def wait_until_fct_is_not_reachable(btsid = ''):
    bts = _get_bts(btsid)
    result = False
    total_time = 180
    interval = 2
    st = time.time()
    while time.time() - st <= total_time:
        if kw('pet_fct_is_reachable', btsid):
            time.sleep(interval)
        else:
            bts.conn_bts = None
            return True
    raise Exception, 'FCT should be un-reachable in specific time.'


def earfcn_to_frequency(earfcn):
    frequency_base = [x*10 for x in [1812.5, 763, 1900, 2010, 1850, 1930, 1910, 2570, 1880, 2300, 2496, 3400, 3600, 703, 1447]]
    fcn_base = [1275, 9260, 36000, 36200, 36350, 36950, 37550, 37750, 38250, 38650, 39650, 41590, 43590, 45590, 46590, 46790]
    basefcn = [fcn for fcn in fcn_base if fcn <= int(earfcn)][-1]
    basefre = frequency_base[fcn_base.index(basefcn)]
    return int(int(earfcn) - basefcn + basefre)

def get_band_name(earfcn):
    fcn_base = [1275, 9260, 36000, 36200, 36350, 36950, 37550, 37750, 38250, 38650, 39650, 41590, 43590, 45590, 46590, 46790]
    fcn = [fcn for fcn in fcn_base if int(earfcn) >= fcn][-1]
    if fcn_base.index(fcn) == 0:
        return 3
    elif fcn_base.index(fcn) == 1:
        return 28
    else:
        return 31 + fcn_base.index(fcn)

def pet_get_bts_sw_version(btsid = ''):
    bts = _get_bts(btsid)
    output = execute_simple_command_on_bts(bts.bts_id, 'ls /ffs/run/Target*.xml', '.xml')
    line = [x for x in output if '.xml' in x][0]
    bts.version = '_'.join(line.split('/')[-1].split('.xml')[0].split('_')[1:])
    return '_'.join(line.split('/')[-1].split('.xml')[0].split('_')[1:])

def pet_get_bbu_version(btsid = ''):
    bts = _get_bts(btsid)
    output = execute_simple_command_on_bts(bts.btsid, 'cat /proc/device-tree/module-identity/unit-id')
    gv.logger.info(output[0])
    return output[0]

def pet_get_bts_version():
    bts = gv.master_bts
    ver = pet_get_bts_sw_version(bts.btsid)
    bbu_ver = pet_get_bbu_version(bts.btsid)
    print 'activeBuildVersion=%s' % (ver)
    print "****Current BTS version is '%s' *****" %(ver)
    kw('log', 'activeBuildVersion=%s' % (ver))
    kw('log', "****Current BTS version is '%s' *****" %(ver))
    kw('log', bbu_ver)
    if gv.env.bts_version == '':
        gv.env.bts_version = ver
    elif gv.env.bts_version <> ver:
        kw('report_error', 'Found BTS version mismatch, current: [%s] vs original: [%s], check if Rollback happened!' % (ver, gv.env.bts_version))

def pet_get_bts_uptime(btsid = ''):
    bts = _get_bts(btsid)
    output = execute_simple_command_on_bts(bts.bts_id, 'uptime', 'load')
    timeresult = output[0].split(',')[0].split('up')[1]
    if 'days' in timeresult:
        timeday = timeresult.split('days')[0]
        if 'min' in timeresult:
            timehour = 0
            timemin = timeresult.split('days')[1].split('min')[0]
        else:
            timehour = timeresult.split('days')[1].split(':')[0]
            timemin = timeresult.split('days')[1].split(':')[1]
    else:
        timeday = 0
        if 'min' in timeresult:
            timehour = 0
            timemin = timeresult.split('min')[0]
        else:
            timehour = timeresult.split(':')[0]
            timemin = timeresult.split(':')[1]
    uptime = int(timeday)*24*60 + int(timehour)*60 + int(timemin)
    return uptime
#BTSLOG part:
def pet_fct_should_be_reachable(btsid):
    if not kw('pet_fct_is_reachable', btsid):
        kw('report_error', 'FCT is not reachable yet.')

def pet_s1_should_be_reachable(btsid):
    if not kw('pet_s1_is_reachable', btsid):
        kw('report_error', 'S1 interface is not reachable yet.')

def wait_until_fct_is_reachable(btsid):
    kw('wait_until_keyword_succeeds', '600', '5', 'pet_fct_should_be_reachable', btsid)
    kw('wait_until_keyword_succeeds', '200', '5', 'pet_s1_should_be_reachable', btsid)
    kw('try_to_enable_ssh', btsid)

def btslog_contain_onair_flag(btsid = ''):
    bts = _get_bts(btsid)
    if not  'onAirDone'.upper()  in ''.join(bts.btslog_buffer).upper():
        kw('report_error', 'Have not found the onAirDone flag in btslog.')

def pet_prepare_infomodel(btsid = ''):
    if not gv.env.use_infomodel:
        return 0
    def get_infomodel_pid(bts):
        print 'ps -ef|grep java|grep %s' %(bts.bts_ip)
        return [x.split()[1] for x in os.popen('ps -ef|grep java|grep %s' %(bts.bts_ip)).readlines()]
    run_local_command('ps -ef|grep name')
    bts = _get_bts(btsid)
    path = case_file('')
    remote_path = '/ffs/run/swpool/OAM/meta_*.zip' if bts.airscale else '/ffs/run/meta_*.zip'
    print [x for x in execute_simple_command_on_bts(btsid, 'ls -la ' + remote_path) if 'meta_' in x]
    filename = [x for x in execute_simple_command_on_bts(btsid, 'ls -la ' + remote_path) if 'meta_' in x][0].split()[-1]
    gv.logger.info(filename)
    download_file_from_bts(btsid, path + filename.split('/')[-1], filename.split('/')[-1], '/'.join(filename.split('/')[:-1]))
    bts.infomodel_lock = threading.Lock()
    connected = False
    for pid in get_infomodel_pid(bts):
        if kw('pet_process_exist', pid):
            run_local_command('kill -9 ' + pid)
    try:
        bts.infomodel = ute_infomodel()
        bts.im_alias = btsid + time.strftime("_%Y_%m_%d__%H_%M_%S")
        bts.infomodel.setup_infomodel(address = bts.bts_control_pc_lab, port = 12345, definitions_file_path = path + filename.split('/')[-1], alias = bts.im_alias)
        for i in range(24):
            try:
                bts.infomodel.connect_infomodel(alias = bts.im_alias)
                connected = True
                break
            except:
                record_debuginfo('Connect to infomodel failed, I will try later!')
                time.sleep(5)
        if not connected:
            kw('report_error', 'Could not connect infomodel successfully in 2 minutes')
        bts.infomodel.start_infomodel_logger(alias = bts.im_alias)
    finally:
        bts.infomodel_pid = get_infomodel_pid(bts)
        gv.logger.info(bts.infomodel_pid)
    run_local_command('ps -ef|grep name')

def finish_infomodel(btsid = ''):
    if not gv.env.use_infomodel:
        return 0
    bts = _get_bts(btsid)
    run_local_command('ps -ef|grep name')
    if bts.infomodel:
        oldmodel = bts.infomodel
        bts.infomodel = None
        try:
            try:
                oldmodel.save_infomodel_log(case_file('infomodel_%s_%s' % (bts.bts_id, time.strftime("%Y_%m_%d__%H_%M_%S"))), alias = bts.im_alias)
            finally:
                oldmodel.teardown_infomodel(alias = bts.im_alias)
        finally:
            gv.logger.info(bts.infomodel_pid)
            for pid in bts.infomodel_pid:
                if kw('pet_process_exist', pid):
                    run_local_command('kill -9 ' + pid)
    run_local_command('ps -ef|grep name')

def start_infomodel_logging(btsid = ''):
    bts = _get_bts(btsid)
    if bts.infomodel:
        bts.infomodel.start_infomodel_logger(alias = bts.im_alias)

def stop_infomodel_logging(btsid = ''):
    bts = _get_bts(btsid)
    if bts.infomodel:
        bts.infomodel.save_infomodel_log(case_file('infomodel_%s_%s' % (bts.bts_id, time.strftime("%Y_%m_%d__%H_%M_%S"))), alias = bts.im_alias)

def get_infomodal_cell_string(btsid = ''):
    bts = _get_bts(btsid)
    if bts.infomodel:
        cell_count = bts.infomodel.query_infomodel('get count /MRBTS-1/RAT-1/BTS_L-1/LNBTS-1/LCELL-* is', alias = bts.im_alias)
        if int(cell_count) == 0:
            return '/MRBTS-1/RAT-1/MCTRL-*/BBTOP_M-1/MRBTS_M-1/LNBTS_M-1/CELL_M-*'
        else:
            return '/MRBTS-1/RAT-1/BTS_L-1/LNBTS-1/LCELL-*'
    else:
        raise Exception, 'Infomodel of BTS does not exist'


def bts_is_onair_by_infomodel(btsid = ''):
    bts = _get_bts(btsid)
    if bts.infomodel:
        cellinfos = bts.infomodel.query_infomodel('get list %s' %(bts.cellstr), alias=bts.im_alias, timeout = 10)
        states = [x['stateInfo']['proceduralState'].upper() for x in cellinfos]
        states = [x for x in states if x == 'ONAIRDONE']
        cellnames = [x['dist_name'].split('/')[-1] for x in cellinfos]
        cellnames = list(set(cellnames))
        for cellinfo in cellinfos:
            gv.logger.info('%s-----State: %s' %(cellinfo['dist_name'], cellinfo['stateInfo']['proceduralState']))
        gv.logger.info(cellnames)
        # if len(cellinfos) >0 and len(states) <> len(cellinfos):
        if len(cellinfos) >0 and len(states) <> len(cellnames):
            raise Exception, 'Not All cell are on air.'


def pet_get_cell_count_by_infomodel(btsid = ''):
    bts = _get_bts(btsid)
    if bts.infomodel:
        cellstr = get_infomodal_cell_string(bts.bts_id)
        bts.cell_count = len(bts.infomodel.query_infomodel('get list %s is [deployment=NotUsed]' % (cellstr), alias = bts.im_alias, timeout = 1))

def pet_bts_cells_should_be_ok():
    pass

def forcely_recovery_all_bts():
    for bts in [x for x in gv.allbts if x.used]:
        kw('forcely_recovery_bts_if_needed', bts.bts_id)

def pet_restart_bts(btsid = '', force = False):
    if gv.env.use_single_oam and gv.ute_admin_available:
        kw('wait_until_fct_is_not_reachable')
        return 0

    bts = _get_bts(btsid)
    if bts and bts.used:
        if not gv.env.restart_bts_for_each_case:
            if not gv.suite.health and not bts.need_change_scf:
                kw('report_error', 'Suite is not health.')
            if not bts.need_change_scf:
                return 0
        gv.logger.info('Reboot BTS: ' + bts.bts_id)
        reboot_succeed = False
        if not force:
            if gv.env.use_single_oam and gv.ute_admin_available:
                gv.logger.info('Use Single OAM to activate download plan')
                reboot_succeed = kw('pet_bts_activate_plan', bts.bts_id)
            else:
                reboot_succeed = kw('reboot_bts', bts.bts_id)
        if not reboot_succeed:
            gv.logger.error('Reboot failed, try to power off BTS.....')
            kw('power_control_for_facom', 'OFF', bts.bts_powerbreak_port)
            kw('sleep', '5s')
            kw('power_control_for_facom', 'ON', bts.bts_powerbreak_port)


def restart_bts_if_needed():
    write_to_console('\nApply new SCF and restart eNB...')
    _restart_bts(gv.master_bts)


def start_to_monitor_btslog_for_all_bts():
    for bts in [x for x in gv.allbts if x.used]:
        kw('start_to_monitor_btslog', bts.bts_id)

def start_to_monitor_infomodel_for_all_bts():
    for bts in [x for x in gv.allbts if x.used]:
        kw('start_to_monitor_infomodel', bts.bts_id)

def wait_until_all_bts_are_ready(check_mode = 'ALL'):
    gv.suite.health = False
    bts = gv.master_bts
    need_restart = True if gv.env.restart_bts_for_each_case else bts.need_change_scf
    need_slave_bts = gv.slave_bts <> None and gv.slave_bts.used
    if need_restart:
        for bts in gv.allbts:
            kw('start_to_monitor_btslog', bts.btsid)
        if gv.env.use_single_oam and gv.ute_admin_available:
            kw('sleep', '60')
        for bts in gv.allbts:
            kw('wait_until_fct_is_reachable', bts.btsid)
            kw('start_to_care_btslog', bts.bts_id)
            kw('pet_prepare_infomodel', bts.bts_id)

        for bts in gv.allbts:
            kw('wait_until_bts_is_onair_by_infomodel', bts.btsid, '10mins', '5')
            kw('wait_until_bts_is_onair_by_btslog',    bts.btsid, '10mins', '5')
            if gv.env.use_infomodel:
                kw('start_to_monitor_infomodel', bts.btsid)
            kw('stop_to_care_btslog', bts.btsid)
            bts.conn_bts = None
    else:
        for bts in gv.allbts:
            kw('start_to_monitor_btslog', bts.btsid)
            kw('pet_prepare_infomodel', bts.btsid)
            kw('start_to_monitor_infomodel', bts.btsid)
            bts.conn_bts = None
    gv.suite.health = True

def wait_until_bts_is_onair_by_infomodel(btsid, timeout, interval):
    if not gv.env.use_infomodel:
        return 0
    from robot.utils import timestr_to_secs
    timeout = timestr_to_secs(timeout)
    interval = timestr_to_secs(interval)
    start_time = time.time()
    bts = _get_bts(btsid)
    bts.cellstr = get_infomodal_cell_string(bts.bts_id)
    gv.logger.info('Cell Sting: ' + bts.cellstr)
    while time.time() < start_time + timeout:
        # try_to_recovery_fct(btsid)
        check_btslog_fatal()
        try:
            kw('bts_is_onair_by_infomodel', btsid)
            return 0
        except:
            time.sleep(interval)
    kw('report_error', 'BTS is not onAir by checking Infomodel')

def try_to_recovery_fct(btsid=''):
    if not pet_fct_is_reachable(btsid):
        kw('run_keyword_and_ignore_error', 'pet_disable_ethernet_port_security', btsid)

def wait_until_bts_is_onair_by_btslog(btsid, timeout, interval):
    from robot.utils import timestr_to_secs
    timeout = timestr_to_secs(timeout)
    interval = timestr_to_secs(interval)
    start_time = time.time()
    while time.time() < start_time + timeout:
        # try_to_recovery_fct(btsid)
        check_btslog_fatal()
        try:
            kw('btslog_contain_onair_flag', btsid)
            return 0
        except:
            time.sleep(interval)
    kw('report_error', 'BTS is not onAir by checking btslog')

def pet_enable_ethernet_port_security():
    pass

def pet_disable_ethernet_port_security(btsid = ''):
    bts = _get_bts(btsid)
    connect_to_bts_control_pc(btsid)
    kw('pet_stop_site_manager')
    execute_command_on_bts_control_pc_without_check(btsid, 'cd ' + to_winpath(bts.nms_tool_path))
    exe_path = r'changesecurity.bat -disable -ne %s -pw Nemuadmin:nemuuser' % (bts.bts_ftm_ip)
    execute_command_on_bts_control_pc_without_check(btsid, exe_path)

def pet_prepare_config_file_for_bts(btsid):
    #upload swconfig file to bts
    bts = _get_bts(btsid)
    if not bts.used:
        return 0

    try:
        back_original_config(btsid, pv('OUTPUT_DIR'))
    except:
        pass

    case = gv.case.curr_case
    from pet_scf_manager import pet_scf_manager
    scf_manager = pet_scf_manager(case, bts)

    changes = [] if gv.case.curr_case.fixed_scf else scf_manager.gene_change_list()
    accept_changes = [x for x in changes if not 'delete' in x]

    if bts.level == 'P': #Master 2 BTS
        src_xml_file = bts_file(btsid, gv.case.curr_case.scf_file)
    else:
        src_xml_file = bts_file(btsid, gv.case.curr_case.ms_scf_file)

    scf_index = '%s_%s' %(btsid, os.path.basename(src_xml_file))
    if scf_index in gv.env.scf_changing:
        last_changing = gv.env.scf_changing[scf_index]
    else:
        last_changing = []

    bts.need_change_scf = last_changing <> changes
    bts.need_change_scf = True if gv.case.curr_case.fixed_scf else bts.need_change_scf

    for change in [x for x in changes if 'delete' in x]:
        try:
            common_xml_operation(pathc(src_xml_file), case_file('dest_scf'), [change])
            accept_changes.append(change)
        except:
            gv.logger.info('Process  [%s] error' % (change))

    directory_path = '/ffs/run' if bts.airscale else '/flash'
    download_file_from_bts(btsid, pathc(bts_file(btsid, 'FileDirectory.xml')), 'FileDirectory.xml', directory_path)
    from lxml import etree
    try:
        scf_version = 'SCFC' + etree.parse(bts_file(btsid, 'FileDirectory.xml')).xpath('//fileElement[@name="SCFC"and@activeFlag="TRUE"]')[0].get('version')
    except:
        scf_version = 'SCFC_100.xml'
    gv.logger.info('Myself found scf: ' + scf_version)

    #upload scf file with the new name get from FileDirectory.xml
    gv.logger.info('Real Change:')
    gv.logger.info(src_xml_file)
    common_xml_operation(pathc(src_xml_file), pathc(bts_file(btsid, scf_version)), accept_changes)

    if not bts.need_change_scf:
        gv.logger.info('SCF Changing for BTS: [%s] is same, not need to upload SCF file again.' %(btsid))
        return 0
    gv.env.scf_changing[scf_index] = changes

    bts.scf_filename = bts_file(btsid, scf_version)
    if not gv.env.use_single_oam:
        gv.logger.info('Upload SCF file to BTS')
        upload_file_to_bts(btsid, pathc(bts_file(btsid, scf_version)), scf_version, directory_path + '/config')
    else:
        gv.logger.info('Use singal OAM to commission')
        pet_bts_full_commission_prepare(btsid)
        pet_bts_download_plan(btsid)
        if not gv.ute_admin_available:
            gv.logger.info('Upload SCF file to BTS because uteadmin is not avaliable')
            upload_file_to_bts(btsid, pathc(bts_file(btsid, scf_version)), scf_version, directory_path + '/config')

    scf_manager.generate_swconfig_file(bts, gv.case.curr_case)
    upload_file_to_bts(btsid, pathc(bts_file(btsid, 'swconfig_new.txt')), 'swconfig.txt', '/ffs/run')


    # vp_filename = bts_source_file(btsid, 'vp.txt')
    # if os.path.exists(vp_filename):
    #     params = open(bts_source_file(btsid, 'vp.txt')).readlines()
    #     params = [x.replace('\n', '') for x in params if x.replace('\n', '').strip()]
    #     remote_vender_path = '/ffs/run/swpool/OAM/' if bts.airscale else '/flash'
    #     vendor_version = etree.parse(bts_file(btsid, 'FileDirectory.xml')).xpath('//fileElement[@name="vendor"and@activeFlag="TRUE"]')[0].get('version')



    # vendor_version = etree.parse(bts_file(btsid, 'FileDirectory.xml')).xpath('//fileElement[@name="vendor"and@activeFlag="TRUE"]')[0].get('version')
    # # vendor_version = get_vendor_version(bts_file(btsid, 'FileDirectory.xml'))
    # params = open(bts_source_file(btsid, 'vp.txt')).readlines()
    # params = [x.replace('\n', '') for x in params if x.replace('\n', '').strip()]
    # if params:
    #     pass
    #     change_xml_file(pathc(bts_source_file(btsid, 'vendor.xml')), pathc(bts_file(btsid, vendor_version)), params)

    #     #upload vendor file with the new name get from FileDirectory.xml and then generate the key file for it.
    #     upload_file_to_bts(btsid, pathc(bts_file(btsid, vendor_version)), vendor_version, directory_path)
    #     kw('execute_command_on_bts', btsid, ['crasign %s/%s' % (directory_path, vendor_version),
    #                                   'craverify %s/%s %s/%s.p7' % (directory_path,vendor_version, directory_path, vendor_version)])

def back_original_config(btsid, workdire = ''):
    import os
    gv.logger.info('Backup BTS config files to [%s]' %(workdire))
    def __downpath(filename):
        return os.sep.join([workdire, filename])
    if workdire:
        gv.logger.info('Begin to backup')
        bts = _get_bts(btsid)
        directory_path = '/ffs/run' if bts.airscale else '/flash'
        download_file_from_bts(btsid, __downpath('FileDirectory.xml'), 'FileDirectory.xml', directory_path)
        from lxml import etree
        rscf_filename = 'SCFC' + etree.parse(__downpath('FileDirectory.xml')).xpath('//fileElement[@name="SCFC"and@activeFlag="TRUE"]')[0].get('version')
        lscf_filename = __downpath('Backup_%s_%s' %(btsid, rscf_filename))
        lswconfig = __downpath('backup_%s_swconfig.txt' %(btsid))
        import os
        if not os.path.exists(lscf_filename):
            download_file_from_bts(btsid, lscf_filename, rscf_filename, directory_path + '/config')
        if not os.path.exists(lswconfig):
            download_file_from_bts(btsid, lswconfig, 'swconfig.txt', '/ffs/run')


def apply_bts_config_according_to_scenario_id():
    if gv.debug_mode <> 'DEBUG':   #in debug mode, bts and TM500 will not restarted
        for bts in gv.allbts:
            kw('pet_prepare_config_file_for_bts', bts.bts_id)
        kw('restart_all_device_wait_until_they_are_ready')
    kw('pet_get_bts_version')

def try_to_enable_ssh(btsid):
    bts = _get_bts(btsid)
    if not kw('ssh_is_enable', bts.bts_ip, '22', bts.bts_fcm_username, bts.bts_fcm_password):
        output = pet_enable_ssh(bts.bts_control_pc_lab, bts.bts_ftm_username, bts.bts_ftm_password)
        if not 'SSH Service Enabled Successfully' in output:
            kw('report_error', 'Enable SSH of BTS failed, please check it first.')

def read_bts_config(btsid = '', role='M', level='P'):
    def _get_a_bts(cbts, fieldname, role):
        fname = str(getattr(cbts, fieldname))
        if fname and fname <> 'NULL':
            sbts = read_bts_config(fname)
            sbts.role = role
            reorganize_bts_config(sbts)
            cbts.btslist.append(sbts)

    from pet_db import get_table_content
    # cbtslist = get_table_content('tblcbts')
    # cbts = [bts for bts in cbtslist if bts.btsid == btsid]
    # if cbts:
    #     gv.logger.info('This is a combined BTS!!!')
    #     cbts = cbts[0]
    #     cbts.btsmode = 'C'
    #     cbts.btslist = []
    #     _get_a_bts(cbts, 'sbts1_id', 'p')
    #     _get_a_bts(cbts, 'sbts2_id', 's')
    #     _get_a_bts(cbts, 'sbts3_id', 't')
    #     return cbts
    # else:
    btslist = get_table_content('tblbts')
    bts = [x for x in btslist if x.btsid == btsid]
    if not bts:
        kw('report_error', 'Could not find bts config from DB: [BTS%s]' %(btsid))
    bts = bts[0]
    bts.role = role
    bts.level = level
    reorganize_bts_config(bts)
    gv.allbts.append(bts)
    return bts

def reorganize_bts_config(bts):
    bts.bts_id = bts.btsid
    bts.workcell = 1
    bts.airscale = True if bts.airscale == '1' else False
    bts.bts_fcm_ip, bts.bts_fcm_username, bts.bts_fcm_password = '192.168.255.1','toor4nsn','oZPS0POrRieRtu'
    bts.bts_ftm_ip, bts.bts_ftm_username, bts.bts_ftm_password = '192.168.255.129','Nemuadmin','nemuuser'
    bts.mr_paging_ioc, bts.mr_paging_impair_ioc         = '140', '84'
    bts.mr_call_drop_ioc, bts.mr_call_drop_impair_ioc   = '140', '84'
    bts.mr_ho_ioc, bts.mr_ho_impair_ioc                 = '140', '89'
    bts.mr_volte_ioc, bts.mr_volte_impair_ioc           = '140', '84'
    bts.conn_bts = None
    bts.conn_pc = None
    bts.config_id = ''
    bts.cell_count = 0
    bts.used = True
    bts.lock_btslog = threading.Lock()
    bts.infomodel_pid = []
    bts.new_earfcn_list = []
    bts.new_eutraCarrierInfo_list = []
    bts.pcap_interface =  r'\Device\NPF_' + bts.pcap_interface.upper().split('NPF_')[-1]
    bts.scf_filename = ''
    bts.infomodel = None
    bts.ute_admin = None
    bts.error_log_list = []
    bts.monitor_error_log = False
    bts.btslog_buffer = []
    bts.tti = IpaMmlItem()
    bts.btsmode = 'S'
    if bts.airscale:
        bts.fspip = '192.168.253.20'
    else:
        bts.fspip = '192.168.253.18'

def prepare_bts_environment(btslist):
    for bts in btslist:
        bts.directory = os.sep.join([gv.suite.log_directory, 'BTS%s' %(bts.btsid)])
        os.makedirs(bts.directory)
        kw('run_keyword_and_ignore_error', 'config_bts_control_pc', bts.btsid)
        kw('bts_cpc_pre_check', bts.btsid)
        kw('makesure_passport_is_running', bts.conn_pc)
        # kw('forcely_recovery_bts_if_needed', bts.btsid)
        if bts.btsid == gv.master_bts.btsid:
            kw('try_to_switchback_active_version', bts.btsid)
        # bts.btsversion = kw('pet_get_bts_sw_version', bts.btsid)

def start_btslog_pcap_server_if_needed(btsid = ''):
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
    kw('wait_until_port_is_listening', '30003', '40')
    execute_command_on_bts_control_pc_without_check(btsid, 'netstat -nao|grep 30003')

def btslog_monitor_thread(btsid):
    bts = _get_bts(btsid)
    buf = ''
    fatal_str = ''
    filename = case_file('btslog_%s_%s.log' % (btsid, time.strftime("%d__%H_%M_%S")))
    max_size = 8192

    import datetime
    import select

    if gv.case.done:
        return 0
    if bts.conn_btslog:
        bts.conn_btslog.setblocking(0)
    else:
        return 0
    fatal_time = 0
    found_fatal = False
    while True:
        now = datetime.datetime.now()
        ret = ''
        if bts.conn_btslog:
            try:
                ready = select.select([bts.conn_btslog], [], [], 900)
            except:
                return 0

            if ready[0] and bts.conn_btslog:
                ret = bts.conn_btslog.recv(max_size)

            if ret:
                buf += ret
                if len(ret) == max_size:
                    recvdata = buf.splitlines()[:-1]
                    buf = buf.splitlines()[-1]
                else:
                    recvdata = buf.splitlines()
                    buf = ''
                recvdata = [line.strip().replace(chr(0), '') for line in recvdata if line.strip()]
                if os.path.exists(filename):
                    if os.path.getsize(filename) >= 1024*1024*100:
                        import zipfile
                        z = zipfile.ZipFile(filename.replace('.log', '_t.zip'), 'w')
                        z.write(filename, os.path.basename(filename), zipfile.ZIP_DEFLATED)
                        os.remove(filename)
                        z.close()
                        filename = case_file('btslog_%s_%s.log' % (btsid, time.strftime("%d__%H_%M_%S")))
                with open(filename, 'a') as f:
                    for line in recvdata:
                        if line.strip():
                            f.write('[%s]  %s\n' % (now.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3], line))

                if bts.care_btslog:
                    bts.btslog_buffer += recvdata

                if bts.monitor_error_log:
                    if hasattr(bts, 'bts_error_log_keywords'):
                        for alog in recvdata:
                            for keyword in bts.bts_error_log_keywords:
                                if keyword.upper() in alog.upper():
                                    bts.error_log_list.append('[%s]  %s' % (now.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3], alog))
                                    break

                if 'fatal'.upper() in ret.upper()  and\
                     not 'Nonfatal'.upper() in ret.upper() and\
                     not 'Non fatal'.upper() in ret.upper() and\
                     not 'EAaErrorFatality_NonFatal'.upper() in ret.upper() and\
                     not 'FaultAddress'.upper() in ret.upper() and\
                     not 'fatalfaultaddress'.upper() in ret.upper() and\
                     not 'fatalfaul'.upper() in ret.upper() and\
                     not 'fatalfaulta'.upper() in ret.upper() and\
                     not 'EFaultId_ExternallyTriggeredDspFatalErrAl'.upper() in ret.upper():
                    # kw('log', 'Found fatal')
                    # kw('log',  ret)
                    fatal_str = ret
                    fatal_time = time.time()
                    found_fatal = True
                    gv.env.save_snapshot = True

                if found_fatal:
                    if time.time() - fatal_time > 10:
                        # kw('log', ret)
                        gv.suite.health = False
                        gv.case.monitor_error_msg = 'Fatal found in BTSlog: [%s]  [%s]. ' % (btsid, str(fatal_str))
                        return 0
        else:
            return 0

def start_to_monitor_btslog(btsid = ''):
    bts = _get_bts(btsid)
    connect_to_bts_control_pc(btsid)
    kw('start_btslog_pcap_server_if_needed', btsid)
    bts.conn_btslog = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    bts.conn_btslog.connect((bts.bts_control_pc_lab, 30003))
    bts.care_btslog = False
    start_new_thread(btslog_monitor_thread , (btsid,))

def stop_to_monitor_btslog(btsid = ''):
    for bts in gv.allbts:
        if bts.conn_btslog:
            with bts.lock_btslog:
                bts.conn_btslog.close()
                bts.conn_btslog = None
        btsid = bts.bts_id
        import zipfile
        for btslog in [filename for filename in os.listdir(case_file('')) if 'btslog_%s_' %(btsid) in filename and '.log' in filename]:
            zipfilename = case_file(btslog.replace('.log', '.zip'))
            z = zipfile.ZipFile(zipfilename, 'w')
            z.write(case_file(btslog), os.path.basename(btslog), zipfile.ZIP_DEFLATED)
            os.remove(case_file(btslog))
            z.close()

def start_to_care_btslog(btsid = ''):
    bts = _get_bts(btsid)
    with bts.lock_btslog:
        bts.btslog_buffer = []
    bts.care_btslog = True

def stop_to_care_btslog(btsid = ''):
    bts = _get_bts(btsid)
    bts.care_btslog = False

def stop_to_care_btslog_and_saveit(btsid = ''):
    bts = _get_bts(btsid)
    stop_to_care_btslog(btsid)
    with open(case_file('btslog2.log'), 'w') as f:
        for line in bts.btslog_buffer:
            f.write(line + '\n')

def infomodel_monitor_thread(btsid = ''):
    pet_bts_alarm_path = {
        'RL55' : ['/MRBTS-*/RAT-*/LNBTS-*/ALARM_L-*', '/MRBTS-*/RAT-*/LNBTS-*/LNCEL-*/ALARM_L-*'],
        'RL65' : ['/MRBTS-*/RAT-*/BTS_L-*/LNBTS-*/ALARM_L-*', '/MRBTS-*/RAT-*/BTS_L-*/LNBTS-*/LNCEL-*/ALARM_L-*'],
        'TL16' : ['/MRBTS-*/RAT-*/BTS_L-*/LNBTS-*/ALARM_L-*', '/MRBTS-*/RAT-*/BTS_L-*/LNBTS-*/LNCEL-*/ALARM_L-*'],
        'TL16A': ['/MRBTS-*/RAT-*/BTS_L-*/LNBTS-*/ALARM_L-*', '/MRBTS-*/RAT-*/BTS_L-*/LNBTS-*/LNCEL-*/ALARM_L-*'],
        'TL17' : ['/MRBTS-*/RAT-*/BTS_L-*/LNBTS-*/ALARM_L-*', '/MRBTS-*/RAT-*/BTS_L-*/LNBTS-*/LNCEL-*/ALARM_L-*'],
        'TRUNK' : ['/MRBTS-*/RAT-*/BTS_L-*/LNBTS-*/ALARM_L-*', '/MRBTS-*/RAT-*/BTS_L-*/LNBTS-*/LNCEL-*/ALARM_L-*'],
    }
    bts = _get_bts(btsid)
    cellstr = get_infomodal_cell_string(bts.bts_id)
    if not bts.infomodel:
        return 0
    bts.cell_count = len(bts.infomodel.query_infomodel('get list %s' % (cellstr), alias = bts.im_alias, timeout = 10))

    while True:
        if not gv:
            return 0
        if gv.case.done:
            return 0
        if gv.case.start_testing:
            for i in range(bts.cell_count):
                if bts.sw_release == 'RL55':
                    cellstr = '/MRBTS-1/RAT-1/BBTOP_L-1/LCELL-%d' % (i + 1)
                else:
                    cellstr = '/MRBTS-1/RAT-1/BTS_L-1/BBTOP_L-1/LCELL-%d' % (i + 1)

                mo = None
                if bts.infomodel:
                    try:
                        mo = bts.infomodel.get_infomodel_object(cellstr, timeout = 5, alias = bts.im_alias)
                        state = mo['stateInfo']['proceduralState']
                        record_monitor_info('Cell%d status:  %s' % (i + 1, state))
                    except:
                        pass

                    error_msg = ''
                    if mo <> None:
                        if state.upper().strip() <> 'onAirDone'.upper():
                            error_msg = 'CELL %d is not onAir, it is: %s.' % (i + 1, state)

                    if error_msg <> '':
                        gv.suite.health = False
                        gv.case.monitor_error_msg = error_msg
                        record_monitor_info('Quit when error happened')
                        return 0

            # alarm_list = []
            # alarm_path = pet_bts_alarm_path[bts.sw_release]
            # alarms = []
            # for path in alarm_path:
            #     try:
            #         if bts.infomodel:
            #             alarms = bts.infomodel.query_infomodel('get list ' + path, timeout = 1, alias = bts.im_alias)
            #     except:
            #         alarms = []
            #     alarm_list += alarms
            # alarminfo = [(x.alarmInformation.alarmText.alarmDetailNbr,
            #               x.alarmInformation.alarmText.faultDescription) for x in alarm_list]
            # if alarminfo:
            #     for alarm in alarminfo:
            #         record_monitor_info('Found Alarm:  %s' % (str(alarm)))
            # else:
            #     record_monitor_info('No Alarm found.')
        time.sleep(3)

def start_to_monitor_infomodel(btsid = ''):
    bts = _get_bts(btsid)
    if bts.infomodel:
        start_new_thread(infomodel_monitor_thread , (btsid,))

def stop_to_monitor_infomodel(btsid = ''):
    bts = _get_bts(btsid)
    kw('finish_infomodel', bts.bts_id)

def try_to_switchback_active_version(btsid = ''):
    ver = pet_get_bts_sw_version(btsid)
    if gv.env.bts_version == '' or gv.env.bts_version == ver.upper().strip():
        gv.env.bts_version = ver
        return 0
    else:
        output = kw('execute_command_on_bts', btsid, 'uboot_env get|grep active_partition')
        for line in output.splitlines():
            if 'active_partition=' in line:
                partion = line.split('=')[1]
                np = '1' if partion == '2' else '2'
                kw('execute_command_on_bts', btsid, 'uboot_env set active_partition=%s' % (np))
                kw('reboot_bts', btsid)
                kw('wait_until_fct_is_reachable', btsid)
                break

def bts_control_pc_conn_is_available(btsid = ''):
    bts = _get_bts(btsid)
    output = os.popen('netstat -na|grep %s' % (bts.bts_control_pc_lab)).read()
    return 'ESTABLISHED' in output

def get_pmcount_time(btsid = '', mode = 'start'):
    output = kw('execute_simple_command_on_bts', btsid, 'date +"%Y-%m-%d-%k-%M"')
    year, month, day, hour, minute = [int(x.strip()) for x in output[0].split('-')]
    import datetime
    d = datetime.datetime(year, month, day, hour, minute, 0)
    return '%0.4d%0.2d%0.2d_%0.2d%0.2d00' % (d.year, d.month, d.day, d.hour, d.minute)

def cleanup_unused_hashfile():
    for bts in [x for x in gv.allbts if x.used]:
        kw('run_keyword_and_ignore_error', 'execute_simple_command_on_bts', bts.bts_id, 'rm -rf /flash/Hash*')

def pet_enable_ssh(host, username, password):
    import urllib, urllib2, base64
    auth_key = base64.encodestring('%s:%s' % (username, password))[:-1]
    query_args = { 'Username': username,
                   'Password': password,
                   'Validate1':'Validate2',
                   'EncodedCreds':auth_key}

    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
    new_auth = gv.master_bts.sw_release in ['TL16A', 'TL17', 'TRUNK', 'TL17SP', 'TL17A']

    if new_auth:
        url_login = 'https://%s/protected/login.cgi' %host
        print url_login
        loginpage = opener.open(url_login, urllib.urlencode(query_args)).read()
        gv.logger.info(loginpage)

    request = urllib2.Request('https://%s/protected/sshservice.html' %host)
    if not new_auth:
        request.add_header('Authorization', 'Basic %s' % auth_key)
    sshpage = opener.open(request).read()
    gv.logger.info(sshpage)
    stamp = [line for line in sshpage.splitlines() if "name=stamp" in line][0].split('"')[1]
    token = [line for line in sshpage.splitlines() if "name=token" in line][0].split('"')[1]

    request = urllib2.Request('https://%s/protected/enableSsh.cgi?stamp=%s&token=%s&frame=sshservice' %(host, stamp, token))
    if not new_auth:
        request.add_header('Authorization', 'Basic %s' % auth_key)
    enablepage = opener.open(request).read()
    gv.logger.info(enablepage)
    return enablepage

def download_bts_pmcount_file(btsid = ''):
    bts = _get_bts(btsid)
    cmd = 'sshpass -p %s scp -v %s@%s:/ram/PM*.xz  %s' %(bts.bts_fcm_password, bts.bts_fcm_username,
        bts.bts_ip, case_file('counter'))
    run_local_command_gracely(cmd)

def download_bts_cpuload_file(btsid = ''):
    bts = _get_bts(btsid)
    cmd = 'sshpass -p %s scp %s@%s:/var/tmp/aasysinfo/runtime/SystemCpu*  %s' %(bts.bts_fcm_password, bts.bts_fcm_username,
        bts.bts_ip, case_file('loadfile'))
    run_local_command_gracely(cmd)

def cleanup_pmcount_file(btsid):
    execute_simple_command_on_bts(btsid, 'rm -rf /ram/PM*.xz')

def cleanup_load_file(btsid):
    execute_simple_command_on_bts(btsid, 'rm -rf /var/tmp/aasysinfo/runtime/SystemCpu*.xz')

def cleanup_work_for_bts(btsid):
    cleanup_pmcount_file(btsid)
    cleanup_load_file(btsid)

def wait_until_new_pmcount_file_generated(btsid=''):
    if gv.case.curr_case.use_kpi_counter:
        start_time = time.time()
        total_time = 30*60
        output1 = execute_simple_command_on_bts(btsid, 'ls -la /ram/PM*.xz')
        while time.time() < start_time + total_time:
            output2 = execute_simple_command_on_bts(btsid, 'ls -la /ram/PM*.xz')
            if len(output2) <> len(output1):
                gv.logger.info('Found New PM Counter file generated!')
                return 0
            else:
                gv.logger.info('Have not found new PM counter file, left: [%d]s go on checking....' %(int(start_time + total_time-time.time())))
            time.sleep(60)
        kw('report_error', 'Failed to found new PM counter file')

def is_master_bts(btsid):
    return btsid == gv.master_bts.btsid

def is_slave_bts(btsid):
    if gv.slave_bts:
        if gv.slave_bts.used:
            if btsid == gv.slave_bts.btsid:
                return True
    return False

def read_all_scf_config(phase):
    bts = gv.master_bts
    for sbts in gv.mbts():
        src_xml_file = bts_file(sbts.btsid, gv.case.curr_case.scf_file) if phase == 'BEFORE' else sbts.scf_filename
        src_xml_file = bts_file(sbts.btsid, gv.case.curr_case.ms_scf_file) if sbts.level == 'S' else src_xml_file
        pet_bts_read_scf_file(sbts.btsid, src_xml_file)

    for sbts in gv.sbts():
        filename = gv.case.curr_case.slave_scf_file if gv.case.curr_case.slave_scf_file.strip() else gv.case.curr_case.scf_file
        src_xml_file = bts_file(sbts.btsid, filename) if phase == 'BEFORE' else sbts.scf_filename
        pet_bts_read_scf_file(sbts.btsid, src_xml_file)

def pet_bts_read_scf_file_for_fdd(btsid = '', scf_file = ''):
    bts = _get_bts(btsid)
    filename = bts_source_file(bts.bts_id, gv.case.curr_case.scf_file) if scf_file.strip() == '' else scf_file
    gv.logger.debug(filename)

    bts.scftree =  etree.parse(filename)
    get_classnamelist(bts)
    cells = get_mos(bts, 'LNCEL_FDD')
    cellnames = get_mos_distname(bts, 'LNCEL_FDD')
    cellnames.sort()
    ncells = []
    for cellname in cellnames:
        ncells.append([cell for cell in cells if cell.get('distName') == cellname][0])
    cells = ncells[:]

    bts.antls = get_mos_distname(bts, 'ANTL')
    idlist = [int(x.split('-')[-1]) for x in bts.antls]
    idlist.sort()
    bts.antls = ['-'.join(bts.antls[0].split('-')[:-1]) + '-' + str(x) for x in idlist]
    bts.lcells = get_mos(bts, 'LCELL')

    bts.lncels = cellnames
    bts.cell_count = len(bts.lncels)

    bts.internal_cellid_list = [x.split('/')[-1].split('-')[-1] for x in bts.lncels]
    gv.logger.info(bts.internal_cellid_list)
    pass

def pet_bts_read_scf_file(bts_id = '', scf_file = ''):
    bts = _get_bts(bts_id)
    filename = bts_source_file(bts.bts_id, gv.case.curr_case.scf_file) if scf_file.strip() == '' else scf_file
    gv.logger.debug(filename)

    bts.scftree =  etree.parse(filename)
    get_classnamelist(bts)

    #Process LNCEL, it is very important
    cells = get_mos(bts, 'LNCEL')
    cellnames = get_mos_distname(bts, 'LNCEL')
    cellnames.sort()
    ncells = []
    for cellname in cellnames:
        ncells.append([cell for cell in cells if cell.get('distName') == cellname][0])
    cells = ncells[:]

    bts.lncels = cellnames
    bts.cell_count = len(bts.lncels)

    bts.internal_cellid_list = [x.split('/')[-1].split('-')[-1] for x in bts.lncels]

    bts.phycellid_list = [get_parameter_under_node(cell, 'phyCellId')[0].text for cell in cells]
    bts.earfcn_list = []
    if bts.btstype == 'TDD':
        bts.earfcn_list = [node.text for node in get_parameters(bts, 'earfcn')]

    print 'XXXXXXXXXx', bts.earfcn_list

    bts.allcells = get_mos(bts, 'LNCEL_TDD') if bts.btstype == 'TDD' else get_mos(bts, 'LNCEL_FDD')
    if len(bts.allcells) ==0:
        bts.allcells = get_mos(bts, 'LNCEL')
    if bts.btstype == 'FDD':
        for cell in bts.allcells:
            bts.earfcn_list.append(get_all_parameter_under_node(cell, 'earfcnDL')[0].text)
    print bts.earfcn_list


    bts.frequency_list = [earfcn_to_frequency(x) for x in bts.earfcn_list]
    bts.dl_frequency_pcell = bts.frequency_list[0]
    bts.dl_frequency_scell = bts.dl_frequency_pcell if bts.cell_count == 1 else bts.frequency_list[1]
    bts.dl_frequency_tcell = bts.frequency_list[2] if bts.cell_count == 3 else 0
    earfcn = bts.earfcn_list[0]
    gv.logger.debug(earfcn)
    bts.bandname = get_band_name(earfcn)
    gv.logger.debug('Band Name:  %s' %(bts.bandname))

    if has_attr(bts, 'bts_physical_ids'):
        bts.phycellid_list = bts.bts_physical_ids.replace(';', ',').split(',')

    bts.antls = get_mos_distname(bts, 'ANTL')
    idlist = [int(x.split('-')[-1]) for x in bts.antls]
    idlist.sort()
    bts.antls = ['-'.join(bts.antls[0].split('-')[:-1]) + '-' + str(x) for x in idlist]
    print bts.antls
    gv.logger.debug(bts.antls)

    bts.lcells = get_mos(bts, 'LCELL')
    bts.btsdistName = get_mos_distname(bts, 'LNBTS')[0]
    bts.tddcells = get_mos(bts, 'LNCEL_TDD')




earfcn_band = {

    '3':['1725', '1875'],
    '28':['9300', '9500'],
    '38':['37900', '38100'],
    '39':['38400', '38500'],
    '40':['38770', '38970', '39170'],
    '41':['40540', '40740', '40940'],
    '42':['42490', '42690', '42890'],
}

def get_new_earfcn(bts, cellid, index):
    earfcn = [node.text for node in get_parameters(bts, 'earfcn')][int(cellid)-1] if bts.btstype == 'TDD' else [node.text for node in get_parameters(bts, 'earfcndl')][int(cellid)-1]
    bandname = get_band_name(earfcn)
    return earfcn_band[str(bandname)][index-1]

def get_handover_cell():
    another_cell = 3 if gv.case.curr_case.ca_type == '2CC' else 2
    another_cell = 4 if gv.case.curr_case.ca_type == '3CC' else another_cell
    return another_cell

def prepare_earfcn_for_bts():
    case = gv.case.curr_case
    group_len = 2 if case.ca_type == '2CC' else 1
    group_len = 3 if case.ca_type == '3CC' else group_len
    reverse_f = [i + 1 for i in range(group_len)]
    if case.is_df:
        reverse_f = [2, 1] if group_len == 2 else [2]
        reverse_f = [2, 1, 3] if group_len == 3 else reverse_f

    values = [0] * gv.master_bts.cell_count * 2 if case.is_inter else [0] * gv.master_bts.cell_count
    for i in range(group_len):
        values[i] = i + 1
        j = i + group_len
        j = j + gv.master_bts.cell_count if case.is_inter else j
        values[j] = reverse_f[i]
    earfcn_name = 'earfcn' if gv.master_bts.btstype == 'TDD' else 'earfcnDL'
    earfcn_list = [node.text for node in get_parameters(gv.master_bts, '%s'%(earfcn_name))]
    print '######',earfcn_list,gv.master_bts.cell_count
    if case.is_inter:
        earfcn_list = earfcn_list + [node.text for node in get_parameters(gv.slave_bts, 'earfcn')]

    for i in range(gv.master_bts.cell_count):
        earfcn_list[i] = get_new_earfcn(gv.master_bts, i+1, values[i]) if values[i] <> 0 else earfcn_list[i]
        if case.is_inter:
            j = i + gv.master_bts.cell_count
            earfcn_list[j] = get_new_earfcn(gv.slave_bts, i+1, values[j]) if values[j] <> 0 else earfcn_list[j]
    gv.master_bts.new_earfcn_list = earfcn_list[:gv.master_bts.cell_count]
    print '#################',gv.master_bts.new_earfcn_list
    if case.is_inter:
        gv.slave_bts.new_earfcn_list = earfcn_list[gv.master_bts.cell_count:]

def prepare_eutraCarrierInfo():
    case = gv.case.curr_case
    op_bts = gv.master_bts if case.ho_type == 'INTRA' else gv.slave_bts
    another_cell = get_handover_cell()

    gv.master_bts.new_eutraCarrierInfo_list = [0] * gv.master_bts.cell_count
    if gv.slave_bts and gv.slave_bts.used:
        gv.slave_bts.new_eutraCarrierInfo_list = [0] * gv.slave_bts.cell_count

    gv.master_bts.new_eutraCarrierInfo_list[0] = op_bts.new_earfcn_list[another_cell-1]
    op_bts.new_eutraCarrierInfo_list[another_cell-1] = gv.master_bts.new_earfcn_list[0]

def prepare_tac_mme():
    case = gv.case.curr_case
    if case.has_mr_volte:
        if case.is_handover:
            gv.master_bts.work_tac = gv.master_bts.tac_volte
            gv.master_bts.work_mme = gv.master_bts.mme_ip_volte
            if case.is_inter:
                gv.slave_bts.work_tac = gv.master_bts.work_tac
                gv.slave_bts.work_mme = gv.master_bts.work_mme
        else:
            gv.master_bts.work_tac = gv.master_bts.tac_common
            gv.master_bts.work_mme = gv.master_bts.mme_ip
    else:
        gv.master_bts.work_tac = gv.master_bts.tac_common
        gv.master_bts.work_mme = gv.master_bts.mme_ip
        if case.is_handover:
            if case.is_inter:
                gv.slave_bts.work_tac = gv.master_bts.work_tac
                gv.slave_bts.work_mme = gv.master_bts.work_mme

def prepare_freqEutra():
    case = gv.case.curr_case
    if case.ho_type == 'INTER' and case.ho_path == 'S1':
        another_cell = get_handover_cell()
        if hasattr(gv.slave_bts, 'new_earfcn_list'):
            gv.master_bts.freqEutra_tstr = str(gv.slave_bts.new_earfcn_list[another_cell-1])
        if hasattr(gv.master_bts, 'new_earfcn_list'):
            gv.slave_bts.freqEutra_tstr = str(gv.master_bts.new_earfcn_list[0])


def prepare_mr_parameters():
    if not gv.case.curr_case.fixed_scf:
        if gv.case.curr_case.case_type == 'MIX_MR':
            if gv.case.curr_case.is_handover:
                prepare_earfcn_for_bts()
            if gv.case.curr_case.is_handover and gv.case.curr_case.is_df:
                prepare_eutraCarrierInfo()
            prepare_tac_mme()
            prepare_freqEutra()
            gv.logger.info(gv.master_bts.new_earfcn_list)
            gv.logger.info(gv.master_bts.new_eutraCarrierInfo_list)

def pet_bts_full_commission_prepare(btsid):
    bts = _get_bts(btsid)
    # from pet_xml import scfns
    # scftree =  etree.parse(bts.scf_filename)
    bts.planid = '3221225472'
    # bts.planid = scftree.xpath('//scfns:cmData', namespaces=scfns)[0].get('id')
    # mos = scftree.xpath('//scfns:managedObject[contains(@class,"MRBTS")]', namespaces=scfns)
    # if mos:
    #     if not mos[0].xpath('.//scfns:extension',  namespaces=scfns): #not has the extension node, need add
    #         gv.logger.info('extension node does not exist, TA will add the node')
    #         extension_node = etree.SubElement(mos[0], "extension", name="BTSExtensions")
    #         etree.SubElement(extension_node, "p", name="scope").text = "full"
    #         scftree.write(bts.scf_filename)

def pet_clear_proxy_env():
    for key in ['http_proxy', 'https_proxy']:
        if key in os.environ.keys():
            del os.environ[key]

def pet_ute_admin_setup(btsid):
    bts = _get_bts(btsid)
    pet_clear_proxy_env()
    from ute_admin import ute_admin
    bts.ute_admin = ute_admin()
    bts.ute_admin_alias = btsid + time.strftime("_%Y_%m_%d__%H_%M_%S")
    try:
        bts.ute_admin.setup_admin(bts_host = bts.bts_control_pc_lab, alias=bts.ute_admin_alias,
                                    bts_port=9002, use_ssl=False, timeout=90)
        gv.ute_admin_available = True
    except:
        traceback.print_exc()
        gv.logger.info('Setup Single OAM Failed.')
        gv.ute_admin_available = False

def pet_ute_admin_teardown(btsid):
    bts = _get_bts(btsid)
    if bts.ute_admin:
        bts.ute_admin.teardown_admin(alias=bts.ute_admin_alias)
        bts.ute_admin = None

def pet_bts_download_plan(btsid):
    bts = _get_bts(btsid)
    if not bts.ute_admin:
        pet_ute_admin_setup(btsid)
    if gv.ute_admin_available:
        try:
            # with open(bts.scf_filename, "rb") as scf:
            #     scf_bytes = list(bytearray(scf.read()))
            # bts.ute_admin.store.get(bts.ute_admin_alias).api.execute_procedure("downloadPlan", {"planId": bts.planid, "btsId": btsid, "scf": scf_bytes}, 60)
            bts.ute_admin.perform_commissioning(plan_id='3221225472', bts_id=btsid, scf_file=bts.scf_filename,
                                                timeout=300,
                                                skip_parameter_relation_errors=True,
                                                should_activate=True,
                                                alias  =  bts.ute_admin_alias)
        finally:
            pass

def pet_bts_activate_plan(btsid):
    bts = _get_bts(btsid)
    if not bts.ute_admin:
        pet_ute_admin_setup(btsid)
    bts.ute_admin.store.get(bts.ute_admin_alias).api.execute_procedure("activatePlan", {"planId": bts.planid}, 60)
    bts.conn_bts = None
    pet_ute_admin_teardown(btsid)
    return True

def pet_bts_is_onair_by_uteadmin(btsid):
    bts = _get_bts(btsid)
    if not bts.ute_admin:
        pet_ute_admin_setup(btsid)
    state =  bts.ute_admin.get_lnbts_operational_state(alias=bts.ute_admin_alias)
    gv.logger.info('Current state: {}'.format(state))
    return state.upper() == 'ONAIR'

def wait_until_bts_is_onair_by_uteadmin(btsid, timeout, interval):
    return 0
    if not gv.env.use_single_oam:
        return 0
    from robot.utils import timestr_to_secs
    timeout = timestr_to_secs(timeout)
    interval = timestr_to_secs(interval)
    start_time = time.time()
    while time.time() < start_time + timeout:
        check_btslog_fatal()
        try:
            kw('pet_bts_is_onair_by_uteadmin', btsid)
            return 0
        except:
            time.sleep(interval)
    kw('report_error', 'BTS is not onAir by checking uteadmin')

def bts_cpc_pre_check(btsid=''):
    kw('connect_to_bts_control_pc', btsid)
    portlist = [12345, 15003, 15007]
    if gv.env.use_single_oam:
        portlist += [12347]
    for portnum in portlist:
        output = connections.execute_shell_command_without_check('netstat -na|grep %s' %(str(portnum)))
        if 'LISTENING' not in output:
            kw('report_error', 'Port {} is not listening, TA will fail for it. Check passport configuration.'.format(portnum))

def conversion_scf_file(btsid = ''):
    bts = _get_bts(btsid)
    from pet_xml import re_organize_scf
    scf_name = gv.case.curr_case.scf_file
    if gv.ms_bts and (btsid == pv('MS_BTS')) and gv.case.curr_case.ms_scf_file:
        scf_name = gv.case.curr_case.ms_scf_file
    re_organize_scf(bts_source_file(bts.btsid, scf_name), bts_file(bts.btsid, scf_name))

def get_fsp_cpu_usage(btsid = ''):
    bts = _get_bts(btsid)
    try:
        conn = try_best_to_connect_ssh(bts.bts_ip, 22, bts.bts_fcm_username, bts.bts_fcm_password)
        if conn:
            connections.execute_ssh_command_bare('ssh %s@%s\n' %(bts.bts_fcm_username, bts.fspip))
            time.sleep(1)
            output = connections.get_ssh_recv_content()
            if 'Are you sure you want to continue connecting' in output:
                connections.execute_ssh_command_bare('yes\n')
                time.sleep(1)
            connections.execute_ssh_command_bare('%s\n' %(bts.bts_fcm_password))
            time.sleep(1)
            output = connections.get_ssh_recv_content()
            connections.execute_ssh_command_bare('top -n 5 -b |grep Cpu\n')
            time.sleep(20)
            output = connections.get_ssh_recv_content()
            connections.disconnect_from_ssh()
            lines = output.splitlines()
            lines = [line.split()[3].split('[')[0] for line in lines if '[' in line]
            lines = lines[len(lines)/5:]
            return sum([int(x) for x in lines])/len(lines)
    except:
        gv.logger.info('Connect to FSP failed!')
        return 0




if __name__ == '__main__':
    # print  get_fsp_cpu_usage('')
    #print read_bts_config('1450')
    gv.case = IpaMmlItem()
    from pettool import get_case_config_new
    gv.case.curr_case = get_case_config_new('1697165')
    gv.master_bts = read_bts_config('623')
    gv.allbts = [gv.master_bts]


    from pet_xml import re_organize_scf
    re_organize_scf('/home/work/tacase/Resource/config/bts/BTS623/scfc_cap_TL17_asmi.xml',
            '/home/work/Jenkins/workspace/ASMI_TPUT_BTS623/63/169716_2017_06_21__14_36_22/BTS623/scfc_cap_TL17_asmi.xml')

    print pet_bts_read_scf_file('623', '')
    print gv.master_bts.frequency_list
    pass