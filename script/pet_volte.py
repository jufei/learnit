import datetime, os, time
import select
from petbase import *
import pettool
from decimal import *

def common_suite_setup_for_volte():
    kw('common_suite_setup_for_pet')

def common_suite_teardown_for_volte():
    kw('common_suite_teardown_for_pet')

def common_test_case_setup_for_volte():
    kw('common_test_case_setup_for_pet')
    kw('select_datadevice')
    kw('tm500_case_setup')
    gv.case.case_log_list = []
    kw('start_to_capture_all_kinds_of_logs')


def common_test_case_teardown_for_volte():
    # if gv.debug_mode == 'DEBUG':
    #     return 0
    kw('run_keyword_and_ignore_error', 'stop_and_download_tshark')
    kw('run_keyword_and_ignore_error', 'clear_mts')
    kw('run_keyword_and_ignore_error', 'stop_running_test_group')
    kw('run_keyword_and_ignore_error', 'tm500_case_teardown')
    if gv.tm500:
        kw('run_keyword_and_ignore_error', 'pet_release_tm500_resource')
    kw('common_test_case_teardown_for_pet')

def common_test_case_setup_for_volte_coverate():
    kw('common_test_case_setup_for_pet')

def common_check_for_volte_should_be_ok():
    kw('common_check_for_pet_should_be_ok')

def pet_ue_attach_for_volte():
    kw('run_keyword_and_ignore_error', 'stop_running_test_group')
    kw('pet_connect_to_tma')
    from pet_tm500_script import get_volte_tm500_script
    lines = get_volte_tm500_script(gv.master_bts)
    lines = [line.replace('\n', '') for line in lines if not re.match('(^(\r|\n|\s+)$)|(^$)|^#', line)] # remove all the unnecessary lines including comment
    save_log(lines, case_file('real_attach.txt'), 'N')
    kw('provision_shenick_group')
    kw('run_keyword_and_ignore_error', 'start_tshark_on_bts')
    output = ''
    fail_keywords = ['FAILURE', 'ERROR', 'LEAVE', 'DISCONNECTION', 'Assert', 'DELETE']
    except_keywords = ['RRC_ENABLE_RELEASE']

    for line in lines:
        output = connections.execute_tm500_command_without_check(line, '2048', '0')
        save_log(output.splitlines(), case_file('volte_attach_result.log'))
        errorlines = contain_keywords(output, fail_keywords)
        if len(errorlines) > 0:
            kw('log', 'Found eror: ' + ';'.join(errorlines))
            kw('report_error', 'Found failure in TM500 output [%s].' %(errorlines[0]))

    done = False
    count = 0
    if gv.case.curr_case.case_type == 'VOLTE_PERM':
        return 0

    total_time = 2 * int(gv.case.curr_case.real_ue_count)
    total_time = 60 if total_time < 60 else total_time
    while count <= total_time:
        check_btslog_fatal()
        ret = connections.read_tm500_output()
        if ret.strip():
            output += ret
            save_log(ret.splitlines(), case_file('volte_attach_result.log'))
            errorlines = contain_keywords(output, fail_keywords, except_keywords)
            if len(errorlines) > 0:
                f_ueid = ''
                kw('log', 'Found eror: ' + ';'.join(errorlines))
                if 'UE Id:' in errorlines[0]:
                    f_ueid = errorlines[0].split('UE Id:')[1].split()[0]
                    print 'Info for the failed UE: '+f_ueid
                    for line in output.splitlines():
                        if 'UE Id:' + f_ueid in line:
                            print line
                if f_ueid:
                    tempstr = connections.execute_tm500_command_without_check('forw mte getstats [6] [%s]' %(f_ueid), '2048', '0')
                else:
                    tempstr = connections.execute_tm500_command_without_check('forw mte getstats [6]', '2048', '0')
                kw('pet_get_running_throughput_from_tm500')
                save_log(tempstr.splitlines(), case_file('volte_attach_result.log'))
                kw('report_error', 'Found failure in TM500 output [%s].' %(errorlines[0]))
            qci1lines   = [line for line in output.splitlines() if 'I: CMPI MTE 0 NAS BEARER RESOURCE ADD IND:UE Id:' in line]
            if len(qci1lines) >= int(gv.case.curr_case.real_ue_count):
                record_debuginfo('Attach completed.')
                done = True
                break
            else:
                kw('log', 'QCI1 Ratio: %s ratio' %(str(100*len(qci1lines)/int(gv.case.curr_case.real_ue_count))))
        time.sleep(1)
        count += 1
    record_tm500log(output)

    rclines     = [line for line in output.splitlines() if 'I: CMPI MTE 0 ECM CONNECTION IND:UE Id:' in line]
    attachlines = [line for line in output.splitlines() if 'I: CMPI MTE 0 EMM REGISTER IND:UE Id:' in line]
    qci5lines   = [line for line in output.splitlines() if 'I: CMPI MTE 0 NAS PDN CONNECTION IND:UE Id:' in line]
    qci1lines   = [line for line in output.splitlines() if 'I: CMPI MTE 0 NAS BEARER RESOURCE ADD IND:UE Id:' in line]
    load_ues    = int(gv.case.curr_case.load_ue_count) if int(gv.case.curr_case.load_ue_count) else 0
    gv.case.curr_case.rc_setup_ratio    = len(rclines)*100/(int(gv.case.curr_case.ue_count) + load_ues)
    gv.case.curr_case.attach_ratio      = len(attachlines)*100/(int(gv.case.curr_case.ue_count) + load_ues)
    gv.case.curr_case.qci5_ratio        = len(qci5lines)*100/int(gv.case.curr_case.ue_count)
    gv.case.curr_case.qci1_ratio        = len(qci1lines)*100/int(gv.case.curr_case.ue_count)
    kw('log', 'RRC Setup Ratio:  %s%%' %(gv.case.curr_case.rc_setup_ratio))
    kw('log', 'Attach Ratio:  %s%%' %(gv.case.curr_case.attach_ratio))
    kw('log', 'QCI5 Ratio:  %s%%' %(gv.case.curr_case.qci5_ratio))
    kw('log', 'QCI1 Ratio:  %s%%' %(gv.case.curr_case.qci1_ratio))
    if int(gv.case.curr_case.qci1_ratio) <> 100:
        kw('report_error', 'QCI1 Ratio is not 100%% instead of %s%% , please check it.' %(gv.case.curr_case.qci1_ratio))
    gv.kpi.kpi_volte_cap = gv.case.curr_case.real_ue_count

