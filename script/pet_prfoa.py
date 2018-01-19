from petbase import *

def common_suite_setup_for_prfoa():
    kw('common_suite_setup_for_pet')

def common_suite_teardown_for_prfoa():
    kw('common_suite_teardown_for_pet')

def common_test_case_setup_for_prfoa():
    kw('common_test_case_setup_for_pet')

def common_test_case_teardown_for_prfoa():
    move_csv_file()
    if gv.artiza:
        gv.artiza.teardown()
    kw('common_test_case_teardown_for_pet')

def start_service_on_artiza():
    if gv.artiza:
        seq_list = ''
        for step in [line for line in gv.case.curr_case.prf_seq_control_steps.splitlines() if line.strip()]:
            if gv.case.curr_case.is_prf_burst:
                seq_list= step.strip().replace(';', '').split('/')[0]
                seqs, call, interval, loopcount = seq_list.split(':')
                for seq in seqs.split(','):
                    gv.artiza.sm.start_burst(seq, call, interval, loopcount)
            else:
                if seq_list: #means there has start a seq, so need to stop first
                    gv.artiza.sm.stop_sim()
                seq_list= step.strip().replace(';', '').split('/')[0]
                gv.artiza.sm.start_sim(seq_list)

            if '/' in step:
                timer = step.strip().replace(';', '').split('/')[-1]
                time.sleep(int(timer))
    pass

def checking_for_overload():
    if len(gv.artiza.sm.stat_result.cplan_history) == 1:
        return 0
    r1 = gv.artiza.sm.stat_result.cplan_history[-1]
    r2 = gv.artiza.sm.stat_result.cplan_history[-2]

    case = gv.case.curr_case
    for line in gv.case.curr_case.cell_seq_map:
        cell, seq = line
        line_cell_1 = get_cplan_item(cell, seq, r1)
        line_all_1 = get_cplan_item('all', seq, r1)
        line_cell_2 = get_cplan_item(cell, seq, r2)
        line_all_2 = get_cplan_item('all', seq, r2)
        gv.logger.info(line_cell_1)
        gv.logger.info(line_cell_2)
        gv.logger.info(line_all_1)
        gv.logger.info(line_all_2)

        if int(line_cell_1.seq_comp) == int(line_cell_2.seq_comp):
            raise Exception, 'Seq Comp stop increasing!!!'
        if int(line_all_1.seq_comp) == int(line_all_2.seq_comp):
            raise Exception, 'Seq Comp stop increasing!!!'

def checking_during_case_running():
    running_target = 20
    case = gv.case.curr_case

    fspusage = kw('get_fsp_cpu_usage')
    if fspusage > 0:
        gv.kpi.fspcpu_list.append(fspusage)

    gv.artiza.sm.get_cplan_statistic()
    if case.is_prf_overload or case.is_prf_burst:
        checking_for_overload()
        return 0
    if case.is_prf_mix:
        calc_mix_success_ratio()
    #Check S1
    if case.is_prf_attach or case.is_prf_paging or case.is_prf_drb:
        s1_sr = calc_prf_success_ratio('s1')
    if case.is_prf_mix:
        s1_sr = gv.kpi.kpi_prf_s1_sr
        gv.logger.info('Current S1 Success Ratio: ' + str(s1_sr))
        if s1_sr < running_target:
            raise Exception, 'Too low S1 Success Rate [%f], case will quit!' %(s1_sr)

    #check SR
    if case.is_prf_mix:
        sr = gv.kpi.kpi_prf_sr
    else:
        sr = calc_prf_success_ratio('rrc')
    gv.logger.info('Current Success Ratio: ' + str(sr))
    if sr < running_target:
        raise Exception, 'Too low Success Rate [%f], case will quit!' %(sr)

    if case.is_prf_mix:
        gv.logger.info('Current Handover Success Ratio: ' + str(gv.kpi.kpi_prf_ho))
        if gv.kpi.kpi_prf_ho < running_target:
            raise Exception, 'Too low Success Rate [%f], case will quit!' %(gv.kpi.kpi_prf_ho)


