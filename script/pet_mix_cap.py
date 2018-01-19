import datetime, os, time, re
from petbase import *
import pettool
from thread import *
from pet_tm500 import execute_tm500_cmd_and_save_log
import pet_ixia

bts_error_log_keywords_for_cap = ['ERR/']

def common_suite_setup_for_mix_cap():
    kw('common_suite_setup_for_pet')

def common_suite_teardown_for_mix_cap():
    kw('common_suite_teardown_for_pet')

def common_test_case_setup_for_mix_cap():
    gv.master_bts.bts_error_log_keywords = bts_error_log_keywords_for_cap
    kw('common_test_case_setup_for_pet')
    if gv.case.curr_case.ue_is_volte:
        gv.env.use_ixia = False
        gv.env.use_catapult = False
    if gv.env.use_ixia:
        kw('ixia_setup')
    kw('tm500_case_setup')
    gv.tm500.tm500_cmd_output_file = case_file('tm500_cmd.log')

def common_test_case_teardown_for_mix_cap():
    gv.case.done = True
    kw('save_bts_error_log')
    kw('stop_tti_parser')
    kw('run_keyword_and_ignore_error', 'stop_running_test_group')
    kw('run_keyword_and_ignore_error', 'clear_mts')
    kw('run_keyword_and_ignore_error', 'tm500_case_teardown')
    if gv.tm500:
        kw('run_keyword_and_ignore_error', 'pet_release_tm500_resource')
    kw('common_test_case_teardown_for_pet')
    pass

def save_bts_error_log():
    with open(case_file('bts_errorlog.log'), 'a') as f:
        for line in gv.master_bts.error_log_list:
            f.write(line + '\n')

def start_tti_praser_for_bts(btsid=''):
    from pet_bts import _get_bts
    bts = _get_bts(btsid)
    bts.tti_result_dire = case_file('tti_' + bts.bts_id)
    os.makedirs(bts.tti_result_dire)
    kw('start_tti_trace2', bts.bts_id)
    fdstr = 'Y' if gv.case.curr_case.fd_20ue else 'N'
    parselog = os.sep.join([bts.tti_result_dire, 'parselog.log'])
    cmd = 'python %s/tti_parser.py -d %s -t %s -c %s -b %s -f %s -r %s -m %s >%s &' %(resource_path(),
                      bts.tti_result_dire,  bts.tti.ttiparser, ','.join(bts.internal_cellid_list),
                      ','.join(gv.case.curr_case.band.replace('M', '').split('-')),
                      fdstr, bts.tti.core_info, bts.btstype, parselog)
    gv.logger.info(cmd)
    run_local_command(cmd)


def pet_cap_start_tti_monitoring():
    for bts in gv.mbts():
        start_tti_praser_for_bts(bts.btsid)

def wait_until_all_tti_parsed():
    time.sleep(10)

def common_check_for_mix_cap_should_be_ok():
    kw('common_check_for_pet_should_be_ok')

def common_check_for_mix_sta_should_be_ok():
    kw('common_check_for_pet_should_be_ok')
    for bts in gv.mbts():
        try:
            kw('bts_is_onair_by_infomodel', bts.btsid)
            return 0
        except:
            kw('report_error', 'BTS is not onAir by checking Infomodel')

def pet_ue_attach_for_mix_cap_service():
    kw('run_keyword_and_ignore_error', 'stop_running_test_group')
    kw('pet_connect_to_tma')
    from pet_tm500_script import get_mix_cap_script
    lines = get_mix_cap_script(gv.master_bts)
    lines = [line.replace('\n', '') for line in lines if not re.match('(^(\r|\n|\s+)$)|(^$)|^#', line)] # remove all the unnecessary lines including comment
    save_log(lines, case_file('real_attach.txt'), 'N')
    save_log(lines, gv.tm500.tm500_cmd_output_file)

    output = ''
    fail_keywords = ['FAILURE', 'ERROR', 'Assert', 'DELETE']
    time.sleep(20)
    gv.logger.info('WAIT FOR CMD EXECUTE!!')
    for line in lines:
        output = execute_tm500_cmd_and_save_log(line)
        errorlines = contain_keywords(output, fail_keywords)
        #time.sleep(0.2)
        if len(errorlines) > 0:
            kw('log', 'Found eror: ' + ';'.join(errorlines))
            kw('report_error', 'Found failure in TM500 output [%s].' %(errorlines[0]))
    record_tm500log(output)

