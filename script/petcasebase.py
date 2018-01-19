import time, os, sys, time, datetime, signal
from petbase import *
from pet_ta_config import all_cases
from pet_bts import read_bts_config
import pettool
import zipfile

#Read environemnt config, scenario config, case config
def initlization_suite_config():
    kw('get_env_variables')
    gv.allbts = []
    gv.master_bts = read_bts_config(pv('MASTER_BTS'), 'M', 'P')
    gv.ms_bts = read_bts_config(pv('MS_BTS'), 'M', 'S') if var_exist('MS_BTS') else None
    gv.logger.info(gv.master_bts)

def light_suite_setup_for_pet():
    gv.suite.suite_index += 1
    gv.case.debug_file = pv('debug_file')
    gv.suite.health = True
    gv.suite.timestamp = time.strftime("%Y_%m_%d__%H_%M_%S")
    gv.suite.suitename = pv('SUITE_NAME').replace(' ','_').replace('-', '_') + '__' + gv.suite.timestamp
    gv.suite.suitename = pv('SUITE_NAME').split('_')[0] + '_' + gv.suite.timestamp
    gv.suite.suitename = gv.suite.timestamp
    gv.suite.suitename = _get_suite_name() + '_' + gv.suite.timestamp
    gv.suite.log_directory = os.sep.join([pv('OUTPUT_DIR'), gv.suite.suitename])
    os.makedirs(gv.suite.log_directory)
    kw('log', 'Suite Log directory: [%s]' %(gv.suite.log_directory))
    kw('initlization_suite_config')

def _get_suite_name():
    import re
    src_file = pv('SUITE_SOURCE')
    gv.logger.info('Source file: ' + src_file)
    caseid = re.findall(r'[0-9]{6,7}', pv('SUITE_SOURCE'))
    gv.logger.info('Found caseid: ' + str(caseid))
    return caseid[0] if len(caseid) > 0 else ''


def show_suite_related_files():
    prefix_url = pv('PREFIX_URL') if var_exist('PREFIX_URL') else '.'
    suite_url = '/'.join([prefix_url, gv.suite.log_directory.split('/')[-1]])
    bts_url = '/'.join([suite_url, 'BTS%s' %(gv.master_bts.bts_id)])
    print "*HTML* <a href=%s>Suite file links is here.</a>" %(suite_url)
    print "*HTML* <a href=%s>BTS file links is here.</a>" %(bts_url)

def show_case_related_files():
    prefix_url = pv('PREFIX_URL') if var_exist('PREFIX_URL') else '.'
    case_url = '/'.join([prefix_url, gv.suite.log_directory.split('/')[-1], gv.case.log_directory.split('/')[-1]])
    print "*HTML* <a href=%s>Case file links is here.</a>" %(case_url)

def common_suite_setup_for_pet():
    kw('light_suite_setup_for_pet')
    kw('show_suite_related_files')
    gv.case.case_index = 0

    from pet_bts import prepare_bts_environment
    prepare_bts_environment(gv.allbts)
    kw('pet_get_bts_version')

def light_suite_teardown_for_pet():
    kw('run_keyword_and_ignore_error', 'clean_all_connections')

def common_suite_teardown_for_pet():
    kw('light_suite_teardown_for_pet')

