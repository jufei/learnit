import datetime, os, time
from petbase import *
import pettool

from pet_tm500 import execute_tm500_cmd_and_save_log

def common_suite_setup_for_mr():
    kw('common_suite_setup_for_pet')

def common_suite_teardown_for_mr():
    kw('common_suite_teardown_for_pet')

def common_test_case_setup_for_mr():
    kw('common_test_case_setup_for_pet')
    kw('select_datadevice')
    kw('tm500_case_setup')
    gv.tm500.tm500_cmd_output_file = case_file('tm500_cmd.log')

def common_test_case_teardown_for_mr():
    kw('run_keyword_and_ignore_error', 'stop_running_test_group')
    kw('run_keyword_and_ignore_error', 'clear_mts')
    kw('run_keyword_and_ignore_error', 'tm500_case_teardown')
    if gv.tm500:
        kw('run_keyword_and_ignore_error', 'pet_release_tm500_resource')
    kw('common_test_case_teardown_for_pet')
    pass

def common_check_for_mr_should_be_ok():
    kw('common_check_for_pet_should_be_ok')

def pet_ue_attach_for_mix_mr_service():
    kw('run_keyword_and_ignore_error', 'stop_running_test_group')
    kw('pet_connect_to_tma')
    from pet_tm500_script import get_mr_mix_script
    lines = get_mr_mix_script(gv.master_bts, gv.slave_bts)
    lines = [line.replace('\n', '') for line in lines if not re.match('(^(\r|\n|\s+)$)|(^$)|^#', line)] # remove all the unnecessary lines including comment
    save_log(lines, case_file('real_attach.txt'), 'N')
    save_log(lines, gv.tm500.tm500_cmd_output_file)

    output = ''
    fail_keywords = ['FAILURE', 'ERROR', 'Assert', 'DELETE']

    for line in lines:
        output = execute_tm500_cmd_and_save_log(line)
        errorlines = contain_keywords(output, fail_keywords)
        if len(errorlines) > 0:
            kw('log', 'Found eror: ' + ';'.join(errorlines))
            kw('report_error', 'Found failure in TM500 output [%s].' %(errorlines[0]))
    record_tm500log(output)

def wait_until_mr_service_is_done():
    from robot.utils import timestr_to_secs
    timeout = int(gv.case.curr_case.case_duration) + 100 if gv.case.curr_case.case_duration else 300
    timeout = 300 if gv.debug_mode <> 'RUN' and timeout>100 else timeout
    fail_keywords = ['FAILURE', 'ERROR', 'NAS DELETE', 'NAS: Registraton failure', 'ASSERTED']
    fail_keywords = ['ASSERTED']
    exception_keywords = ['FAILURE', 'ERROR', 'NAS DELETE', 'NAS: Registraton failure']
    except_keywords = ['[Procedure]']
    interval = 10
    gv.kpi.kpi_case_duration = int(gv.case.curr_case.case_duration)/60

    try:
        gv.tm500.radio_card_count = open(case_file('tm500cmd.log')).read().upper().count('C: SELR 0x00 Ok'.upper())
        gv.logger.info('Total radio card: %d' %(radio_card_count))
    except:
        gv.tm500.radio_card_count = 0
        gv.logger.info('Have not found the radio card, check the tm500cmd.log please.')

    from pet_tm500 import pet_connect_to_tma

    try:
        write_to_console('Start Manual Rate Service...')
        pet_connect_to_tma()
        start_time = time.time()
        total_time = timestr_to_secs(timeout)
        count = 0
        output = ''
        while time.time() < start_time + total_time:
            check_btslog_fatal()
            ret = execute_tm500_cmd_and_save_log()
            if ret.strip():
                errorlines = contain_keywords(ret, fail_keywords, except_keywords)
                if len(errorlines) > 0:
                    kw('log', 'Found unexpected eror: ' + ';'.join(errorlines))
                    kw('report_error', 'Found failure in TM500 output [%s].' %(errorlines[0]))

                f_ueid = ''
                errorlines = contain_keywords(ret, exception_keywords, except_keywords)
                if len(errorlines) > 0:
                    if 'UE Id:' in errorlines[0]:
                        f_ueid = errorlines[0].split('UE Id:')[1].split()[0]
                    cmdstr = 'forw mte getstats [6] [%s]' %(f_ueid) if f_ueid else 'forw mte getstats [6]'
                    execute_tm500_cmd_and_save_log(cmd=cmdstr, timeout='1', ignore_log='Y')
            time.sleep(0.1)
            count += 1
            if count >= 1000:
                ret = connections.read_tm500_output(1)
                save_log(ret.splitlines(), gv.tm500.tm500_cmd_output_file)
                ratios = get_statistic_info_for_mr_service(False)
                for kpiname in ratios:
                    if ratios[kpiname] < 80:
                        kw('report_error', 'Current KPI: %s is %0.2f, is lower than 80, case failed.' %(kpiname, ratios[kpiname]))
                gv.logger.info('Still need wait for : %d seconds.' %((start_time + total_time - time.time())))
                count = 0
        # ret = connections.execute_tm500_command_without_check('forw mte mtspausemts', ignore_output = 'Y')
        # ret += connections.read_tm500_output(10)
        save_log(ret.splitlines(), gv.tm500.tm500_cmd_output_file)
    finally:
        gv.master_bts.conn_bts = None

