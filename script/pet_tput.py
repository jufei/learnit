import datetime, os, time
from petbase import *
import pettool

def common_suite_setup_for_tput():
    kw('common_suite_setup_for_pet')

def common_suite_teardown_for_tput():
    kw('common_suite_teardown_for_pet')

def common_test_case_setup_for_tput():
    kw('common_test_case_setup_for_pet')
    kw('select_datadevice')
    kw('tm500_case_setup')
    gv.case.case_log_list = ['tcpdump', 'infomodel']
    kw('start_to_capture_all_kinds_of_logs')

def common_test_case_teardown_for_tput():
    kw('run_keyword_and_ignore_error', 'cleanup_ftp_on_data_device')
    kw('run_keyword_and_ignore_error', 'pet_stop_pppoe_connection')
    kw('run_keyword_and_ignore_error', 'tm500_case_teardown')
    if gv.tm500:
        kw('run_keyword_and_ignore_error', 'pet_release_tm500_resource')
    kw('common_test_case_teardown_for_pet')

def common_test_case_setup_for_throughput():
    kw('common_test_case_setup_for_tput')

def common_test_case_setup_for_handover():
    kw('common_test_case_setup_for_tput')

def common_test_case_teardown_for_throughput():
    kw('common_test_case_teardown_for_tput')

def common_check_for_tput_should_be_ok():
    kw('common_check_for_pet_should_be_ok')

def common_check_for_throughput_should_be_ok():
    kw('common_check_for_tput_should_be_ok')

def common_test_case_setup_for_latency():
    kw('common_test_case_setup_for_tput')
    kw('pet_ue_attach')
    kw('pet_tm500_disconnect')
    kw('pet_tm500_connect')

def common_test_case_teardown_for_latency():
    kw('common_test_case_teardown_for_tput')

def common_test_case_setup_for_ping_delay():
    kw('common_test_case_setup_for_tput')
    # kw('pet_ue_attach')
    # kw('pet_tm500_disconnect')
    # kw('pet_tm500_connect')

def common_test_case_teardown_for_ping_delay():
    kw('cleanup_ftp_on_data_device')
    kw('common_test_case_teardown_for_tput')

def common_test_case_teardown_for_handover():
    kw('run_keyword_and_ignore_error', 'execute_command_on_data_device', ['killall iperf', 'ps -ef|grep iperf'])
    kw('common_test_case_teardown_for_tput')


#Keyword for PPPOE
def setup_pppoe_connection():
    kw('connect_to_tm500_control_pc')
    if gv.case.curr_case.ca_type == '3CC':
        kw('Start_Pppoe_Connection', gv.tm500.pppoe_connection_lme)
    else:
        kw('Start_Pppoe_Connection', gv.tm500.pppoe_connection)
    gv.pppoe_ip = kw('Get Pppoe Connection Ip Address')
    gv.logger.info('Setup PPPOE successfully,  ip: [%s] ' %(gv.pppoe_ip))

def capture_ttitrace_for_tput():
    kw('sleep', '10s')
    from pet_bts import read_bts_config
    bts = read_bts_config(gv.master_bts.bts_id, 'M', 'P')
    tti_tool_path = '/data/pylib/tools/ttitrace'
    save_log_path = gv.case.log_directory
    from pet_tti_c import c_tti_trace
    gv.logger.info(gv.env.bts_version)

    tti = c_tti_trace(bts.bts_control_pc_lab, bts.sw_release, gv.master_bts.cell_count, gv.env.bts_version, tti_tool_path, save_log_path, '')
    tti.get_tti_core_info()
    tti.get_tti_application()
    gv.logger.info(tti.core_info)
    gv.logger.info(tti.telnet_ip)
    tti.start_capture_tti_log()

def wait_until_throughput_is_ready():
    from robot.utils import timestr_to_secs
    timeout = gv.case.curr_case.case_duration if gv.case.curr_case.case_duration else '5mins'
    timeout = '20s' if gv.debug_mode <> 'RUN' else timeout
    timeout = '5mins'
    fail_keywords = ['FAILURE', 'ERROR', 'LEAVE', 'DISCONNECTION', 'Assert', 'Re-establishment']
    interval = 30
    total_time = timestr_to_secs(timeout)
    try:
        kw('run_keyword_and_ignore_error', 'pet_start_tm500_logging')
        write_to_console('Start CPK Service...')
        kw('pet_connect_to_tma')
        count = 0
        output = ''
        start_time = time.time()
        ttitrace = False
        while time.time() < start_time + total_time:
            check_btslog_fatal()
            if not ttitrace:
                kw('run_keyword_and_ignore_error', 'capture_ttitrace_for_tput')
                ttitrace = True
            from pet_tm500 import pet_get_running_throughput_from_tm500
            dl, ul = pet_get_running_throughput_from_tm500()
            # dl, ul =  kw('run_keyword_and_ignore_error', 'pet_get_running_throughput_from_tm500')
            if float(dl) + float(ul) <1:
                kw('report_error', 'Too low throughput, [%0.2f], case will be stopped.' %(float(dl) + float(ul)))
            else:
                record_debuginfo('Current through put: %0.2fM' %(float(dl) + float(ul)))

            ret = connections.read_tm500_output()
            if ret.strip():
                record_debuginfo(ret)
                output += ret
                errorlines = contain_keywords(output, fail_keywords)
                if len(errorlines) > 0:
                    kw('log', 'Unexpected Error info: ' + ';'.join(errorlines))
                    record_debuginfo(output)
                    kw('report_error', 'Found failure in TM500 output [%s].' %(ret))
                    break
            time.sleep(interval)
            record_debuginfo('Still need wait for : %d seconds.' %((start_time + total_time - time.time())))
    finally:
        gv.master_bts.conn_bts = None
        kw('run_keyword_and_ignore_error', 'pet_stop_tm500_logging')