def light_test_case_setup_for_pet():
    gv.case.case_index += 1
    # if not gv.suite.health:
    #     kw('report_error', 'Suite is not health, this case will not run.')
    gv.case.in_teardown = False
    gv.env.save_snapshot = False
    gv.allbts = []
    gv.master_bts = read_bts_config(pv('MASTER_BTS'), 'M', 'P')
    gv.ms_bts = read_bts_config(pv('MS_BTS'), 'M', 'S') if var_exist('MS_BTS') else None
    gv.logger.info(gv.master_bts)

    casename = pv('TEST NAME').replace(' ','_').replace('(','_').replace(')','_').replace('-', '_').replace('+', '_').upper()
    casename = casename[:10].replace('&', '_')
    tags = kw('create list', '@{Test Tags}')
    caseid = [x for x in tags if x.startswith('QC_')][0].split('_')[-1]
    casename = '%s_%s' %(caseid, casename)
    gv.case.log_directory = os.sep.join([gv.suite.log_directory, casename])
    gv.case.timestamp = time.strftime("%Y_%m_%d__%H_%M_%S")
    gv.logger.info('Case Log directory: [%s]' %(gv.case.log_directory))
    os.makedirs(gv.case.log_directory)
    os.makedirs(case_file('counter'))
    os.makedirs(case_file('loadfile'))
    os.makedirs(case_file('artiza'))
    os.makedirs(case_file('artiza/csv'))
    os.makedirs(case_file('tti'))
    gv.case.keyword_group = init_keyword_group()
    gv.case.monitor_error_msg = ''
    gv.shenick_groups = []
    gv.tm500 = None
    gv.datadevice = None
    gv.counter_result = None
    gv.case.done = False

    kw('prepare_case_info')
    kw('prepare_slave_bts_if_used')
    kw('prepare_tm500_if_used')
    kw('pet_tm500_firmware_upgrade_if_needed')
    kw('prepare_mbms_server_if_used')

    from pet_interface import adjust_pa_according_to_palist
    adjust_pa_according_to_palist()
    # kw('report_error', 'Stop by Jufei')

def prepare_case_info():
    gv.case.tags = kw('create list', '@{Test Tags}')
    gv.case.qc_test_instance_id = [x for x in gv.case.tags if x.startswith('QC_')][0].split('_')[-1]
    # gv.case.curr_case = pettool.get_case_config(gv.case.qc_test_instance_id)
    gv.case.curr_case = pettool.get_case_config_new(gv.case.qc_test_instance_id)
    re_organize_case()
    gv.logger.debug(gv.case)

    gv.master_bts.btslog_buffer = []
    if gv.ms_bts:
        # if gv.case.curr_case.master_secondary_scenario.strip():
        if gv.case.curr_case.ms_scf_file.strip():
            gv.ms_bts.btslog_buffer = []
            gv.ms_bts.used = True
        else:
            gv.ms_bts.used = False
    gv.logger.info(gv.master_bts)
    for attr in [x for x in dir(gv.case.curr_case) if x[0] <> '_']:
        setattr(gv.master_bts, attr, getattr(gv.case.curr_case, attr))

def prepare_slave_bts_if_used():
    gv.slave_bts = None
    if gv.case.curr_case.use_slave_bts:
        if var_exist('SLAVE_BTS'):
            gv.slave_bts = read_bts_config(pv('SLAVE_BTS'), 'S', 'P')
            kw('prepare_bts_environment', [gv.slave_bts])
            gv.slave_bts.used = True
            bts = gv.slave_bts
            for sbts in gv.sbts():
                sbts.workcell = 3 if gv.case.curr_case.ca_type == '2CC' else 2
                sbts.workcell = 4 if gv.case.curr_case.ca_type == '3CC' else sbts.workcell
                kw('conversion_scf_file', sbts.bts_id)
                gv.logger.debug(sbts)

def prepare_tm500_if_used():
    if gv.env.use_tm500:
        kw('select_tm500')
        gv.logger.debug(gv.tm500)
        kw('run_keyword_and_ignore_error', 'config_tm500_control_pc')
        kw('makesure_passport_is_running', gv.tm500.conn_pc)
        connections.BTSTELNET.tm500_output_file = case_file('tm500cmd.log')

def prepare_mbms_server_if_used():
    if gv.case.curr_case.mbms:
        conn =  connections.connect_to_ssh_host('10.69.64.83', '22', 'root', 'btstest', '#')
        for subsystem in ['HSS', 'MME', 'MBMSGW', 'INET', 'UPE']:
            output = connections.execute_ssh_command('ps -ef|grep ./'+subsystem).splitlines()
            output = [line for line in output if './'+subsystem in line and not 'grep' in line]
            if len(output) == 0:
                connections.execute_ssh_command('cd /root/Desktop/ysf/LTE_emu/cn/system/'+subsystem.lower())
                connections.execute_ssh_command_without_check('nohup ./%s &' %(subsystem.lower()))
        connections.disconnect_from_ssh()