def pet_ue_attach_for_mix_volte():
    kw('run_keyword_and_ignore_error', 'stop_running_test_group')
    kw('pet_connect_to_tma')
    from pet_tm500_script import get_volte_tm500_script
    lines = get_volte_tm500_script(gv.master_bts)
    lines = [line.replace('\n', '') for line in lines if not re.match('(^(\r|\n|\s+)$)|(^$)|^#', line)] # remove all the unnecessary lines including comment
    save_log(lines, case_file('real_attach.txt'), 'N')
    kw('provision_shenick_group')
    kw('run_keyword_and_ignore_error', 'start_tshark_on_bts')
    output = ''
    fail_keywords = ['FAILURE', 'ERROR', 'LEAVE', 'DISCONNECTION', 'Assert', 'DELETE']
    except_keywords = ['RRC_ENABLE_RELEASE']

    for line in lines:
        output = connections.execute_tm500_command_without_check(line, '2048', '0')
        save_log(output.splitlines(), case_file('volte_attach_result.log'))
        errorlines = contain_keywords(output, fail_keywords)
        if len(errorlines) > 0:
            kw('log', 'Found eror: ' + ';'.join(errorlines))
            kw('report_error', 'Found failure in TM500 output [%s].' %(errorlines[0]))

    done = False
    count = 0

    total_ue_count   = int(gv.case.curr_case.ue_count) + int(gv.case.curr_case.load_ue_count)
    total_time = 2 * int(total_ue_count)
    total_time = 120 if total_time < 120 else total_time
    start_time = time.time()
    gv.logger.info('Total timer: '+str(total_time))
    while time.time() < start_time + total_time:
        check_btslog_fatal()
        ret = connections.read_tm500_output()
        if ret.strip():
            output += ret
            save_log(ret.splitlines(), case_file('volte_attach_result.log'))
            errorlines = contain_keywords(output, fail_keywords, except_keywords)
            if len(errorlines) > 0:
                f_ueid = ''
                kw('log', 'Found eror: ' + ';'.join(errorlines))
                if 'UE Id:' in errorlines[0]:
                    f_ueid = errorlines[0].split('UE Id:')[1].split()[0]
                    print 'Info for the failed UE: '+f_ueid
                    for line in output.splitlines():
                        if 'UE Id:' + f_ueid in line:
                            print line
                if f_ueid:
                    tempstr = connections.execute_tm500_command_without_check('forw mte getstats [6] [%s]' %(f_ueid), '2048', '0')
                else:
                    tempstr = connections.execute_tm500_command_without_check('forw mte getstats [6]', '2048', '0')
                kw('pet_get_running_throughput_from_tm500')
                save_log(tempstr.splitlines(), case_file('volte_attach_result.log'))
                kw('report_error', 'Found failure in TM500 output [%s].' %(errorlines[0]))
            qci1lines   = [line for line in output.splitlines() if 'QoS Indication:  QCI Label:1' in line]
            qci2lines   = [line for line in output.splitlines() if 'QoS Indication:  QCI Label:2' in line]
            if len(qci1lines) >= total_ue_count:
                record_debuginfo('Attach completed.')
                done = True
                break
            else:
                kw('log', 'QCI1 Ratio: %s ratio' %(str(100*len(qci1lines)/total_ue_count)))
        time.sleep(5)
    record_tm500log(output)

    rclines     = [line for line in output.splitlines() if 'I: CMPI MTE 0 ECM CONNECTION IND:UE Id:' in line]
    attachlines = [line for line in output.splitlines() if 'I: CMPI MTE 0 EMM REGISTER IND:UE Id:' in line]
    qci5lines   = [line for line in output.splitlines() if 'I: CMPI MTE 0 NAS PDN CONNECTION IND:UE Id:' in line]
    qci1lines   = [line for line in output.splitlines() if 'QoS Indication:  QCI Label:1' in line]
    qci2lines   = [line for line in output.splitlines() if 'QoS Indication:  QCI Label:2' in line]
    load_ues    = int(gv.case.curr_case.load_ue_count) if int(gv.case.curr_case.load_ue_count) else 0
    gv.case.curr_case.rc_setup_ratio    = len(rclines)*100/(int(gv.case.curr_case.real_ue_count) + load_ues)
    gv.case.curr_case.attach_ratio      = len(attachlines)*100/total_ue_count
    gv.case.curr_case.qci5_ratio        = len(qci5lines)*100/total_ue_count
    gv.case.curr_case.qci1_ratio        = len(qci1lines)*100/total_ue_count
    gv.case.curr_case.qci2_ratio        = len(qci2lines)*100/int(gv.case.curr_case.ue_count)
    kw('log', 'RRC Setup Ratio:  %s%%' %(gv.case.curr_case.rc_setup_ratio))
    kw('log', 'Attach Ratio:  %s%%' %(gv.case.curr_case.attach_ratio))
    kw('log', 'QCI5 Ratio:  %s%%' %(gv.case.curr_case.qci5_ratio))
    kw('log', 'QCI1 Ratio:  %s%%' %(gv.case.curr_case.qci1_ratio))
    kw('log', 'QCI2 Ratio:  %s%%' %(gv.case.curr_case.qci2_ratio))
    if int(gv.case.curr_case.qci1_ratio) <> 100:
        kw('report_error', 'QCI1 Ratio is not 100%% instead of %s%% , please check it.' %(gv.case.curr_case.qci1_ratio))
    gv.kpi.kpi_volte_cap = gv.case.curr_case.real_ue_count

    lines = output.splitlines()
    gv.case.curr_case.ue_info = {}
    gv.case.curr_case.focus_ue_count = min(4, int(gv.case.curr_case.ue_count))
    for i in range(len(lines)):
        if 'Pdn Id:1' in lines[i]:
            ueid = lines[i-1].split('UE Id:')[-1]
            ipaddr = lines[i+3].split()[-1]
            gv.case.curr_case.ue_info[ueid] = ipaddr
    gv.logger.info(gv.case.curr_case.ue_info)