def wait_until_ftp_download_is_ready():
    wait_until_throughput_is_ready()

def wait_until_ftp_upload_is_ready():
    wait_until_throughput_is_ready()

def ping_from_bts_control_pc_to_ue():
    kw('connect_to_bts_control_pc')
    kw('Ping Remote System', gv.service.ue_ip)

def wait_until_ue_deattached():
    kw('wait_until_find_expected_string_in_tm500_output', '1mins', '2s', 'I: CMPI RRC Leave Connected Cell Selection')

def wait_until_ue_re_attached():
    kw('wait_until_find_expected_string_in_tm500_output', '1mins', '2s',
        ['I: CMPI L2 Random Access Initiated',
         'I: CMPI DTE PPPOE CONNECTION IND: UE Id'])

def try_to_trigger_ue_by_ping_operation():
    run_local_command('ping -c 1 -W 1 %s >/dev/null' %(gv.service.ue_ip))

def ping_from_ue_to_bts(times, ping_count, ping_size):
    times = 1 if gv.debug_mode <> 'RUN' else times
    kw('connect_to_tm500_control_pc')
    ret = 0
    msg = kw('Ping Remote System', gv.master_bts.bts_control_pc_lab)
    if float(msg[0][1]) == 0: #Receive = 0, means: ping failed
        kw('report_error', 'Ping failed, please check it.')
    else:
        for i in range(int(times)):
            msg = kw('Ping Remote System', gv.master_bts.bts_control_pc_lab, '-n %s -l %s' %(ping_count, ping_size))
            if ret == 0:
                ret = float(msg[1][2])
            else:
                ret = min(ret, float(msg[1][2]))
            if ret <= 1.0:
                kw('report_error', 'Ping delay [%s] is doubtful, please check it.' %(str(ret)))
        gv.kpi.ping_avg_time = float(ret)

def ping_from_data_device(times, ping_count, ping_size):
    # import time
    # time.sleep(60)
    # times = 10 if gv.debug_mode <> 'RUN' else times
    remote = '10.69.66.150'
    remote = gv.master_bts.bts_ip
    cmd = 'ping  %s -c %s -s %s' %(remote, ping_count, ping_size)
    kw('execute_command_on_data_device', 'route add %s ppp0' %(remote))
    ret = 0
    output = kw('execute_command_on_data_device', 'ping %s -w 1' %(remote))
    if r'100% packet loss' in output:
        kw('report_error', 'Ping failed, please check it.')
    for i in range(int(times)):
        check_btslog_fatal()
        output = kw('execute_command_on_data_device', cmd)
        if not r'0% packet loss' in output:
            kw('report_error', 'Some ping packet lost, please check it.')
        validlines = [line for line in output.splitlines() if 'icmp_seq=' in line][1:]
        ti = 0
        for line in validlines:
            ti += [float(x.split('=')[1]) for x in line.split() if 'time=' in x][0]
        avg = float(ti)/(float(ping_count)-1)

        if ret == 0:
            ret = float(avg)
        else:
            ret = min(ret, avg)
        kw('log', 'The average ping delay is: [%s]' %(str(avg)))
        if ret <= 1.0:
            kw('report_error', 'Ping delay [%s] is doubtful, please check it.' %(str(ret)))
    gv.kpi.ping_avg_time = float(ret)

def start_to_capture_throughput_for_analysis():
    kw('sleep', '40s')