def work_after_service_done():
    get_statistic_info_for_prfoa()
    if gv.debug_mode <> 'DEBUG' and not gv.case.curr_case.is_prf_overload and not gv.case.curr_case.is_prf_burst:
        process_kpi_counter()

def process_kpi_counter():
    if gv.case.curr_case.use_kpi_counter:
        kw('wait_until_new_pmcount_file_generated')
        kw('counter_kpi_should_be_correct')

def move_csv_file():
    cmd = 'cp %s/* %s/' %(gv.artiza.config.taserver_local_workspce, case_file('artiza/csv'))
    run_local_command(cmd)

def wait_until_prfoa_service_is_done():
    gv.kpi.kpi_prf_sr = 0
    gv.kpi.fspcpu_list = []
    case = gv.case.curr_case
    from robot.utils import timestr_to_secs
    timeout = int(gv.case.curr_case.case_duration) + 100 if gv.case.curr_case.case_duration else 300
    timeout = 300 if gv.debug_mode == 'DEBUG' and timeout>100 else timeout
    write_to_console('Start PRF Service on Artiza...')
    start_time = time.time()
    total_time = timestr_to_secs(timeout)
    count, count_2 = 0, 0
    output = ''

    if case.prf_service_wait_timer > 0:
        gv.logger.info('Wait for Service Wait Timer: %d' %(case.prf_service_wait_timer))
        time.sleep(case.prf_service_wait_timer)

    gv.logger.info('Start real service.')
    while time.time() < start_time + total_time:
        check_btslog_fatal()
        time.sleep(0.1)
        count += 1
        if count >= 4000:
            checking_during_case_running()
            gv.artiza.sm.get_tput_stat()
            gv.logger.info('Still need wait for : %d seconds.' %((start_time + total_time - time.time())))
            count = 0
    if gv.debug_mode <> 'DEBUG':
        wait_until_prfoa_service_done_by_check_seq_start()
    kw('work_after_service_done')

def wait_until_prfoa_service_done_by_check_seq_start():
    def _sum_seq_start(data):
        result = 0
        for line in gv.case.curr_case.cell_seq_map:
            result += int(get_cplan_item(line[0], line[1], data).seq_start)
        return result
    gv.logger.info('Wait until service done')
    if gv.case.curr_case.is_prf_overload or gv.case.curr_case.is_prf_burst:
        return 0

    while True:
        gv.artiza.sm.get_cplan_statistic()
        calc_prf_success_ratio('rrc')
        done = True
        datasource = gv.artiza.sm.stat_result.cplan_history
        if len(datasource) >=2:
            if _sum_seq_start(datasource[-1]) <> _sum_seq_start(datasource[-2]):
                gv.logger.info('Service is not done by checking seq start for all seq.')
                time.sleep(10)
            else:
                gv.logger.info('Service is done by checking seq start for all seq.')
                return 0
        else:
            gv.logger.info('Service is done by checking seq start for all seq.')
            return 0

def get_statistic_info_for_prfoa():
    if gv.case.curr_case.is_prf_mix:
        calc_mix_success_ratio()
    else:
        gv.kpi.kpi_prf_sr           =   calc_prf_success_ratio('rrc')
        gv.kpi.kpi_prf_s1_sr        =   calc_prf_success_ratio('s1')

    gv.kpi.kpi_prf_caps         =   int(gv.case.curr_case.prf_caps)
    gv.kpi.kpi_case_duration    =   int(gv.case.curr_case.case_duration)/60
    gv.kpi.kpi_prf_capacity     =   int(gv.case.curr_case.prf_capacity)

def common_check_for_prfoa_should_be_ok():
    kw('common_check_for_pet_should_be_ok')

def get_cplan_item(cell, seq, data):
    return [x for x in data if str(x.cell) == str(cell) and str(x.seq) == str(seq)][0]