def capture_packet_for_mix_volte_server():
    def _build_command(cmd):
        return 'cli -u %s -p %s  %s' %(gv.tm500.shenick_username, gv.tm500.shenick_partition, cmd)
    conn = connections.connect_to_ssh_host(gv.tm500.shenick_control_ip,
                                           gv.tm500.shenick_control_port,
                                           gv.tm500.shenick_control_username,
                                           gv.tm500.shenick_control_password,
                                           '~$')
    connections.switch_ssh_connection(conn)

    output = ''
    output += connections.execute_ssh_command_without_check(_build_command('pcapFinish'))
    for i in range(gv.case.curr_case.focus_ue_count):
        output += connections.execute_ssh_command_without_check('rm -rf /tmp/ue%d.pcap' %(i))
    output += connections.execute_ssh_command_without_check(_build_command('pcapState'))
    for i in range(gv.case.curr_case.focus_ue_count):
        output += connections.execute_ssh_command_without_check(_build_command('pcapStart Interface=%s/1/0 NoOfPackets=100000000 DestIpa=%s DurationSec=120 /tmp/ue%d.pcap' %(
                                                   9+int(gv.tm500.shenick_partition), gv.case.curr_case.ue_info[str(i)], i)))

    for i in range(25):
        output += connections.execute_ssh_command_without_check(_build_command('pcapState'))
        time.sleep(5)
    output += connections.execute_ssh_command_without_check(_build_command('pcapStop'))
    output += connections.execute_ssh_command_without_check(_build_command('pcapFinish'))
    connections.disconnect_from_ssh()

    from pet_shenick import get_file_from_shenick
    for i in range(gv.case.curr_case.focus_ue_count):
        get_file_from_shenick('/tmp/ue%d.pcap' %(i), '%s/ue%d.pcap' %(gv.case.curr_case.round_dire, i))


def wait_until_volte_service_is_done():
    from robot.utils import timestr_to_secs
    timeout = int(gv.case.curr_case.case_duration) if gv.case.curr_case.case_duration else 300
    # timeout = 300 if gv.debug_mode <> 'RUN' and timeout>100 else timeout
    fail_keywords = ['FAILURE', 'ERROR', 'Release Request', 'NAS DELETE', 'BEARER RESOURCE DELETE']
    interval = 10
    ttitrace = False

    gv.kpi.kpi_case_duration = int(gv.case.curr_case.case_duration)/60
    try:
        time.sleep(20)
        write_to_console('Start VOLTE Service...')
        kw('pet_connect_to_tma')
        start_time = time.time()
        total_time = timestr_to_secs(timeout)
        count = 0
        output = ''
        while time.time() < start_time + total_time:
            check_btslog_fatal()
            if total_time - (time.time() - start_time) > 200:
                ret = connections.read_tm500_output()
                if ret.strip():
                    kw('report_error', 'Found failure in TM500 output: [%s].' %(ret))
            count += 1
            # if gv.debug_mode == 'RUN' and gv.case.curr_case.case_type.upper() in ['VOLTE_CAP']:
            #     kw('check_if_data_flow_is_working')
            # else:
            #     time.sleep(60)
            time.sleep(0.1)
            if count > 1000:
                count = 0
                record_debuginfo('Still need wait for : %d seconds.' %((start_time + total_time - time.time())))
    finally:
        gv.master_bts.conn_bts = None

    # retrieve_shenick_statistic_result()
    if gv.case.curr_case.use_kpi_counter:
        kw('wait_until_new_pmcount_file_generated')
        kw('counter_kpi_should_be_correct')
        kw('calculate_kpi_for_mix_volte')


    kw('run_keyword_and_ignore_error', 'clear_mts')

def wait_until_mix_volte_service_is_done():
    from robot.utils import timestr_to_secs
    timeout = int(gv.case.curr_case.case_duration) if gv.case.curr_case.case_duration else 300
    timeout = 1500 if gv.debug_mode <> 'RUN' and timeout>100 else timeout
    fail_keywords = ['FAILURE', 'ERROR', 'Assert', 'NAS DELETE', 'BEARER RESOURCE DELETE', 'RRC LEAVE']
    interval = 10
    ttitrace = False
    except_keywords = []

    gv.kpi.kpi_case_duration = int(gv.case.curr_case.case_duration)/60
    try:
        write_to_console('Start Mix VOLTE Service...')
        kw('pet_connect_to_tma')
        start_time = time.time()
        total_time = timestr_to_secs(timeout)
        count = 0
        output = ''
        service_round = 1
        while time.time() < start_time + total_time:
            check_btslog_fatal()
            kw('do_mix_volte_service', service_round)
            service_round += 1
            ret = connections.read_tm500_output()
            if total_time - (time.time() - start_time) > 300:
                errorlines = contain_keywords(ret, fail_keywords, except_keywords)
                if len(errorlines) > 0:
                    kw('report_error', 'Found failure in TM500 output: [%s].' %(ret))
            count += 1
            time.sleep(5)
            record_debuginfo('Still need wait for : %d seconds.' %((start_time + total_time - time.time())))
    finally:
        gv.master_bts.conn_bts = None

    kw('get_fine_statistic', 'Normal')
    calculate_final_kpi_for_mix_volte_service()
    # if gv.debug_mode <> 'DEBUG':
    if gv.case.curr_case.use_kpi_counter:
        kw('wait_until_new_pmcount_file_generated')
        kw('counter_kpi_should_be_correct')
        kw('calculate_kpi_for_mix_volte')

def calculate_kpi_for_mix_volte():
    pass

def file_exists_on_data_device(filename):
    output = kw('execute_command_on_data_device', 'ls -la ' + filename)
    if 'No such file or directory' in output:
        kw('report_error', 'File has not found')

def wait_until_volte_data_file_exist(filename, timeout):
    kw('wait_until_keyword_succeeds', '5mins', '2', 'file_exists_on_data_device', filename)

