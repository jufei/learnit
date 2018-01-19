import os, re
from petbase import *

def verify_each_pmcount_expression(configname, pmfilepath):
    from pet_counter_cal import c_counter_manager
    manager = c_counter_manager(configname, '', pmfilepath)
    manager.prepare_counter_source()
    manager.parse_data_file()
    gv.logger.info('Old need check items:  %d' %(len([x for x in manager.pmconfig if x.needcheck])))
    gv.logger.info('Adapt counter need check config ....')
    set_counter_need_check(manager.pmconfig)
    gv.counter_result = manager.pmconfig
    manager.save_data_file(case_file('counter.csv'))
    manager.calc_all_counters()
    manager.check_result()
    manager.show_check_result_in_html()
    manager.show_failed_items()
    manager.show_check_result_in_table()
    if in_robot():
        kw('run_keyword_and_ignore_error', 'log', manager.show_check_for_ta_analysis())
    gv.counter_manager = manager
    if in_robot():
        if [kpi for kpi in manager.pmconfig if not kpi.passed]:
            kwg('report_error', 'Check PM Counter KPI Failed!')

def counter_kpi_should_be_correct():
    if gv.case.curr_case.use_kpi_counter:
        from pet_bts import download_bts_pmcount_file
        download_bts_pmcount_file(gv.master_bts.bts_id)
        filename = os.path.sep.join([resource_path(), 'config', 'case', '%s.xkt' %(gv.env.release)])
        gv.logger.info('Used XKT File: ' + filename)
        verify_each_pmcount_expression(filename, case_file('counter'))
    else:
        gv.logger.info('No specific PM Counter temlate file for this case.')

def read_counter_defination_config():
    filename = 'counterdef_%s.xlsx' %(gv.case.curr_case.domain)
    gv.counterfile = os.path.sep.join([resource_path(), 'config', 'case', filename])
    gv.logger.info('Used Counter Excel File: ' + filename)
    if not os.path.exists(gv.counterfile):
        gv.logger.info('Counter Defination XLS file does not exist.')
        return []

    import xlrd
    bk = xlrd.open_workbook(gv.counterfile)
    shxrange = range(bk.nsheets)
    sh = bk.sheet_by_name('counter')
    nrows, ncols = sh.nrows, sh.ncols
    titles = sh.row_values(0)
    info = []
    for i in range(1, nrows):
        line = ['%s' % (x) for x in sh.row_values(i)]
        acase = IpaMmlItem()
        if line[0].strip():
            for j in range(len(titles)):
                if titles[j].strip():
                    fieldname = titles[j].lower().replace(' ', '_').strip()
                    if fieldname not in [x.lower() for x in ['GroupName', 'CounterName', 'ideal', 'impaired']]:
                        fieldname = 'ct_'+ fieldname
                    setattr(acase, fieldname, '%s' % (line[j].strip()))
            if acase.countername.strip():
                if acase.countername.startswith('LTE_'):
                    acase.counter_alias_name = acase.countername.split('/')[-1] if '/' in acase.countername else ' '.join(acase.countername.split(' ')[1:])
                else:
                    acase.counter_alias_name = acase.countername.strip()
        info.append(acase)
    return info

counter_pms = {
    'ct_call_drop'          :    'check_ct_call_drop',
    'ct_intra_df'           :    'check_ct_intra_df',
    'ct_intra_sf'           :    'check_ct_intra_sf',
    'ct_paging'             :    'check_ct_paging',
    'ct_s1_df'              :    'check_ct_s1_df',
    'ct_s1_sf'              :    'check_ct_s1_sf',
    'ct_volte_call_drop'    :    'check_ct_volte_call_drop',
    'ct_volte_intra_df'     :    'check_ct_volte_intra_df',
    'ct_volte_intra_sf'     :    'check_ct_volte_intra_sf',
    'ct_volte_s1_df'        :    'check_ct_volte_s1_df',
    'ct_volte_s1_sf'        :    'check_ct_volte_s1_sf',
    'ct_volte_x2_df'        :    'check_ct_volte_x2_df',
    'ct_volte_x2_sf'        :    'check_ct_volte_x2_sf',
    'ct_x2_df'              :    'check_ct_x2_df',
    'ct_x2_sf'              :    'check_ct_x2_sf',

    #for PRF
    'ct_prf_attach'         :    'check_ct_prf_attach',
    'ct_prf_paging'         :    'check_ct_prf_paging',
    'ct_prf_drb'            :    'check_ct_prf_drb',
    'ct_prf_ho'             :    'check_ct_prf_ho',
    'ct_prf_mix'            :    'check_ct_prf_mix',
    'ct_prf_overload'       :    'check_ct_prf_overload',

    #for Volte:
    'ct_video_mix'         :     'check_ct_mix_video',
    'ct_volte_cap'         :     'check_ct_volte_cap',
}