def calc_prf_success_ratio(sr_type='rrc'):
    result = gv.artiza.sm.stat_result.cplan_history[-1]
    sr_list = []
    case = gv.case.curr_case
    if case.is_prf_mix:
        return calc_mix_success_ratio()

    for line in gv.case.curr_case.cell_seq_map:
        cell, seq = line
        line_cell = get_cplan_item(cell, seq, result)
        line_all  = get_cplan_item('all', seq, result)
        sr = 0
        if case.is_prf_attach or case.is_prf_drb:
            if sr_type == 'rrc':
                sr = float(line_cell.seq_comp_rate)
            else:
                sr = 100 - float(float(line_all.seq_incomp)*100.0/float(line_cell.seq_start))
        if case.is_prf_paging:
            if sr_type == 'rrc':
                sr = float(float(line_cell.seq_comp)*100/float(line_all.seq_start))
            else:
                sr = line_all.seq_comp_rate
        sr_list.append(sr)

    if case.is_prf_ho:  #handover success rate
        ho_out_sr_list = []
        ho_in_sr_list = []
        for i in range(len(case.cell_seq_map)/2):
            cell1, seq1 = gv.case.curr_case.cell_seq_map[i*2]
            cell2, seq2 = gv.case.curr_case.cell_seq_map[i*2+1]
            line_cell1 = get_cplan_item(cell1, seq1, result)
            line_cell2 = get_cplan_item(cell2, seq2, result)
            line_all1  = get_cplan_item('all', seq1, result)
            line_all2  = get_cplan_item('all', seq2, result)

            sr_1  = 100 - float(float(line_all1.seq_incomp)*100/float(line_cell1.seq_start))
            sr_2  = float(line_cell1.seq_comp_rate)

            ho_out_sr_list += [sr_1, sr_2]

            sr_1 = float(line_all2.seq_comp_rate)
            sr_2 = float(line_cell2.seq_comp)*100/float(line_all2.seq_start)

            ho_in_sr_list += [sr_1, sr_2]
        return round((min(ho_out_sr_list) + min(ho_in_sr_list))/2, 2)

    return min(sr_list)

def calc_mix_success_ratio():
    def _calc_sr(seq_index, s1mode, srmode, s1list, srlist):
        for i in range(3): # paging
            cell = str(i + 1)
            seq  = str(i*9 + int(seq_index))
            gv.logger.info('!!!!!!!!!!!!!  Cell: %s, Seq %s' %(cell, seq))
            line_cell = get_cplan_item(cell, seq, result)
            line_all  = get_cplan_item('all', seq, result)
            if s1mode.upper() == 'direct'.upper():
                sr_1    =  float(line_all.seq_comp_rate)
            else:
                sr_1  = 100 - float(float(line_all.seq_incomp)*100/float(line_cell.seq_start))
            if srmode.upper() == 'direct'.upper():
                sr_2  = float(line_cell.seq_comp_rate)
            else:
                sr_2  = float(line_cell.seq_comp)*100/float(line_all.seq_start)
        s1list.append(sr_1)
        srlist.append(sr_2)

    result = gv.artiza.sm.stat_result.cplan_history[-1]
    case = gv.case.curr_case
    s1sr = []
    sr = []
    ho = []
    _calc_sr(1, 'cross',  'direct', s1sr, sr)   #random access
    _calc_sr(2, 'cross',  'cross',  s1sr, ho)   #handover out
    _calc_sr(3, 'direct', 'cross',  s1sr, ho)   #handover in
    _calc_sr(4, 'cross',  'direct', s1sr, sr)   #drb
    _calc_sr(5, 'cross',  'direct', s1sr, sr)   #taupdate
    _calc_sr(6, 'direct', 'cross',  s1sr, sr)   #paging
    gv.kpi.kpi_prf_ho = min(ho)
    gv.kpi.kpi_prf_sr    = min(sr)
    gv.kpi.kpi_prf_s1_sr    = min(s1sr)