def retrieve_shenick_statistic_result():
    kw('get_shenick_test_group_detail_result', gv.tm500.shenick_volte_group_name, case_file('CurrentDetail.zip'))
    kw('deal_with_voip_result_file', case_file('CurrentDetail.zip'))

def deal_with_voip_result_file(filename):
    def _process_kpi_log(field, filename):
        with open(filename, 'w') as f:
            ueids = ['%0.4d' %(x) for x in range(int(gv.case.curr_case.real_ue_count))]
            timestamplist = []
            for ueid in ueids:
                timestamplist +=  getattr(uedata[ueid], field).keys()
            timestamplist = list(set(timestamplist))
            timestamplist.sort()

            f.write('timestamp,'+','.join(ueids)+',Average'+'\n')
            lines = []
            allvalue = []
            for timestamp in timestamplist:
                line = timestamp
                for ueid in ueids:
                    if timestamp in getattr(uedata[ueid], field).keys():
                        value = getattr(uedata[ueid], field)[timestamp]
                    else:
                        value = 'nan'
                    line += ',' +value
                valuelist = [float(x) for x in line.split(',')[1:] if x.strip() and x.upper() != 'NAN']
                allvalue += valuelist
                avg_timestamp = str(sum(valuelist)/len(valuelist)) if valuelist else 'nan'
                line += ',' + avg_timestamp
                lines.append(line.split(',')[1:])
                f.write(line+'\n')
            line = 'Average'
            avglist = []
            for i in range(len(ueids)):
                col = [float(x[i]) for x in lines if x[i].strip() and x[i].upper() != 'NAN']
                avg_ue = str(sum(col)/len(col)) if col else 'nan'
                line += ',' +avg_ue
                if avg_ue <> 'nan':
                    avglist.append(float(avg_ue))
            valuelist = [float(x) for x in line.split(',')[1:] if x.strip() and x.upper() != 'NAN']
            if float(len(allvalue)) == 0:
                total_avg = 0
            else:
                total_avg =sum(allvalue)/float(len(allvalue))
            line += ','+ str(total_avg)
            f.write(line+'\n')
            if avglist == []:
                kwg('report_error', 'volte mos check fail: avglist is null')
                return total_avg, 0, 0
            return round(total_avg, 5), round(min(avglist), 5), round(max(avglist), 5)


    # filename = r'D:\temp\01\CurrentDetail.zip'
    import zipfile
    cared_fields = ['QmVoice MOS', 'RTP Jitter (RFC3550) ms', 'QmVoice Mean PDV ms', 'Out RTP Packets/s', 'In RTP Packets/s']
    f = zipfile.ZipFile(filename)
    csvfiles = [x.filename for x in f.filelist if '.csv' in x.filename and 'voip' in x.filename]
    uedata = IpaMmlDict()
    ueids = ['%0.4d' %(x) for x in range(int(gv.case.curr_case.load_ue_count) + int(gv.case.curr_case.ue_count))]
    out_rtp, in_rtp = 0, 0

    for csvfile in csvfiles:
        aue = IpaMmlItem()
        aue.filename = csvfile
        aue.id = csvfile.split('_')[1]
        if aue.id in ueids:
            lines = f.read(csvfile).splitlines()
            title = lines[0].split(',')
            aue.mos_data        = {}
            aue.jitter_data     = {}
            aue.pdv_data        = {}
            aue.out_rtp_data    = {}
            aue.in_rtp_data     = {}
            for i in range(5, len(lines)):
                if lines[i].split(',')[title.index('In Service')] == '1':
                    aue.mos_data[lines[i].split(',')[0]]        = lines[i].split(',')[title.index('QmVoice MOS')]
                    aue.jitter_data[lines[i].split(',')[0]]     = lines[i].split(',')[title.index('RTP Jitter (RFC3550) ms')]
                    aue.pdv_data[lines[i].split(',')[0]]        = lines[i].split(',')[title.index('QmVoice Mean PDV ms')]
                    aue.out_rtp_data[lines[i].split(',')[0]]    = lines[i].split(',')[title.index('Out RTP Packets/s')]
                    aue.in_rtp_data[lines[i].split(',')[0]]     = lines[i].split(',')[title.index('In RTP Packets/s')]
                    if int(aue.id)%2 == 0: # first ue, like 0000
                        out_rtp += float(lines[i].split(',')[title.index('Out RTP Packets/s')])
                    else:
                        in_rtp += float(lines[i].split(',')[title.index('In RTP Packets/s')])
            uedata[aue.id] = aue
    f.close()
    gv.kpi.kpi_volte_mos,       gv.kpi.kpi_volte_min_mos,       gv.kpi.kpi_volte_max_mos    = _process_kpi_log('mos_data', case_file('mos.csv'))
    gv.kpi.kpi_volte_jitter,    gv.kpi.kpi_volte_min_jitter,    gv.kpi.kpi_volte_max_jitter = _process_kpi_log('jitter_data', case_file('jitter.csv'))
    gv.kpi.kpi_volte_pdv,       gv.kpi.kpi_volte_min_pdv,       gv.kpi.kpi_volte_max_pdv    = _process_kpi_log('pdv_data', case_file('pdv.csv'))
    print 'out_rtp: ', out_rtp
    if out_rtp != 0 :
        gv.kpi.kpi_loss_ratio = round(1.0-in_rtp/out_rtp, 3)
    else:
        gv.kpi.kpi_loss_ratio = 1

    print gv.kpi
    kw('log', 'MOS: [min: %s, avg: %s, max: %s] '    %(gv.kpi.kpi_volte_min_mos,       gv.kpi.kpi_volte_mos,       gv.kpi.kpi_volte_max_mos))
    kw('log', 'Jitter: [min: %s, avg: %s, max: %s] ' %(gv.kpi.kpi_volte_min_jitter,    gv.kpi.kpi_volte_jitter,    gv.kpi.kpi_volte_max_jitter))
    kw('log', 'Pdv: [min: %s, avg: %s, max: %s] '    %(gv.kpi.kpi_volte_min_pdv,       gv.kpi.kpi_volte_pdv,       gv.kpi.kpi_volte_max_pdv))
    kw('log', 'Packet loss ratio: %0.2f%%' %(gv.kpi.kpi_loss_ratio*100))