def check_tti_result():
    listmap = {
    'kpi_sf_dl_list': 'Download Special Frame numUesFd ratio',
    'kpi_nf_dl_list': 'Download Normal  Frame numUesFd ratio',
    'kpi_nf_ul_list': 'Upload   Normal  Frame numUesFd ratio',
    }

    def _get_check_range(alist):
        dropcount = 6
        if len(alist) <=dropcount:
            return []
        else:
            return alist[dropcount-1:-1]
    def check_list(cell, listname, target):
        gv.logger.info('%s    %s:   %s%%' %(cell.name, listmap[listname],
            str(getattr(cell, listname)).replace('[', '').replace(']','')))
        result = _get_check_range(getattr(cell, listname))
        if result:
            if float(result[-1]) < float(target):
                kwg('report_error', 'TTI Trace check fail: %s %s %0.2f%% vs %0.2f%% ' %(cell.name, listname, float(result[-1]), float(target)))
    for bts in gv.mbts():
        gv.logger.info('Check Tti Result In')
        case = gv.case.curr_case  
        bts.tti_result_dire = case_file('tti_' + bts.bts_id)  
        result_file = os.sep.join([bts.tti_result_dire, 'tti_result.log'])
        gv.logger.info('tti result file:%s' %(result_file))
        if not os.path.exists(result_file):
            gv.logger.info('tti result file is not exist!')
            return 0
        lines = open(result_file).readlines()[1:]
        result = []
        for line in lines:
            item = IpaMmlItem()
            item.direction, item.cellid, item.sf, item.nf = line.split(',')[0],line.split(',')[1],line.split(',')[2],line.split(',')[3]
            result.append(item)
        bts.ttiresult = IpaMmlItem()
        bts.ttiresult.pcell = IpaMmlItem()
        pcellid = bts.internal_cellid_list[0]
        bts.ttiresult.pcell.name = 'PCELL'
        bts.ttiresult.pcell.kpi_sf_dl_list = [float(item.sf) for item in result if item.direction == 'DL' and item.cellid == pcellid]
        bts.ttiresult.pcell.kpi_nf_dl_list = [float(item.nf) for item in result if item.direction == 'DL' and item.cellid == pcellid]
        bts.ttiresult.pcell.kpi_nf_ul_list = [float(item.nf) for item in result if item.direction == 'UL' and item.cellid == pcellid]
        #gv.logger.info('pcell.kpi_sf_dl_list=%s pcell.kpi_nf_dl_list=%s pcell.kpi_nf_ul_list=%s' %(bts.ttiresult.pcell.kpi_sf_dl_list,bts.ttiresult.pcell.kpi_nf_dl_list,bts.ttiresult.pcell.kpi_nf_ul_list))
        check_list(bts.ttiresult.pcell, 'kpi_sf_dl_list', case.pcell_target_dl)
        check_list(bts.ttiresult.pcell, 'kpi_nf_dl_list', case.pcell_target_dl)
        check_list(bts.ttiresult.pcell, 'kpi_nf_ul_list', case.pcell_target_ul)
        if gv.case.curr_case.ca_type in ['2CC', '3CC']:
            bts.ttiresult.scell = IpaMmlItem()
            scellid = bts.internal_cellid_list[1]
            bts.ttiresult.scell.name = 'SCELL'
            bts.ttiresult.scell.kpi_sf_dl_list = [float(item.sf) for item in result if item.direction == 'DL' and item.cellid == scellid]
            bts.ttiresult.scell.kpi_nf_dl_list = [float(item.nf) for item in result if item.direction == 'DL' and item.cellid == scellid]
            bts.ttiresult.scell.kpi_nf_ul_list = [float(item.nf) for item in result if item.direction == 'UL' and item.cellid == scellid]
            #gv.logger.info('scell.kpi_sf_dl_list=%s scell.kpi_nf_dl_list=%s scell.kpi_nf_ul_list=%s' %(bts.ttiresult.scell.kpi_sf_dl_list,bts.ttiresult.scell.kpi_nf_dl_list,bts.ttiresult.scell.kpi_nf_ul_list))
            check_list(bts.ttiresult.scell, 'kpi_sf_dl_list', case.scell_target_dl)
            check_list(bts.ttiresult.scell, 'kpi_nf_dl_list', case.scell_target_dl)
            check_list(bts.ttiresult.scell, 'kpi_nf_ul_list', case.scell_target_ul)

def get_running_throughput():
    kw('pet_connect_to_tma')
    output = execute_tm500_cmd_and_save_log('forw MTE GETSTATS [0] [combined] [combined]')
    gv.logger.info('output=%s' %(output))
    result_tmp = str(re.findall(r".*DL-SCH(.*?)UL-SCH.*", output, re.S))
    gv.logger.info('result_tmp=%s' %(result_tmp))
    if result_tmp == []:
        kwg('report_error', 'Query running throughput fail!')
        return 0
    result = round(int((re.findall(r".*THROUGHPUT\:\s+(\d+)\s+AVERAGE.*", result_tmp, re.S)[0]))/(1024*1024), 2)
    gv.logger.info('Current RUNNING DL Throughput is %0.2f' %(result))
    return result

