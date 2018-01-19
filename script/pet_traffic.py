import os, time
from petbase import *
from pet_prisma_mng import c_prisma_runner
import pettool

def common_suite_setup_for_traffic_model():
    kw('common_suite_setup_for_pet')

def common_suite_teardown_for_traffic_model():
    kw('common_suite_teardown_for_pet')

def common_test_case_setup_for_traffic_model():
    kw('common_test_case_setup_for_pet')
    gv.case.case_log_list = []
    kw('start_to_capture_all_kinds_of_logs')

def common_test_case_teardown_for_traffic_model():
    kw('common_test_case_teardown_for_pet')

def common_check_for_trafic_model_should_be_ok():
    kw('common_check_for_pet_should_be_ok')

def start_test_scenario():
    gv.prisma_runner = c_prisma_runner(gv.prisma)
    gv.prisma_runner.running()

def wait_until_traffic_model_service_is_done():
    timeout = str(int(gv.case.curr_case.case_duration) + 60)
    gv.prisma_runner.wait_until_completed(timeout, '60')

def get_statistic_info_for_traffic_model():
    gv.kpi.kpi_tr = 100

def get_csv_value(csvfile = '', fielddefs = {}):
    lines = open(csvfile).readlines()
    titles = [x.upper() for x in lines[0].split(',')]
    lastline = lines[-1].split(',')
    for field in fielddefs:
        if field.upper() in titles:
            index = titles.index(field.upper())
            fielddefs[field] = lastline[index]
        else:
            raise 'Invalid field name in defination: %s' %(field)
    return fielddefs

fielddefs = {
    'NAS->EMM/ESM->EMM->Attach Request': '-1',
    'NAS->EMM/ESM->EMM->Attach Request - Rate': '-1',
}