def check_if_data_flow_is_working():
    filename = 'MonitorData_%s.zip' %(time.strftime("%Y_%m_%d__%H_%M_%S"))
    kw('get_shenick_test_group_detail_result', gv.tm500.shenick_volte_group_name, case_file(filename))
    kw('check_if_data_follow_is_zero', case_file(filename))

def check_if_data_follow_is_zero(zipfilename):
    import zipfile
    error_msg = ''
    f = zipfile.ZipFile(zipfilename)
    try:
        csvfiles = [x.filename for x in f.filelist if '.csv' in x.filename and 'voip' in x.filename]
        ueids = ['%0.4d' %(x) for x in range(int(gv.case.curr_case.real_ue_count))]
        for csvfile in csvfiles:
            ueid = csvfile.split('_')[1]
            if ueid in ueids:
                lines = f.read(csvfile).splitlines()
                lines = [line for line in lines if line.strip()]
                rate = lines[-1].split(',')[2].lower()
                if rate == 'nan' or float(rate) == 0:
                    error_msg = 'Data flow for UE [%s] is 0, case will fail. [%s]' %(ueid, rate)
                    break
    finally:
        f.close()
    if error_msg:
        kw('report_error', error_msg)

def do_a_short_time_test_for_ue_volte_access():
    kw('pet_tm500_disconnect')
    kw('pet_tm500_connect')
    kw('pet_ue_attach_for_volte')
    kw('wait_until_volte_service_is_done')

def repeat_to_do_ue_call_drop_for_specific_time(spec_times=1):
    spec_times = 2 if gv.debug_mode <> 'RUN' else int(spec_times)
    gv.kpi.kpi_volte_call_drop_ratio = 'INVALID'
    for i in range(int(spec_times)):
        kw('log', 'Time: %d' %(i+1))
        if i <>0:
            kw('pet_tm500_disconnect')
            kw('sleep', '90s')
            kw('pet_tm500_connect')
        kw('pet_ue_attach_for_volte')
        kw('wait_until_volte_service_is_done')
    gv.kpi.kpi_volte_call_drop_ratio = 0

def repeat_to_do_volte_service_for_specific_time(spec_times = 1):
    spec_times = 2 if gv.debug_mode <> 'RUN' else int(spec_times)
    gv.kpi.kpi_volte_perm_mos_list = []
    gv.kpi.kpi_volte_perm_loss_ratio_list = []
    gv.kpi.kpi_volte_perm_loss_ratio = 'INVALID'
    for i in range(int(spec_times)):
        kw('log', 'Time: %d' %(i+1))
        if i <>0:
            kw('pet_tm500_disconnect')
            kw('sleep', '90s')
            kw('pet_tm500_connect')
        kw('pet_ue_attach_for_volte')
        kw('wait_until_volte_service_is_done')
        kw('retrieve_shenick_statistic_result')
        kw('check_if_data_follow_is_zero', case_file('CurrentDetail.zip'))
        gv.kpi.kpi_volte_perm_mos_list.append(gv.kpi.kpi_volte_mos)
        if gv.kpi.kpi_loss_ratio >= 0:
            gv.kpi.kpi_volte_perm_loss_ratio_list.append(gv.kpi.kpi_loss_ratio)
        gv.logger.info(gv.kpi.kpi_volte_perm_mos_list)
        gv.logger.info(gv.kpi.kpi_volte_perm_loss_ratio_list)
    gv.kpi.kpi_volte_perm_loss_ratio = 0

def verify_volte_counter_files():
    kw('generate_report_files')
    kw('download_count_files')

def filter_rtp_packets(pcap_filename='', dst_mac='', rtp_payload = '120'):
    def _get_time(timestamp):
        p = timestamp.split()
        return Decimal(time.mktime(time.strptime("%s %s %s %s" %(p[2].replace('"', ''),
            p[3], p[4], p[5].split('.')[0]), '%b %d, %Y %H:%M:%S'))) + Decimal(float('0.'+p[5].split('.')[-1]))
    tmp_filename = '/tmp/rtp.txt'
    if dst_mac.strip():
        cmd = 'tshark -r %s -d udp.port==1-65535,rtp -Y "eth.dst==%s&&rtp.p_type==%s" -T fields -e rtp.seq -e rtp.p_type -e frame.time -e ip.dst >%s' %(pcap_filename, dst_mac, rtp_payload, tmp_filename)
    else:
        cmd = 'tshark -r %s -d udp.port==1-65535,rtp -Y "rtp.p_type==%s" -T fields -e rtp.seq -e rtp.p_type -e frame.time -e ip.dst >%s' %(pcap_filename, rtp_payload, tmp_filename)
    run_local_command(cmd)
    lines = open(tmp_filename).read()
    caps = []
    sep = '\t'
    for line in lines.splitlines():
        item = IpaMmlItem()
        item.seq            =   line.split(sep)[0]
        item.payload_type   =   line.split(sep)[1]
        item.time           =   _get_time(line)
        item.dstip          =   line.split(sep)[-1]
        item.line           =   line
        caps.append(item)
    return caps

def get_time_differ_for_packets(packets):
    ita = []
    for i in range(len(packets)):
        if i <> 0:
            ita.append(1000.0*float(packets[i].time - packets[i-1].time))
    return ita

def get_plr_for_packets(packets):
    total = int(packets[-1].seq) - int(packets[0].seq) +1
    real_toal = len(packets)
    return float(total - real_toal)*100/float(total)

def rtp_pdv_analysis(ita = [], pctg = 99):
    if len(ita) == 0:
        raise Exception, 'No valid RTP data to analysis'
    import numpy as np
    mean_ita    = float(sum(ita))/len(ita)
    std_ita     = round(np.std(ita), 5)
    ita_99      = round(np.percentile(ita, pctg), 5)
    mean_pdv    = round(std_ita/2, 5)
    pdv_99      = round(ita_99 - mean_ita, 5)
    print 'mean_ita: ', mean_ita, 'std_ita: ', std_ita, 'mean_pdv: ', mean_pdv, 'pdv_99: ', pdv_99
    return mean_pdv, pdv_99