def _get_case_attr(case, attrname):
    if str(getattr(gv.case.curr_case, attrname)).strip():
        return int(getattr(gv.case.curr_case, attrname))
    return 0

def is_impair_case(case):
    if case.domain == 'MR':
        return _get_case_attr(case, 'mr_paging_impair_ue_count') +\
                _get_case_attr(case, 'mr_cd_impair_ue_count') +\
                _get_case_attr(case, 'mr_ho_impair_ue_count') > 0
    if case.domain == 'PRF':
        return False

def check_ct_call_drop(case):
    return _get_case_attr(case, 'mr_call_drop_ue_count') +\
            _get_case_attr(case, 'mr_cd_impair_ue_count')  > 0

def check_ct_intra_df(case):
    return case.real_ho_ue_count and case.ho_type.upper() == 'INTRA' and case.different_frequency

def check_ct_intra_sf(case):
    return case.real_ho_ue_count and case.ho_type.upper() == 'INTRA' and case.different_frequency

def check_ct_paging(case):
    return _get_case_attr(case, 'mr_paging_ue_count') +\
            _get_case_attr(case, 'mr_paging_impair_ue_count') > 0

def check_ct_s1_df(case):
    return case.real_ho_ue_count and\
           case.ho_type.upper() == 'INTER' and\
           case.ho_path.strip().upper() == 'S1' and\
           case.different_frequency

def check_ct_s1_sf(case):
    return case.real_ho_ue_count and\
           case.ho_type.upper() == 'INTER' and\
           case.ho_path.strip().upper() == 'S1' and\
           case.different_frequency

def check_ct_volte_call_drop(case):
    return case.real_call_drop_volte > 0

def check_ct_volte_intra_df(case):
    return case.has_ho_volte and case.is_intra and case.is_df

def check_ct_volte_intra_sf(case):
    return case.has_ho_volte and case.is_intra and case.is_sf

def check_ct_volte_s1_df(case):
    return case.has_ho_volte and case.is_df and case.ho_path.strip().upper() == 'S1'

def check_ct_volte_s1_sf(case):
    return case.has_ho_volte and case.is_sf and case.ho_path.strip().upper() == 'S1'

def check_ct_volte_x2_df(case):
    return case.has_ho_volte and case.is_df and case.ho_path.strip().upper() == 'X2'

def check_ct_volte_x2_sf(case):
    return case.has_ho_volte and case.is_sf and case.ho_path.strip().upper() == 'X2'

def check_ct_x2_df(case):
    return case.real_ho_ue_count and\
           case.ho_type.upper() == 'INTER' and\
           case.ho_path.strip().upper() == 'X2' and\
           case.different_frequency

def check_ct_x2_sf(case):
    return case.real_ho_ue_count and\
           case.ho_type.upper() == 'INTER' and\
           case.ho_path.strip().upper() == 'X2' and\
           not case.different_frequency

def check_ct_prf_attach(case):
    return case.is_prf_attach

def check_ct_prf_paging(case):
    return case.is_prf_paging

def check_ct_prf_drb(case):
    return case.is_prf_drb

def check_ct_prf_ho(case):
    return case.is_prf_ho

def check_ct_prf_mix(case):
    return case.is_prf_mix

def check_ct_prf_overload(case):
    return case.is_prf_overload

def check_ct_mix_video(case):
    return case.case_type.upper() == 'VOLTE_MIX'

def check_ct_volte_cap(case):
    return case.case_type.upper() == 'VOLTE_CAP'

def set_counter_need_check(counter_config):
    counter_def_list = read_counter_defination_config()
    if counter_def_list:
        for counter in counter_config:
            if counter.needcheck:
                counter.needcheck = False
                count_def = [x for x in counter_def_list if x.countername.upper() == counter.name.upper()]
                count_def = [x for x in counter_def_list if x.counter_alias_name.upper() == counter.counter_alias_name.upper()]
                if count_def:
                    count_def = count_def[0]
                    for param in counter_pms:
                        if hasattr(count_def, param):
                            if getattr(count_def, param).upper() == 'Y' and\
                                globals()[counter_pms[param]](gv.case.curr_case):
                                gv.logger.info('[%s] need check' %(count_def.countername))
                                if is_impair_case(gv.case.curr_case):
                                    counter.summarytarget = getattr(count_def, 'impaired')
                                else:
                                    counter.summarytarget = getattr(count_def, 'ideal')
                                counter.needcheck = True
                                break

