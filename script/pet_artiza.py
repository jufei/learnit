import datetime, os, time
from petbase import *
import pettool

def common_suite_setup_for_tput():
    kw('common_suite_setup_for_pet')

def common_suite_teardown_for_tput():
    kw('common_suite_teardown_for_pet')

def common_test_case_setup_for_artiza():
    kw('common_test_case_setup_for_pet')
    kw('select_datadevice')
    kw('artiza_case_setup')
    gv.case.case_log_list = ['tcpdump', 'infomodel']
    kw('start_to_capture_all_kinds_of_logs')


def common_test_case_teardown_for_artiza():
    kw('run_keyword_and_ignore_error', 'cleanup_ftp_on_data_device')
    kw('run_keyword_and_ignore_error', 'pet_stop_pppoe_connection')
    kw('run_keyword_and_ignore_error', 'artiza_case_teardown')
    if gv.tm500:
        kw('run_keyword_and_ignore_error', 'pet_release_artiza_resource')
    kw('common_test_case_teardown_for_pet')


# def read_artiza_config(artiza_id):
#     artizapath = os.path.sep.join([resource_path(), 'config', 'artiza'])
#     import sys, importlib
#     sys.path.append(tm500path)
#     model = importlib.import_module('artiza_%s'%(tm500_id))
#     artizaconfig = IpaMmlItem()
#     for key in model.TOOLS_VAR:
#         setattr(artizaconfig, key.lower(), model.TOOLS_VAR[key])

#     artizaconfig.conn_pc = None
#     artizaconfig.conn_tma = None
#     artizaconfig.conn_shenick = None
#     artizaconfig.version = ''
#     artizaconfig.output = ''
#     # spv('TM500_POWERBREAK_PORT', tm500config.tm500_powerbreak_port)
#     return artizaconfig