def pet_override_pmi_parameter(ue_count, pmi_override, radio_context):
    kw('pet_connect_to_tma')
    result = []
    for ue_id in range(ue_count):
        result.append('forw mte SetUEContext %s' %(ue_id))
        for context in radio_context:
            result.append('forw mte PhyOverrideCqi 2(%s((1{15 15}) ) []) [%s]' %(pmi_override,context))
    for line in result:
        execute_tm500_cmd_and_save_log(line)

def adjust_pmi_override_parameter():
    kw('pet_connect_to_tma')
    target = float(''.join(re.findall(r".*kpi_dl_tput:(.*);kpi_ul_tput.*", gv.case.curr_case.kpi, re.S)))
    gv.logger.info('pet_override dl throughput target is %.2f' %(target))

    if get_running_throughput() >= target*0.9:
        return 0

    for pmi in range(1, 16):
        gv.logger.info('Try PIM Override parameter %s' %(pmi))
        radio_context = [0, 1] if gv.case.curr_case.ca_type in ['2CC','3CC'] else [0]
        pet_override_pmi_parameter(int(gv.case.curr_case.ue_count), pmi, radio_context)
        time.sleep(5)
        if get_running_throughput() >= target*0.9:
            return 0
    kw('report_error', 'TA tried all PMI parameter and throughput is too low.')

def wait_until_cap_service_is_done():
    import time
    if gv.tm500.tm500_id == '0':
        if gv.case.curr_case.has_cap_volte:
            test_group = '//'+ gv.tm500.shenick_volte_group_name
        else:
            test_group = '//'+ gv.tm500.shenick_group_name
        gv.logger.info('start_test_group by manual, groupname:{}, '.format(test_group))
        kw('start_test_group', test_group)

    if gv.env.use_ixia:
        kw('pet_ixia_start')
        time.sleep(90)

    '''if gv.case.curr_case.tm == '4X2' and not gv.case.curr_case.has_cap_volte:
        kw('adjust_pmi_override_parameter')'''

    for bts in gv.mbts():
        if gv.case.curr_case.check_tti:
            start_tti_praser_for_bts(bts.btsid)
        bts.monitor_error_log = True
        bts.btslog_monitor_start = time.time()
    from robot.utils import timestr_to_secs
    timeout = gv.case.curr_case.case_duration if gv.case.curr_case.case_duration else '10mins'
    timeout = '10mins' if gv.debug_mode <> 'RUN' else timeout
    fail_keywords = ['Assert']
    #fail_keywords = ['FAILURE', 'ERROR', 'LEAVE', 'DISCONNECTION', 'Assert']
    #fail_keywords = ['FAILURE', 'ERROR', 'LEAVE', 'DISCONNECTION', 'Assert','RRC Leave Connected Cell']
    total_time = timestr_to_secs(timeout)
    try:
        write_to_console('Start MIX CAP Service...')
        kw('pet_connect_to_tma')
        output = ''
        start_time = time.time()
        while time.time() < start_time + total_time:
            check_btslog_fatal()
            if gv.case.curr_case.check_tti:
                check_tti_result()
            ret = connections.read_tm500_output()
            if ret.strip():
                output += ret
                errorlines = contain_keywords(ret, fail_keywords)
                if len(errorlines) > 0:
                    kw('log', 'Unexpected Error info: ' + ';'.join(errorlines))
                    record_debuginfo(output)
                    kw('report_error', 'Found failure in TM500 output [%s].' %(ret))
                    break
            time.sleep(30)
            gv.logger.info('Still need wait for : %d seconds.' %((start_time + total_time - time.time())))
        for bts in gv.mbts():
            bts.btslog_monitor_end = time.time()
        if gv.case.curr_case.check_tti:
            calcu_mix_cap_kpi()
    finally:
        gv.case.service_done = True
        for bts in gv.mbts():
            bts.monitor_error_log = False
            bts.conn_bts = None
    kw('wait_until_all_tti_parsed')