def common_test_case_setup_for_pet():
    gv.case.start_testing = False
    kw('light_test_case_setup_for_pet')
    kw('show_case_related_files')

    if gv.env.use_tm500:
        kw('start_to_monitor_tm500_console_output')
        gv.tm500.tm500_cmd_output_file = case_file('tm500_cmd.log')

    for bts in gv.mbts():
        kw('conversion_scf_file', bts.btsid)
    for bts in gv.sbts():
        kw('conversion_scf_file', bts.btsid)
    kw('read_all_scf_config', 'BEFORE')  #Done
    try:
        if gv.debug_mode in ['DEBUG', 'PRF']:
            for bts in [x for x in gv.allbts if x.used]:
                if gv.env.use_tm500:
                    kw('restart_tm500_if_needed')
                    kw('wait_until_tm500_startup_succeed')

                kw('start_to_monitor_btslog', bts.bts_id)
                kw('pet_prepare_infomodel', bts.bts_id)
                kw('start_to_monitor_infomodel', bts.bts_id)
                if gv.env.use_artiza:
                    kw('prepare_artiza_before_bts_onair')
                    kw('wait_until_bts_is_onair_by_infomodel', gv.master_bts.btsid, '10mins', '5')
                    kw('prepare_artiza_after_bts_onair')
                if gv.env.use_prisma:
                    kw('prepare_prisma_after_onair')

                # if gv.env.use_tm500:
                #     kw('pet_restart_tm500')
                #     gv.tm500.tm500_restarted = True
                #     gv.tm500_version = gv.case.curr_case.tm500_version
                #     kw('wait_until_tm500_startup_succeed')
        else:
            kw('cleanup_unused_hashfile')  #Done
            kw('prepare_mr_parameters')
            for bts in gv.mbts():
                kw('pet_prepare_config_file_for_bts', bts.btsid)
                kw('pet_restart_bts', bts.btsid, gv.env.reboot_bts_by_pb)
            if gv.env.use_artiza:
                kw('prepare_artiza_before_bts_onair')

            for bts in gv.sbts():
                kw('pet_prepare_config_file_for_bts', bts.btsid)
                kw('pet_restart_bts', bts.btsid, gv.env.reboot_bts_by_pb)

            if gv.env.use_tm500:
                kw('restart_tm500_if_needed')
            kw('wait_until_all_bts_are_ready')
            if gv.env.use_tm500:
                kw('wait_until_tm500_startup_succeed')
            kw('prepare_artiza_after_bts_onair')
            write_to_console('eNB is OnAir.')
    finally:
        pass
    kw('read_all_scf_config', 'AFTER')
    kw('cleanup_work_for_bts', gv.master_bts.bts_id)
    gv.case.start_testing = True

def light_test_case_teardown_for_pet():
    gv.case.done = True
    kw('clean_all_connections')

def common_test_case_teardown_for_pet():
    gv.case.in_teardown = True
    if gv.env.save_snapshot:
        kw('run_keyword_and_ignore_error', 'get_snapshot_log')
        gv.env.save_snapshot = False
    kw('run_keyword_and_ignore_error', 'stop_cmdagent')
    kw('run_keyword_and_ignore_error', 'pet_release_data_device')
    kw('run_keyword_and_ignore_error', 'stop_console_server_if_needed')
    kw('run_keyword_and_ignore_error', 'stop_to_capture_all_kinds_of_logs')
    if gv.env.use_tm500:
        kw('run_keyword_and_ignore_error', 'stop_to_monitor_tm500_console_output')
        kw('run_keyword_and_ignore_error', 'zip_tm500log_file')
    for bts in [x for x in gv.allbts if x.used]:
        kw('run_keyword_and_ignore_error', 'stop_to_monitor_btslog', bts.bts_id)
        kw('run_keyword_and_ignore_error', 'stop_to_monitor_infomodel', bts.bts_id)
        kw('run_keyword_and_ignore_error', 'pet_ute_admin_teardown', bts.bts_id)
    kw('light_test_case_teardown_for_pet')