def calc_rtp(pcap_filename, dst_mac):
    caps    = filter_rtp_packets(pcap_filename, dst_mac)
    ita     = get_time_differ_for_packets(caps)
    mean_pdv, pdv_99 = rtp_pdv_analysis(ita)
    plr = round(get_plr_for_packets(caps), 5)
    return mean_pdv, pdv_99, plr

def calc_video_delay(pcap_filename='', dst_ip = ''):
    print 'Pcap file: [%s], dstip: [%s]' %(pcap_filename, dst_ip)
    caps  = filter_rtp_packets(pcap_filename, '', '112')
    print len(caps)
    caps  = [x for x in caps if x.dstip == dst_ip]
    print len(caps)
    seqlist = [x.seq for x in caps]
    seqlist = list(set(seqlist))
    seqlist.sort()
    print len(seqlist)
    timelist = []
    for seq in seqlist:
        caps_seq = [x for x in caps if x.seq == seq]
        # print seq, len(caps_seq)
        if len(caps_seq) == 2:
            timelist.append(abs(caps_seq[0].time - caps_seq[1].time))
    return round(sum(timelist)*Decimal(1000.0)/len(timelist), 5)

#volte performance part

def volte_perm_calc_rtp(pcap_filename):
    dst_mac = '00:1e:6b:03:00:02' if 'ue0' in pcap_filename else '00:1e:6b:03:00:04'
    caps = filter_rtp_packets(pcap_filename, dst_mac, '120')
    print len(caps)
    ita  = get_time_differ_for_packets(caps)
    print max(ita), min(ita)
    index = ita.index(min(ita))
    print index

    print caps[index-2:index+2]



    mean_pdv, pdv_99 = rtp_pdv_analysis(ita)

    pdv_999 = 0
    if gv.case.curr_case.volte_service == 'VIDEO':
        caps = filter_rtp_packets(pcap_filename, dst_mac, '112')
        ita  = get_time_differ_for_packets(caps)
        mean_pdv, pdv_999 = rtp_pdv_analysis(ita, 99.9)

    plr = get_plr_for_packets(caps)
    return mean_pdv, pdv_99, plr, pdv_999

def volte_perm_calc_fine_stat(filename):
    import zipfile
    f = zipfile.ZipFile(filename)
    csvfiles = [x.filename for x in f.filelist if 'cvoip_0000_1.Fine.csv' in x.filename]
    lines = f.read(csvfiles[0]).splitlines()
    title = lines[0].split(',')
    result = []
    for line in lines[1:]:
        value = line.split(',')[title.index('RTP Mean Latency ms')]
        if value <> 'nan':
            result.append(float(value))
    f.close()
    if len(result) == 0:
        return 0
    else:
        return sum(result)/len(result)

def get_ue_ip_address():
    output = kw('wait_until_find_expected_string_in_tm500_output', '60', '1', 'I: CMPI RRC Leave Connected Cell Selection: UE Id:')
    lines = output.splitlines()
    for i in range(len(lines)):
        if 'Pdn Id:1' in lines[i]:
            ueid = lines[i-1].split('UE Id:')[-1]
            ipaddr = lines[i+3].split()[-1].strip()
            if ueid == '0':
                gv.case.curr_case.ue0_ip = ipaddr
            else:
                gv.case.curr_case.ue1_ip = ipaddr
    gv.logger.info('UeID: 0, IP: [%s]' %(gv.case.curr_case.ue0_ip))
    gv.logger.info('UeID: 1, IP: [%s]' %(gv.case.curr_case.ue1_ip))


def wait_until_qci1_is_done():
    output = kw('wait_until_find_expected_string_in_tm500_output', '600', '1', 'I: CMPI MTE 0 NAS BEARER RESOURCE ADD IND:UE Id')
    time.sleep(1)
    output += connections.read_tm500_output()
    attached_uelist = [line for line in output.splitlines() if 'I: CMPI MTE 0 NAS BEARER RESOURCE ADD IND:UE Id' in line]
    if len(attached_uelist) == int(gv.case.curr_case.real_ue_count):
        record_debuginfo('QCI1 completed.')

def check_througput_is_ok():
    time.sleep(5)
    from pet_tm500 import pet_get_running_throughput_from_tm500
    dl_tput, ul_tput = pet_get_running_throughput_from_tm500()
    dl_tput = dl_tput*1024
    gv.logger.info(dl_tput)
    if dl_tput < 48:
        raise Exception, 'Too low download throughput, case will fail!'

def check_tm500_error(fail_keywords):
    output = connections.read_tm500_output()
    for keyword in fail_keywords:
        if keyword.upper() in output.upper():
            raise Exception,'Found [%s] in TM500 output, case will fail' %(keyword)

def pet_capture_volte_perm_packet():
    def _build_command(cmd):
        return 'cli -u %s -p %s  %s' %(gv.tm500.shenick_username, gv.tm500.shenick_partition, cmd)
    conn = connections.connect_to_ssh_host(gv.tm500.shenick_control_ip,
                                           gv.tm500.shenick_control_port,
                                           gv.tm500.shenick_control_username,
                                           gv.tm500.shenick_control_password,
                                           '~$')
    connections.switch_ssh_connection(conn)

    output = ''
    output += connections.execute_ssh_command_without_check(_build_command('pcapFinish'))
    output += connections.execute_ssh_command_without_check('rm -rf /tmp/ue0.pcap')
    output += connections.execute_ssh_command_without_check('rm -rf /tmp/ue1.pcap')
    output += connections.execute_ssh_command_without_check(_build_command('pcapState'))
    output += connections.execute_ssh_command_without_check(_build_command('pcapStart Interface=%s/1/0 NoOfPackets=100000000 DestIpa=%s DurationSec=120 /tmp/ue0.pcap' %(
                                               9+int(gv.tm500.shenick_partition), gv.case.curr_case.ue0_ip)))

    output += connections.execute_ssh_command_without_check(_build_command('pcapStart Interface=%s/1/0 NoOfPackets=100000000 DestIpa=%s DurationSec=120 /tmp/ue1.pcap' %(
                                               9+int(gv.tm500.shenick_partition), gv.case.curr_case.ue1_ip)))

    for i in range(25):
        output += connections.execute_ssh_command_without_check(_build_command('pcapState'))
        time.sleep(5)
    output += connections.execute_ssh_command_without_check(_build_command('pcapStop'))
    output += connections.execute_ssh_command_without_check(_build_command('pcapFinish'))
    connections.disconnect_from_ssh()

    kw('get_file_from_shenick', '/tmp/ue0.pcap', '%s/ue0.pcap' %(gv.case.curr_case.round_dire))
    kw('get_file_from_shenick', '/tmp/ue1.pcap', '%s/ue1.pcap' %(gv.case.curr_case.round_dire))