def wait_until_mix_sta_is_done():
    import time
    if gv.env.use_ixia:
        kw('pet_ixia_start')
        time.sleep(90)

    for bts in gv.mbts():
        if gv.case.curr_case.check_tti:
            start_tti_praser_for_bts(bts.btsid)
        bts.monitor_error_log = True
        bts.btslog_monitor_start = time.time()
    from robot.utils import timestr_to_secs
    kw('pet_start_tm500_logging_2')
    time.sleep(300)
    kw('stop_tm500_logging_and_download_logs_2', 'tmftpul')
    timeout = gv.case.curr_case.case_duration if gv.case.curr_case.case_duration else '10mins'
    timeout = '10mins' if gv.debug_mode <> 'RUN' else timeout
    fail_keywords = ['Assert']
    #fail_keywords = ['FAILURE', 'ERROR', 'LEAVE', 'DISCONNECTION', 'Assert']
    #fail_keywords = ['FAILURE', 'ERROR', 'LEAVE', 'DISCONNECTION', 'Assert','RRC Leave Connected Cell']
    total_time = timestr_to_secs(timeout)
    try:
        write_to_console('Start MIX CAP Service...')
        kw('pet_connect_to_tma')
        output = ''
        start_time = time.time()
        while time.time() < start_time + total_time:
            check_btslog_fatal()
            if gv.case.curr_case.check_tti:
                check_tti_result()
            ret = connections.read_tm500_output()
            if ret.strip():
                output += ret
                errorlines = contain_keywords(ret, fail_keywords)
                if len(errorlines) > 0:
                    kw('log', 'Unexpected Error info: ' + ';'.join(errorlines))
                    record_debuginfo(output)
                    kw('report_error', 'Found failure in TM500 output [%s].' %(ret))
                    break
            time.sleep(30)
            gv.logger.info('Still need wait for : %d seconds.' %((start_time + total_time - time.time())))
        for bts in gv.mbts():
            bts.btslog_monitor_end = time.time()
        if gv.case.curr_case.check_tti:
            calcu_mix_cap_kpi()
    finally:
        gv.case.service_done = True
        for bts in gv.mbts():
            bts.monitor_error_log = False
            bts.conn_bts = None
    kw('wait_until_all_tti_parsed')

def wait_get_and_deal_voip_result():
    if not gv.case.curr_case.has_cap_volte:
        print 'Is not have volte'
        return 0
    print '%%wait_get_and_deal_voip_result have volte%%'
    print gv.tm500.shenick_volte_group_name
    gv.kpi.kpi_volte_perm_mos_list = []
    kw('get_shenick_test_group_detail_result', gv.tm500.shenick_volte_group_name, case_file('CurrentDetail.zip'))
    kw('deal_with_voip_result_file', case_file('CurrentDetail.zip'))
    #kw('check_if_data_follow_is_zero', case_file('CurrentDetail.zip'))
    gv.kpi.kpi_volte_perm_mos_list.append(gv.kpi.kpi_volte_mos)

def stop_tti_parser():
    pidlist = [x.split()[1] for x in os.popen('ps -ef|grep tti_parser.py |grep %s' %(gv.case.log_directory )).readlines()]
    for pid in pidlist:
        run_local_command('kill -9 ' + pid)

def calcu_mix_cap_kpi():
    def _last_value(alist):
        if len(alist) >= 2:
            return alist[-2]
        else:
            return 0
    for bts in gv.mbts():
        if bts.btstype == 'FDD':
            return 0
        gv.kpi.kpi_pcell_dl_sf_fd = _last_value(bts.ttiresult.pcell.kpi_sf_dl_list)
        gv.kpi.kpi_pcell_dl_nf_fd = _last_value(bts.ttiresult.pcell.kpi_nf_dl_list)
        gv.kpi.kpi_pcell_ul_nf_fd = _last_value(bts.ttiresult.pcell.kpi_nf_ul_list)
        if gv.case.curr_case.ca_type in ['2CC', '3CC']:
            gv.kpi.kpi_scell_dl_sf_fd = _last_value(bts.ttiresult.scell.kpi_sf_dl_list)
            gv.kpi.kpi_scell_dl_nf_fd = _last_value(bts.ttiresult.scell.kpi_nf_dl_list)
            gv.kpi.kpi_scell_ul_nf_fd = _last_value(bts.ttiresult.scell.kpi_nf_ul_list)

if __name__ == '__main__':
    # case = IpaMmlItem()
    # case.fd_20ue = 'N'
    # case.band = '20'
    # # csvfile = '/home/work/temp/3/tti_dl.csv'
    # path = '/home/work/jrun/TL17PET2_CAP_00140_20M_ULDL1_SSF7_TM3_2PIPE_CAP__2016_09_28__16_00_28/FD20UE_NO1'
    # csvfile = '/home/work/temp/4/dl.csv'
    # csvfile = os.sep.join([path, 'TtiTrace_20160928080450_1233_ul_a.csv'])

    # bts = IpaMmlItem()
    # bts.internal_cellid_list=['110']
    # # print calc_ul_tti_kpi(csvfile, case, bts)
    # csvfile = os.sep.join([path, 'TtiTrace_20160928080450_1232_dl_a.csv'])
    # print calc_dl_tti_kpi(csvfile, case, bts)
    pass