def zip_tm500log_file():
    file_list = os.listdir(case_file(''))
    tm500log = ['tm500cmd.log', 'tm500_cmd.log']
    for log in tm500log:
        if log in file_list:
            tm500_file = case_file(log)
            if os.path.getsize(tm500_file) > 1024*1024*5:
                zip_file = case_file(log.replace('log','zip'))
                f = zipfile.ZipFile(zip_file, 'w', zipfile.ZIP_DEFLATED)
                f.write(tm500_file)
                f.close()
                cmd = 'rm -rf '+ tm500_file
                print cmd
                os.system(cmd)


def common_check_for_pet_should_be_ok():
    check_btslog_fatal()
    finish_keyword_group(gv.case.keyword_group)

def re_organize_case():
    init_data = {
         'codec'                        :   '',
         'ho_type'                      :   '',
         'ho_path'                      :   '',
         'max_tti_user'                 :   '',
         'mr_paging_ue_count'           :   '0',
         'mr_paging_impair_ue_count'    :   '0',
         'mr_call_drop_ue_count'        :   '0',
         'mr_cd_impair_ue_count'        :   '0',
         'mr_intra_ho_ue_count'         :   '0',
         'mr_ho_impair_ue_count'        :   '0',
         'mr_volte_ue_count'            :   '0',
         'mr_volte_impair_ue_count'     :   '0',
         'mr_volte_ho_ue_count'         :   '0',
         'mr_volte_ho_impair_ue_count'  :   '0',
         'ho_stagger'                   :   '25',
         'cd_stagger'                   :   '25',
         'mr_volte_ho_stagger'          :   '25',
         'paging_stagger'               :   '25',
         'mr_volte_stagger'             :   '25',
         'ca_type'                      :   '',
         'sector_start'                 :   '0',
         'sector_end'                   :   '360',
         'ref_signal_power'             :   '10',
         'cell_range'                   :   '1000',
         'format'                       :   '0',
         'ql'                           :   '5',
         'case_duration'                :   '3600',
         'tm500_version'                :   'L',
         'tm500_attach_file'            :   '',
         'team'                         :   '',
         'fixed_scf'                    :   0,
         'prf_capacity'                 :   '0',
         'load_ue_count'                :    0,
         'check_tti'                    :   0,
         'mts_scenario'                 :   '',
         'ue_group_config'              :   '',


    }
    case = gv.case.curr_case
    for attr in init_data:
        if hasattr(case, attr):
            if str(getattr(case, attr)).strip() == '':
                setattr(case, attr, init_data[attr])
        else:
            setattr(case, attr, init_data[attr])
    for attr in ['ho_path', 'ho_type']:
        if hasattr(case, attr):
            if str(getattr(case, attr)).strip() == '':
                setattr(case, attr, getattr(case, attr))

    case.tm = case.tm.upper().replace('TM', '')
    case.real_paging_ue_count = int(case.mr_paging_ue_count) +\
                                int(case.mr_paging_impair_ue_count)
    case.real_cd_ue_count = int(case.mr_call_drop_ue_count) +\
                                int(case.mr_cd_impair_ue_count)
    case.real_ho_ue_count = int(case.mr_intra_ho_ue_count) +\
                                int(case.mr_ho_impair_ue_count)
    case.real_volte_ue_count = int(case.mr_volte_ue_count) +\
                                 int(case.mr_volte_impair_ue_count) +\
                                 int(case.mr_volte_ho_ue_count) +\
                                 int(case.mr_volte_ho_impair_ue_count)
    case.real_call_drop_volte = int(case.mr_volte_ue_count) +\
                                 int(case.mr_volte_impair_ue_count)
    case.real_ho_volte = int(case.mr_volte_ho_ue_count) + int(case.mr_volte_ho_impair_ue_count)

    case.band = case.band.replace('M','')
    case.tm = case.tm.replace('TM','')
    case.is_handover = case.ho_type.strip() <> ''
    case.is_inter = case.ho_type == 'INTER'
    case.is_intra = case.ho_type == 'INTRA'
    if hasattr(case, 'different_frequency'):
        case.is_df = case.different_frequency
        case.is_sf = not case.different_frequency
    case.is_s1 = case.ho_path == 'S1'
    case.is_x2 = case.ho_path == 'X2'
    case.use_slave_bts = case.is_inter

    case.has_mr_volte = case.real_volte_ue_count >0
    case.has_impair =       int(case.mr_paging_impair_ue_count) +\
                            int(case.mr_cd_impair_ue_count) +\
                            int(case.mr_ho_impair_ue_count) +\
                            int(case.mr_volte_impair_ue_count) +\
                            int(case.mr_volte_ho_impair_ue_count) > 0
    case.has_ho_volte = case.real_ho_volte > 0

    if case.domain =='PRF':
        case.is_prf_attach = case.prf_case_type.upper() in ['Attach&Deattach'.upper()]
        case.is_prf_paging = case.prf_case_type.upper() in ['Paging'.upper()]
        case.is_prf_ho     = case.prf_case_type.upper() == 'handover'.upper()
        case.is_prf_drb    = case.prf_case_type.upper() == 'DRB'
        case.is_prf_mix    = case.prf_case_type.upper() == 'MIX'
        case.is_prf_overload    =   case.prf_load_type.upper() == 'OVERLOAD'
        case.is_prf_burst       =   case.prf_load_type.upper() == 'BURST'
        kpistr = case.kpi.lower()
        case.kpi = ';'.join(['kpi_prf_'+x.split(':')[0].strip()+':'+x.split(':')[1] for x in kpistr.replace(',', ';').split(';') if x.strip()])
        # case.kpi += ';kpi_prf_duration:' + str(int(int(case.case_duration)/60))
        case.cell_seq_map = []
        for line in case.prf_cell_seq_map.splitlines():
            if line.strip():
                line = line.upper().replace('CELL', '').replace('SEQ', '')
                cellno, seqno = line.split('-')
                case.cell_seq_map.append([cellno, seqno])

    if case.case_type == 'VOLTE_COVERAGE':
        case.prisma_file_scenario   = 'volte_coverage.sce'
        case.prisma_file_counter    = 'counter_volte.zip'
        case.prisma_file_user       = 'usr.usr'
        case.prisma_file_sid        = 'sid.sid'
        case.prisma_file_mdl        = 'good.mdl'

        kpistr = case.kpi.lower()
        case.kpi = ';'.join(['kpi_volte_vc_'+x.split(':')[0].strip()+':'+x.split(':')[1] for x in kpistr.replace(',', ';').split(';') if x.strip()])

    if case.case_type in ['VOLTE_PERM', 'VOLTE_MIX']:
        kpistr = case.kpi.lower()
        # case.kpi = ';'.join(['kpi_volte_vp_'+x.split(':')[0].strip()+':'+x.split(':')[1] for x in kpistr.replace(',', ';').split(';') if x.strip()])
        case.load_ue_count = int(case.load_ue_count)
        case.is_mix = int(case.ue_count) > 0 and int(case.load_ue_count) > 0
    if case.case_type in ['VOLTE_CAP']:
        case.is_mix = False
        case.total_ue_count = int(case.ue_count) + int(case.load_ue_count)

    re_organize_case_for_pet2(case)