def repeat_to_do_intra_enb_handover_until_tm500_log_is_valid():
    src_rru = '1'
    dst_rru = '2'
    for i in range(20):
        kw('log', 'Handover for round: %d' %(i+1))
        kw('pet_start_tm500_logging')
        kw('adjust_rru_signal', src_rru, '-10db')
        kw('increase_signal_of_rru_until_handover_happen', dst_rru)
        kw('stop_tm500_logging_and_download_logs', 'tm500log%d' %(i))
        if kw('tm500_log_is_valid_for_handover'):
            kw('log', 'This round, TM500 log file is valid.')
            return 0
        else:
            kw('adjust_rru_signal', src_rru, 'MIN')
            kw('adjust_rru_signal', dst_rru, 'MAX')
            kw('adjust_rru_signal', dst_rru, '-10db')
            tmp = src_rru
            src_rru = dst_rru
            dst_rru = tmp
    kw('report_error', 'TA has run 10 rounds but TM500 log files always invalid, case failed.')

def pet_ue_attach_for_mue_tput():
    kw('pet_connect_to_tma')
    kw('run_keyword_and_ignore_error', 'stop_running_test_group')
    from pet_tm500_script import get_tput_mue_attach_script
    lines = get_tput_mue_attach_script(gv.master_bts)
    lines = [line.replace('\n', '') for line in lines if not re.match('(^(\r|\n|\s+)$)|(^$)|^#', line)] # remove all the unnecessary lines including comment
    save_log(lines, case_file('real_attach.txt'), 'N')
    kw('provision_shenick_group')


    output = ''
    fail_keywords = ['FAILURE', 'ERROR', 'LEAVE', 'DISCONNECTION', 'Assert', 'DELETE']

    for line in lines:
        output += connections.execute_tm500_command_without_check(line, '2048', '0')
        save_log(output.splitlines(), case_file('attach_result.log'))
        errorlines = contain_keywords(output, fail_keywords)
        if len(errorlines) > 0:
            kw('log', 'Found eror: ' + ';'.join(errorlines))
            kw('report_error', 'Found failure in TM500 output [%s].' %(errorlines[0]))

    done = False
    count = 0



    gv.case.curr_case.real_ue_count = gv.case.curr_case.ue_count
    total_time = 2 * int(gv.case.curr_case.real_ue_count)
    total_time = 60 if total_time < 60 else total_time
    while count <= total_time:
        ret = connections.read_tm500_output()
        if ret.strip():
            output += ret
            save_log(output.splitlines(), case_file('attach_result.log'))
            errorlines = contain_keywords(output, fail_keywords)
            if len(errorlines) > 0:
                kw('log', 'Found eror: ' + ';'.join(errorlines))
                save_log(output.splitlines(), case_file('attach_result.log'))
                kw('report_error', 'Found failure in TM500 output [%s].' %(errorlines[0]))
            attached_uelist = [line for line in output.splitlines() if 'IPv4 Address:' in line]
            if len(attached_uelist) >= int(gv.case.curr_case.real_ue_count):
                record_debuginfo('Attach completed.')
                done = True
                break
            else:
                kw('log', 'MUE attach success ratio: %s ratio' %(str(100*len(attached_uelist)/int(gv.case.curr_case.real_ue_count))))
        time.sleep(1)
        count += 1

    output += connections.execute_tm500_command_without_check('forw mte getstats [6]', '2048', '0')
    record_tm500log(output)
    gv.case.curr_case.tput_mue_attach_ratio = 100*len(attached_uelist)/int(gv.case.curr_case.real_ue_count)
    if int(gv.case.curr_case.tput_mue_attach_ratio) <> 100:
        kw('report_error', 'UE attach ratio is not 100%% instead of %s%% , please check it.' %(gv.case.curr_case.tput_mue_attach_ratio))
    gv.master_bts.ue_ip_list = [x.split()[-1].strip() for x in attached_uelist]

    if gv.case.curr_case.case_type in ['CPK_MUE_DL_COMBIN']:
        time.sleep(30)
        from pet_shenick import execute_shenick_cli_command
        # execute_shenick_cli_command('setServiceStateOfApplication MUE_UDP/IP/DL_UDP_lp0_0000_0 "Out of Service"')
        cmd = 'setServiceStateOfApplication MUE_UDP/IP/DL_UDP_lp0_0000_0 "In Service"'
        cmd = cmd.replace('"', "'")
        print execute_shenick_cli_command(cmd)
        # execute_shenick_cli_command('setServiceStateOfApplication MUE_UDP/IP/DL_UDP_lp0_0000_0 "In Service"')

def stop_pppoe_connection(connection_name):
    connections.execute_shell_command('rasdial "%s" /DISCONNECT' % connection_name)

if __name__ == '__main__':
    from pet_tm500 import read_tm500_config
    gv.tm500 = read_tm500_config('88')
    from pet_shenick import _build_shenick_command
    print _build_shenick_command()

    cmd = 'setServiceStateOfApplication MUE_UDP/IP/DL_UDP_lp0_0000_0 "In Service"'
    cmd = cmd.replace('"', "'")
    print _build_shenick_command(cmd)