def get_fine_statistic(sttype = 'Fine'):
    from pet_shenick import execute_command_on_shenick_by_ssh
    cmd1 = 'rm -rf /tmp/finestat.zip'
    cmd2 = 'cli -u %s -p %s saveStats  StatsType=Fine /tmp/finestat.zip' %(gv.tm500.shenick_username, gv.tm500.shenick_partition)
    execute_command_on_shenick_by_ssh([cmd1, cmd2])
    kw('get_file_from_shenick', '/tmp/finestat.zip', '%s/finestat.zip' %(gv.case.curr_case.round_dire))

def calculate_kpi_for_volte_performance():
    mean_pdv, pdv_99, plr, pdv_999 = volte_perm_calc_rtp(os.sep.join([gv.case.curr_case.round_dire, 'ue0.pcap']))
    gv.kpi.kpi_volte_vp_pdv_list.append(mean_pdv)
    gv.kpi.kpi_volte_vp_pdv99_list.append(pdv_99)
    gv.kpi.kpi_volte_vp_plr_list.append(plr)
    gv.kpi.kpi_volte_vp_pdv999_list.append(pdv_999)
    mean_pdv, pdv_99, plr, pdv_999 = volte_perm_calc_rtp(os.sep.join([gv.case.curr_case.round_dire, 'ue1.pcap']))
    gv.kpi.kpi_volte_vp_pdv_list.append(mean_pdv)
    gv.kpi.kpi_volte_vp_pdv99_list.append(pdv_99)
    gv.kpi.kpi_volte_vp_plr_list.append(plr)
    gv.kpi.kpi_volte_vp_pdv999_list.append(pdv_999)

    if gv.case.curr_case.volte_service == 'VIDEO':
        gv.kpi.kpi_volte_vp_pd_list.append(calc_video_delay(os.sep.join([gv.case.curr_case.round_dire, 'ue0.pcap']), gv.case.curr_case.ue0_ip))
        gv.kpi.kpi_volte_vp_pd_list.append(calc_video_delay(os.sep.join([gv.case.curr_case.round_dire, 'ue1.pcap']), gv.case.curr_case.ue1_ip))
    else:
        gv.kpi.kpi_volte_vp_pd_list.append(volte_perm_calc_fine_stat(os.sep.join([gv.case.curr_case.round_dire, 'finestat.zip'])))

    gv.kpi.kpi_volte_vp_pdv     = round(sum(gv.kpi.kpi_volte_vp_pdv_list)/len(gv.kpi.kpi_volte_vp_pdv_list), 5)
    gv.kpi.kpi_volte_vp_pdv_99   = round(sum(gv.kpi.kpi_volte_vp_pdv99_list)/len(gv.kpi.kpi_volte_vp_pdv99_list), 5)
    gv.kpi.kpi_volte_vp_plr     = round(sum(gv.kpi.kpi_volte_vp_plr_list)/len(gv.kpi.kpi_volte_vp_plr_list), 5)
    gv.kpi.kpi_volte_vp_pd      = round(sum(gv.kpi.kpi_volte_vp_pd_list)/len(gv.kpi.kpi_volte_vp_pd_list), 5)
    gv.kpi.kpi_volte_vp_pdv_999 = round(sum(gv.kpi.kpi_volte_vp_pdv999_list)/len(gv.kpi.kpi_volte_vp_pdv999_list), 5) if gv.kpi.kpi_volte_vp_pdv999_list else 0

def do_voip_performance_service(roundid):
    gv.case.curr_case.round = int(roundid)
    gv.case.curr_case.round_dire = case_file('round%s' %(roundid))
    os.makedirs(gv.case.curr_case.round_dire)
    kw('log', 'Round: '+str(gv.case.curr_case.round))
    write_to_console('Round: '+str(gv.case.curr_case.round))
    kw('wait_until_qci1_is_done')
    kw('check_througput_is_ok')
    kw('pet_capture_volte_perm_packet')
    kw('get_fine_statistic')
    check_tm500_error(['Assert'])
    kw('calculate_kpi_for_volte_performance')

def do_mix_volte_service(roundid):
    gv.case.curr_case.round = int(roundid)
    gv.case.curr_case.round_dire = case_file('round%s' %(roundid))
    os.makedirs(gv.case.curr_case.round_dire)
    kw('log', 'Round: '+str(gv.case.curr_case.round))
    write_to_console('Round: '+str(gv.case.curr_case.round))
    kw('capture_packet_for_mix_volte_server')
    kw('calculate_kpi_for_mix_volte_service')

def calculate_kpi_for_mix_volte_service():
    def _parse_qci_plr(i, payload):
        dst_mac = '00:1e:6b:03:00:%02x' %((i+1)*2)
        cap_file = os.sep.join([gv.case.curr_case.round_dire, 'ue%d.pcap' %(i)])
        caps = filter_rtp_packets(cap_file, dst_mac, payload)
        seqs_count = len(list(set([x.seq for x in caps])))
        qciname = 'ue%d_qci%s_plr_list' %(i, payload)
        if not hasattr(gv.kpi, qciname):
            setattr(gv.kpi, qciname, [])
        getattr(gv.kpi, qciname).append(1-float(seqs_count)/float(len(caps)))
        print qciname, getattr(gv.kpi, qciname)

    for i in range(gv.case.curr_case.focus_ue_count):
        _parse_qci_plr(i, '120')
        _parse_qci_plr(i, '112')
    pass