def re_organize_case_for_pet2(case):
    if case.team.upper() <> 'PET2':
        return 0
    case.uegroup_list = []
    case.ue_is_ca = False
    case.ue_is_3cc = False
    case.ue_has_nca = False
    case.ue_is_ulca = False
    case.ue_is_mdrb = False
    case.ue_is_m678 = False
    case.captrue_ttitrace = False
    case.ue_count = 0
    case.ue_nca_count = 0
    case.ue_ca_count = 0
    case.ue_3cc_count = 0
    case.ue_is_volte =  False
    case.traffic_3cc = 0
    case.traffic_ca = 0
    case.traffic_nca = 0
    case.bbpooling = False
    if case.f_1130 and case.f_2664:
        case.bbpooling = True
    for groupstr in case.ue_group_config.split(';'):
        if groupstr.strip():
            group = IpaMmlItem()
            group_len = len(groupstr.split(','))
            group.ue_type       = groupstr.split(',')[0]
            group.prb           = groupstr.split(',')[1]
            group.ue_count      = groupstr.split(',')[2]
            group.cell_index    = groupstr.split(',')[3]
            group.traffic_mbps  = groupstr.split(',')[4] if group_len > 4 else 0
            case.uegroup_list.append(group)
            if group.ue_type == '3CC':
                case.ue_is_3cc = True
                case.ue_3cc_count = group.ue_count
                case.traffic_3cc = group.traffic_mbps
            if group.ue_type in ['CA','ULCA'] :
                case.ue_is_ca = True
                case.ue_ca_count = group.ue_count
                case.traffic_ca = group.traffic_mbps
            if group.ue_type == 'NCA':
                case.ue_has_nca = True
                case.ue_nca_count = group.ue_count
                case.traffic_nca = group.traffic_mbps
            if group.prb in ['MA', 'MB']:
                case.ue_is_mdrb = True
            if group.prb == 'MI':
                case.ue_is_m678 = True
            if group.ue_type == 'ULCA':
                case.ue_is_ulca = True
                case.ue_is_ca = True
            if group.prb == 'V':
                case.ue_is_volte = True
            case.ue_count = case.ue_count + int(group.ue_count)

    case.service_group_list = []
    for groupstr in case.mts_scenario.split(';'):
        if groupstr.strip():
            group = IpaMmlItem()
            group.service_list1             = groupstr.split(',')[0]
            group.service_list2             = groupstr.split(',')[1]
            group.ue_count                  = groupstr.split(',')[2]
            case.service_group_list.append(group)

    case.has_cap_volte = 'voip' in case.mts_scenario
    if case.check_tti:
        if case.has_cap_volte:
        	case.pcell_target_dl = 0
        	case.pcell_target_ul = 90
        else:
        	case.pcell_target_dl = 95 if case.uegroup_list[0].prb.upper() == 'S' and not case.ue_is_ca else 70
        	case.pcell_target_ul = 95 if case.uegroup_list[0].prb.upper() == 'S' and not case.ue_is_ca else 70
        case.kpi += ';kpi_pcell_dl_sf_fd:%s' %(case.pcell_target_dl)
        case.kpi += ';kpi_pcell_dl_nf_fd:%s' %(case.pcell_target_dl)
        case.kpi += ';kpi_pcell_ul_nf_fd:%s' %(case.pcell_target_ul)
        case.scell_target_dl = 0
        case.scell_target_ul = 0
        if case.ue_is_ca:
            case.kpi += ';kpi_scell_dl_sf_fd:%s' %(case.scell_target_dl)
            case.kpi += ';kpi_scell_dl_nf_fd:%s' %(case.scell_target_dl)
            case.kpi += ';kpi_scell_ul_nf_fd:%s' %(case.scell_target_ul)

    case.cap_fix_mme_ip = '10.68.152.170' if gv.env.use_catapult and case.ue_is_m678 else ''

if __name__ == '__main__':
    gv.team = 'PET1'
    gv.case.curr_case = pettool.get_case_config('407019')
    re_organize_case()
    print gv.case.curr_case
    for attr in dir(gv.case.curr_case):
        print attr, type(getattr(gv.case.curr_case, attr))