def get_counter_value(countername):
    item = [x for x in gv.counter_manager.pmconfig if x.name.strip().upper() == countername.strip().upper()]
    if item:
        if item[0].reporttype.lower() == 'FailureRatio'.lower() and 'NA' in str(item[0].result):
            return 0.0
        else:
            return float(item[0].result)
    else:
        kw('report_error', 'Could not find the counter result for : [%s]' %(countername))

if __name__ == '__main__':
    from optparse import *
    parser = OptionParser()
    parser.add_option("-d",  "--dire", dest="dire", default='/', help='Counter file directory')
    parser.add_option("-c",  "--caseid", dest="caseid", default='670000', help='BTS ID')
    (options, sys.argv[1:]) = parser.parse_args()

    from pettool import get_case_config_new
    gv.case.curr_case = get_case_config_new(options.caseid)
    from petcasebase import re_organize_case
    re_organize_case()

    gv.case.log_directory = '/tmp'
    xktfilename = '/home/work/tacase/Resource/config/case/%s.xkt' %(gv.case.curr_case.releaseno)
    verify_each_pmcount_expression(xktfilename, options.dire)

    # dire = '/home/work/Jenkins2/workspace/MR_TL17_MJ/20160726_1226/TA_TL17FSIH_OBSAI_CAP_00105_20M_20_20_20M_ULDL1_SSF7_TM3_TM3_TM3_TM3_3CC_MR_DRX__2016_07_26__12_26_47/EQUEST_NO1/counter/'
    # dire = '/home/work/Jenkins2/workspace/MR_TL17_MJ/20160728_0905/TA_TL17FSIH_OBSAI_CAP_00106_20M_20_20_20M_ULDL1_SSF7_TM3_TM3_TM3_TM3_3CC_MR_DRX_F2026__2016_07_28__09_07_44/TE1235_NO1/counter'
    # dire = '/home/work/Jenkins2/workspace/MR_TL17_642/20160822_1125/TA_TL17FSIH_CPRI_CAP_00010_20M_ULDL2_SSF7_TM8_8PIPE__2016_08_22__11_25_14/_VOLTE_NO1/counter/'
    # dire = '/home/work/Jenkins2/workspace/MR_TL17_CC/20160825_0643/TA_TL17FSMF_OBSAI_CAP_00012_20M_ULDL2_SSF7_TM4X2_2CC_4PIPE__2016_08_25__11_43_44/01_MIX_NO1/counter/'
    # dire = '/home/work/Jenkins2/workspace/MR_TL17_CC/20160906_0930/TA_TL17FSMF_OBSAI_CAP_00005_20M_ULDL2_SSF7_TM4X2_4PIPE_F1235_F2026__2016_09_06__09_30_28/L_DROP_NO5/counter/'
    # dire = '/home/work/Jenkins2/workspace/MR_TL17_MJ/363/TA_TRUNK_CAP_00002_20M_20M_20M_20M_ULDL1_SSF7_TM3_TM3_TM3_TM3_3CC_MR__2016_11_09__17_55_20/PAGING_NO1/counter/'

    # dire = '/home/work/temp/4'
    # xktfilename = '/home/work/tacase_dev/Resource/config/case/TL17SP.xkt'
    # dire = '/home/work/jrun/2017_05_09__16_09_50/472700_E_IDEAL_RF/counter'
    # from pettool import get_case_config_new
    # gv.env.release = 'TL17SP'
    # gv.team = 'PET1'
    # gv.case.curr_case = get_case_config_new('472700')
    # from petcasebase import re_organize_case
    # re_organize_case()
    # # print gv.case.curr_case

    # # gv.case = IpaMmlItem()
    # # gv.case.curr_case = IpaMmlItem()
    # gv.case.log_directory = '/tmp'
    # # config =  read_counter_defination_config()
    # # for item in config:
    # #     print item.countername, '-------------', item.counter_alias_name
    # # gv.counterfile = '/home/work/tacase/Resource/config/case/counterdef_16A.xlsx'
    # verify_each_pmcount_expression(xktfilename, dire)
    # pass