def mix_volte_calc_normal_stat(filename):
    def _get_service_data(filename, fieldname):
        result = []
        lines = f.read([x for x in csvfiles if filename in x.filename][0]).splitlines()
        title = lines[0].split(',')
        for line in lines[1:]:
            if line.strip():
                if str(line.split(',')[title.index('In Service')]) == '1':
                    value = line.split(',')[title.index(fieldname)]
                    if value <> 'nan':
                        result.append(float(value))
        return sum(result)

    import zipfile
    f = zipfile.ZipFile(filename)
    csvfiles = [x for x in f.filelist if 'cvoip_' in x.filename]
    in_result = []
    out_result = []
    plr_result = []
    for i in range(50):
        file1 = 'cvoip_%0.4d_1.Normal.csv' %(10 + i*2)
        file2 = 'cvoip_%0.4d_1.Normal.csv' %(10 + i*2 +1)
        in_result.append(_get_service_data(file1, 'In RTP Packets/s'))
        out_result.append(_get_service_data(file2, 'Out RTP Packets/s'))
        in_result.append(_get_service_data(file2, 'In RTP Packets/s'))
        out_result.append(_get_service_data(file1, 'Out RTP Packets/s'))
    f.close()
    for i in range(len(in_result)):
        plr_result.append((round((out_result[i]-in_result[i])/out_result[i], 4)))

    print in_result
    print out_result
    print len(plr_result)
    print plr_result
    return plr_result


def calculate_final_kpi_for_mix_volte_service():
    pdr_list = mix_volte_calc_normal_stat()
    qci1_list = []
    for i in range(gv.case.curr_case.focus_ue_count):
        payload = '120'
        qciname = 'ue%d_qci%s_plr_list' %(i, payload)
        qci1_list.append(max(getattr(gv.kpi, qciname)))
    print qci1_list
    qci1_list += pdr_list
    gv.kpi.kpi_volte_vp_qci1_plr = sum(qci1_list)/len(qci1_list)

    qci2_list = []
    for i in range(gv.case.curr_case.focus_ue_count):
        payload = '112'
        qciname = 'ue%d_qci%s_plr_list' %(i, payload)
        qci2_list.append(max(getattr(gv.kpi, qciname)))
    print qci2_list
    gv.kpi.kpi_volte_vp_qci2_plr = sum(qci2_list)/len(qci2_list)

def repeat_to_do_voip_call_for_specific_time(times):
    kw('pet_ue_attach_for_volte')
    kw('get_ue_ip_address')
    gv.kpi.kpi_volte_vp_plr_list = []
    gv.kpi.kpi_volte_vp_pd_list = []
    gv.kpi.kpi_volte_vp_pdv_list = []
    gv.kpi.kpi_volte_vp_pdv99_list = []
    gv.kpi.kpi_volte_vp_pdv999_list = []
    times = 1 if gv.debug_mode in ['DEBUG'] else times
    for i in range(int(times)):
        kw('do_voip_performance_service', i+1)


def _get_time(timestamp):
    p = timestamp.split()
    print  p[2].replace('"', ''), p[3], p[4], p[5].split('.')[0]
    t1 = time.mktime(time.strptime("%s %s %s %s" %(p[2].replace('"', ''),
        p[3], p[4], p[5].split('.')[0]), '%b %d, %Y %H:%M:%S'))
    # print t1
    # print 'p5  ', float('0.'+p[5].split('.')[-1])
    # print p[5][7:]
    # t2 = float(p[5][7:])
    t2 = float('0.'+p[5].split('.')[-1])
    return Decimal(t1 + t2)

if __name__ == '__main__':
    # gv.logger.info('Start')
    # calc_rtp('/home/work/temp/rtp.pcap', '00:1e:6b:03:00:02')
    # print volte_perm_calc_rtp('/home/work/temp/rtp.pcap', '00:1e:6b:03:00:02')
    # print calc_video_delay('/home/work/Jenkins2/workspace/JH_TL17SP_VOLTE/11/472728_2017_06_03__00_09_42/472728_[1]20_01_0/round1/ue0.pcap', '172.25.5.200')

    # print volte_perm_calc_rtp('/home/work/Jenkins2/workspace/JH_TL17SP_VOLTE/61/472728_2017_07_03__14_24_11/472728_[1]20_01_0/round10/ue1.pcap')
    calc_video_delay('/home/work/Jenkins2/workspace/JH_TL17SP_VOLTE/62/472728_2017_07_03__15_55_18/472728_[1]20_01_0/round6/ue1.pcap', '172.25.8.230')
    # timestamp = '4416       120     "Jul  3, 2017 14:35:49.983951000 CST"   172.25.3.45'
    # print timestamp
    # print _get_time(timestamp)

    # timestamp = '4417       120     "Jul  3, 2017 14:35:50.003858000 CST"   172.25.3.45'
    # print timestamp
    # print _get_time(timestamp)


    # from pettool import get_case_config_new
    # gv.case = IpaMmlItem()
    # gv.case.curr_case = IpaMmlItem()
    # gv.case.curr_case = get_case_config_new('555596')
    # # gv.case.curr_case.volte_service='VIDEO'
    # # gv.case.curr_case.real_ue_count = 100
    # gv.case.log_directory = '/tmp'
    # # print volte_perm_calc_rtp('/home/work/Jenkins2/workspace/JH_TL17SP_VOLTE/57/472728_2017_06_30__00_03_24/472728_[1]20_01_0/round7/ue0.pcap')
    # # print calc_video_delay('/home/work/Jenkins2/workspace/JH_TL17SP_VOLTE/60/472728_2017_07_02__23_50_18/472728_[1]20_01_0/round1/ue0.pcap', '172.25.6.253')
    # # mix_volte_calc_normal_stat('/home/work/temp/5/finestat.zip')
    # # gv.logger.info('analysis done')
    # # print volte_perm_calc_fine_stat('/home/work/temp/a.zip')
    # zipfile = '/home/work/Jenkins2/workspace/JH_TL17SP_VOLTE_CAP/12/555596_2017_07_02__00_04_26/555596_[1]SPEECH_/CurrentDetail.zip'
    # deal_with_voip_result_file(zipfile)
    pass