def calc_mr_caps():
    gv.kpi.kpi_cap = 10000
    case = gv.case.curr_case
    if case.real_paging_ue_count:
        gv.kpi.kpi_cap = min(gv.kpi.kpi_cap, int(1000/int(case.paging_stagger)))
    if case.real_cd_ue_count:
        gv.kpi.kpi_cap = min(gv.kpi.kpi_cap, int(1000/int(case.cd_stagger)))
    if case.real_ho_ue_count:
        gv.kpi.kpi_cap = min(gv.kpi.kpi_cap, int(1000/int(case.ho_stagger)))
    if case.real_volte_ue_count:
        gv.kpi.kpi_cap = min(gv.kpi.kpi_cap, int(1000/int(case.mr_volte_stagger)))
    if case.real_ho_volte:
        gv.kpi.kpi_cap = min(gv.kpi.kpi_cap, int(1000/int(case.mr_volte_ho_stagger)))

def get_statistic_info_for_mr_service(final = True):
    def _get_nas_statistic(nasstr):
        return [int(x) for x in nasstr.split()[1:]][:3]

    def _get_rrc_statistic(nasstr):
        return [int(x) for x in nasstr.split()[1:]][:2]

    def _get_case_attr(attrname):
        if str(getattr(gv.case.curr_case, attrname)).strip():
            return int(getattr(gv.case.curr_case, attrname))
        return 0

    def analysis_kpi(output, kpitype, search_kw, show_kw, kpiname):
        result = [x for x in output.splitlines() if search_kw in x]
        if not result:
            kw('report_error', 'Could not find %s result in TM500 output.' %(show_kw))
        else:
            gv.logger.info(result[0])
            if kpitype == 'NAS':
                count, retry, success = _get_nas_statistic(result[0])
            else:
                count, success = _get_rrc_statistic(result[0])
            if count == 0:
                kw('report_error', 'The %s Count is 0, it is un-reasonable!' %(show_kw))
            else:
                setattr(gv.kpi, kpiname, 100*float(success)/count)
            print count, success
            return count, success

    def check_count(count, exp_value, cstr):
        if gv.debug_mode in ['DEBUG', 'DEV'] or not gv.case.curr_case.mr_check_l3_stat:
            return 0
        min_times = int(exp_value)*int(gv.case.curr_case.case_duration)/3600
        # min_times = int(float(exp_value)*(float(gv.case.curr_case.case_duration)/3600))
        if final:
            if count <= min_times:
                kw('report_error', '[%s] has not reached the min times: %d' %(cstr, min_times))

    paging_count   = _get_case_attr('mr_paging_ue_count') + _get_case_attr('mr_paging_impair_ue_count')
    cd_count       = _get_case_attr('mr_call_drop_ue_count') + _get_case_attr('mr_cd_impair_ue_count')
    ho_count       = _get_case_attr('mr_intra_ho_ue_count') + _get_case_attr('mr_ho_impair_ue_count')
    volte_count    = _get_case_attr('mr_volte_ue_count') + _get_case_attr('mr_volte_impair_ue_count')
    volte_ho_count = _get_case_attr('mr_volte_ho_ue_count') + _get_case_attr('mr_volte_ho_impair_ue_count')

    from pet_tm500 import pet_connect_to_tma
    pet_connect_to_tma()
    result = {}
    cmd_timeout = '10'

    if final:
        calc_mr_caps()
        kw('stop_mts_gracefully')
        kw('wait_until_new_pmcount_file_generated', gv.master_bts.bts_id)
        kw('counter_kpi_should_be_correct')

    output_rrc = execute_tm500_cmd_and_save_log('forw mte GetRRCStats', cmd_timeout, 'MEASUREMENT_REPORT')
    lines = [x for x in output_rrc.splitlines() if 'PAGING     ' in x]
    if not lines:
        gv.logger.info('**********************************')
        gv.logger.info('\n'.join(lines))
        gv.logger.info('**********************************')
        kw('report_error', 'Could not find Paging Request result in TM500 output.')
    else:
        stat_paging_count = int(lines[0].split()[1])

    case = gv.case.curr_case
    from pet_counter import get_counter_value

    if ho_count > 0 or volte_ho_count > 0:
        count, success = analysis_kpi(output_rrc, 'RRC', 'HANDOVER          ', 'Handover', 'kpi_handover_ratio')
        result['kpi_handover_ratio'] = gv.kpi.kpi_handover_ratio
        check_count(count, case.real_ho_ue_count * 55 + case.real_ho_volte * 30, 'HANDOVER')

        if final:
            cname = ''
            if case.ho_type.upper() == 'INTRA' and not case.different_frequency:
                cname = 'LTE_5035a/E-UTRAN HO Success Ratio, intra eNB'
            if case.ho_type.upper() == 'INTER' and\
                    case.ho_path.strip().upper() == 'X2' and\
                    not case.different_frequency:
                cname = 'LTE_5048b/E-UTRAN HO Success Ratio, Inter eNB X2 based'
            if case.ho_type.upper() == 'INTER' and\
                    case.ho_path.strip().upper() == 'S1' and\
                    not case.different_frequency:
                cname = 'LTE_5084b/E-UTRAN Total HO Success Ratio, inter eNB S1 based'
            if case.different_frequency:
                cname = 'LTE_5114a/E-UTRAN Inter-Frequency HO Success Ratio'
            if cname:
                gv.kpi.kpi_handover_ratio = get_counter_value(cname)
            else:
                kw('report_error', 'Counter is invalud to calculate the kpi_handover_ratio')

    if paging_count:
        output = execute_tm500_cmd_and_save_log('forw mte GetNASStats', cmd_timeout, 'NW_DEACTIVATE_BEARER')
        service_req_count, sevice_req_success = analysis_kpi(output, 'NAS', 'SERVICE_REQ_MT', 'Service Request', 'kpi_service_rt_mt_ratio')
        setattr(gv.kpi, 'kpi_paging_ratio', 100*float(service_req_count)/int(stat_paging_count))
        check_count(service_req_count, case.real_paging_ue_count * 65, 'SERVICE_REQ_MT')

        if final:
            gv.kpi.kpi_service_rt_mt_ratio = 100 - get_counter_value('LTE_5031b/E-UTRAN RRC Paging Discard Ratio')

    if cd_count:
        output = execute_tm500_cmd_and_save_log('forw mte GetNASStats', cmd_timeout, 'NW_DEACTIVATE_BEARER')
        attach_count, attach_success = analysis_kpi(output, 'NAS', 'ATTACH                         ', 'Attach', 'kpi_attach_ratio')
        result['kpi_attach_ratio'] = gv.kpi.kpi_attach_ratio
        analysis_kpi(output, 'NAS', 'PDN_CONNECTIVITY               ', 'Attach', 'kpi_erab_ratio')
        result['kpi_erab_ratio'] = gv.kpi.kpi_erab_ratio

        rrc_connect_count, rrc_connect_success = analysis_kpi(output_rrc, 'RRC', 'RRC_CONNECTION_REQUEST           ',
            'RRC Paging count', 'kpi_rrc_ratio')
        result['kpi_rrc_ratio'] = gv.kpi.kpi_rrc_ratio
        check_count(attach_count, case.real_cd_ue_count * 35, 'ATTACH')

        if final:
            gv.kpi.kpi_attach_ratio = 100 - get_counter_value('LTE_5004d/E-UTRAN Radio Bearer Drop Ratio')
            gv.kpi.kpi_erab_ratio = get_counter_value('LTE_5003a/E-UTRAN Data Radio Bearer Setup Success Ratio')
            gv.kpi.kpi_rrc_ratio = get_counter_value('LTE_5218f/Total E-UTRAN RRC Connection Setup Success Ratio')

    if volte_count:
        output = execute_tm500_cmd_and_save_log('forw mte GetNASStats', cmd_timeout, 'NW_DEACTIVATE_BEARER')
        c_volte_count, volte_success = analysis_kpi(output, 'NAS', 'NW_ACTIVATE_DEDICATED_BEARER', 'NW_ACTIVATE_DEDICATED_BEARER', 'kpi_qci1_ratio')
        if int(c_volte_count) < int(volte_count*0.8):
            kw('report_error', 'Volte UE count failed, [%s] vs [%s] ' %(c_volte_count, volte_count))
        check_count(c_volte_count, case.real_volte_ue_count * 15, 'NW_ACTIVATE_DEDICATED_BEARER')
        if final:
            gv.kpi.kpi_qci1_ratio = get_counter_value('LTE_5204c/E-UTRAN E-RAB Setup Success Ratio, QCI1')

    if volte_ho_count:
        count, success = analysis_kpi(output_rrc, 'RRC', 'HANDOVER          ', 'Handover', 'kpi_handover_ratio')
        check_count(count, case.real_ho_ue_count * 55 + case.real_ho_volte * 30, 'HANDOVER')

        output = execute_tm500_cmd_and_save_log('forw mte GetNASStats', cmd_timeout, 'NW_DEACTIVATE_BEARER')
        c_volte_ho_count, volte_success = analysis_kpi(output, 'NAS', 'NW_ACTIVATE_DEDICATED_BEARER', 'NW_ACTIVATE_DEDICATED_BEARER', 'kpi_volte_ho_ratio')
        if int(c_volte_ho_count) < int(volte_ho_count*0.8):
            kw('report_error', 'Handover failed, [%s] vs [%s] ' %(c_volte_count, volte_count))

        if final:
            cname = ''
            if case.is_df:
                cname = 'LTE_5884a/E-UTRAN Inter-Frequency HO Success Ratio for QCI1'
            elif case.is_s1:
                cname = 'LTE_5882a/E-UTRAN HO Success Ratio, inter eNB S1 based for QCI1'
            elif case.is_x2:
                cname = 'LTE_5880a/E-UTRAN HO Success Ratio, inter eNB X2 based for QCI1'
            else:
                cname = 'LTE_5873a/E-UTRAN HO Success Ratio, intra eNB for QCI1'
            if cname:
                gv.kpi.kpi_volte_ho_ratio = get_counter_value(cname)
            else:
                kw('report_error', 'Counter is invalud to calculate the kpi_handover_ratio')

    execute_tm500_cmd_and_save_log('forw mte GetRRCStats [1] [] [] [1]', cmd_timeout)
    for i in range(gv.tm500.radio_card_count):
        execute_tm500_cmd_and_save_log('forw mte GetNASStats [1] [%d]' %(i), cmd_timeout)
    return result

def stop_mts_gracefully():
    kw('pet_connect_to_tma')
    exp_str = 'I: CMPI MTE 0 MTSCLEARMTS COMPLETE IND'
    execute_tm500_cmd_and_save_log()
    output = execute_tm500_cmd_and_save_log(cmd = 'forw mte mtsclearmts', ignore_log = 'N', timeout = '5')
    if exp_str in output:
        gv.logger.info('Found Indication in command output.')
    else:
        kw('wait_until_find_expected_string_in_tm500_output', '900', '1', 'I: CMPI MTE 0 MTSCLEARMTS COMPLETE IND')
    execute_tm500_cmd_and_save_log('FORW MTE DECONFIGRDASTOPTESTCASE')

