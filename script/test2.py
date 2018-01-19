import time, os
from optparse import *
from pet_ipalib import IpaMmlItem, IpaMmlDict

import petbase
import petcasebase
import pettool
import pet_tput
import pet_volte
import pet_mr
import pet_ta_config
import pet_bts
import pet_datadevice
import pet_tm500
import pet_tm500_script
import pet_pa_c
import pet_prisma_mng
import pet_mix_cap
import pet_scf_c_pet2

from robot.api import ExecutionResult, ResultVisitor

def loginfo(istr):
    print str(istr)

class SuiteChecker(ResultVisitor):
    def __init__(self):
        self.suite = None

    def visit_suite(self, suite):
        self.suite = suite

class CaseChecker(ResultVisitor):
    def __init__(self):
        self.case_count = 0
        self.fail_reason = []
        self.tests = []
        self.result = []
    def visit_test(self, test):
        self.tests.append(test)

from petbase import *

def prepare_for_debug(btsid = '1703', tm500_id = '233', instance_id = '586999'):
    gv.dbfile = os.path.sep.join([resource_path(), 'config', 'case', 'databasepet3.xlsx'])
    gv.team = 'PET2'
    gv.master_bts_c = pet_bts.read_bts_config(btsid)
    gv.master_bts = gv.master_bts_c if gv.master_bts_c.btsmode <> 'C' else gv.master_bts_c.btslist[0]
    gv.case.curr_case = pettool.get_case_config_new(instance_id)
    from petcasebase import re_organize_case
    re_organize_case()
    for attr in [x for x in dir(gv.case.curr_case) if x[0] <> '_']:
        setattr(gv.master_bts, attr, getattr(gv.case.curr_case, attr))
    gv.master_bts.case = gv.case.curr_case
    print gv.case.curr_case

    pet_bts.pet_bts_read_scf_file()

    tm500path = os.path.sep.join([resource_path(), 'config', 'tm500'])
    import sys, importlib
    sys.path.append(tm500path)
    model = importlib.import_module('tm500_%s'%(tm500_id))
    tm500config = IpaMmlItem()
    for key in model.TOOLS_VAR:
        setattr(tm500config, key.lower(), model.TOOLS_VAR[key])

    tm500config.shenick_volte_group_name = 'TA_VOLTE_IMS_FTP'
    # if gv.case.curr_case.codec.strip():
    #     tm500config.shenick_volte_group_name += '_' + gv.case.curr_case.codec.upper()
    # if 'volte_load' in [x.lower().strip() for x in dir(gv.case.curr_case) if x[0] <> '_']:
    #     if gv.case.curr_case.volte_load.strip():
    #         tm500config.shenick_volte_group_name = 'TA_VOLTE_IMS_LOAD'
    if gv.case.curr_case.case_type == 'MIX_MR':
        tm500config.shenick_volte_group_name = 'TA_Mixed_UDP_FTP'
    if gv.case.curr_case.case_type.strip().upper() in ['THROUGHPUT_MUE_UL', 'THROUGHPUT_MUE_DL']:
        tm500config.shenick_volte_group_name = 'TA_MUE_UL'

    gv.tm500 = tm500config

def prepare_for_debug_for_ho(btsid = '1703', sbtsid = '537', tm500_id = '233', instance_id = '586999'):
    gv.dbfile = os.path.sep.join([resource_path(), 'config', 'case', 'database.xlsx'])
    gv.master_bts = pet_bts.read_bts_config(btsid)
    gv.slave_bts = pet_bts.read_bts_config(sbtsid)

    gv.allbts = [gv.master_bts, gv.slave_bts]
    gv.case.curr_case = pettool.get_case_config(instance_id)
    from petcasebase import re_organize_case
    re_organize_case()
    print gv.case.curr_case

    for attr in [x for x in dir(gv.case.curr_case) if x[0] <> '_']:
        setattr(gv.master_bts, attr, getattr(gv.case.curr_case, attr))
        setattr(gv.slave_bts, attr, getattr(gv.case.curr_case, attr))

    pet_bts.pet_bts_read_scf_file(sbtsid)
    pet_bts.pet_bts_read_scf_file()

    tm500path = os.path.sep.join([resource_path(), 'config', 'tm500'])
    import sys, importlib
    sys.path.append(tm500path)
    model = importlib.import_module('tm500_%s'%(tm500_id))
    tm500config = IpaMmlItem()
    for key in model.TOOLS_VAR:
        setattr(tm500config, key.lower(), model.TOOLS_VAR[key])

    tm500config.shenick_volte_group_name = 'TA_VOLTE_IMS_FTP'
    if gv.case.curr_case.codec.strip():
        tm500config.shenick_volte_group_name += '_' + gv.case.curr_case.codec.upper()
    if 'volte_load' in [x.lower().strip() for x in dir(gv.case.curr_case) if x[0] <> '_']:
        if gv.case.curr_case.volte_load.strip():
            tm500config.shenick_volte_group_name = 'TA_VOLTE_IMS_LOAD'
    if gv.case.curr_case.case_type == 'MIX_MR':
        tm500config.shenick_volte_group_name = 'TA_Mixed_UDP_FTP'
    if gv.case.curr_case.case_type.strip().upper() in ['THROUGHPUT_MUE_UL', 'THROUGHPUT_MUE_DL']:
        tm500config.shenick_volte_group_name = 'TA_MUE_UL'
    gv.tm500 = tm500config



def test_for_tm500_script_generation(btsid = '1703', tm500_id = '219', instance_id = '586999', sbtsid = ''):
    if sbtsid:
        prepare_for_debug_for_ho(btsid, sbtsid, tm500_id, instance_id)
    else:
        prepare_for_debug(btsid, tm500_id, instance_id)
    print gv.master_bts
    from pet_tm500_script import get_mix_cap_script
    script = get_mix_cap_script(gv.master_bts)
    gv.logger.info('SCRIPT GENERATED:')
    for line in script:
        print line

def test_for_scf(btsid = '1412', tm500_id = '219', instance_id = '586999'):
    prepare_for_debug(btsid, tm500_id, instance_id)
    from pet_bts import prepare_mr_parameters
    prepare_mr_parameters()
    from pet_scf_manager import pet_scf_manager
    scf_manager = pet_scf_manager(gv.case.curr_case, gv.master_bts)
    changes = scf_manager.gene_change_list()


    from PetShell.file_lib.xml_control import common_xml_operation, ParseXML
    print pathc(bts_source_file(btsid, gv.case.curr_case.scf_file))
    accept_changes = [x for x in changes if not 'delete' in x]
    for change in [x for x in changes if 'delete' in x]:
        try:
            common_xml_operation(pathc(bts_source_file(btsid, gv.case.curr_case.scf_file)), '/tmp/dest_scf', [change])
            accept_changes.append(change)
        except:
            print 'Process  [%s] error' %(change)
            pass

    common_xml_operation(pathc(bts_source_file(btsid, gv.case.curr_case.scf_file)),
            '/home/work/temp/new.xml', accept_changes)

def test_for_scf2(btsid = '642', slavebtsid='1111', tm500_id = '219', instance_id = '586999'):
    prepare_for_debug_for_ho(btsid, slavebtsid, '219', instance_id)
    from pet_bts import prepare_mr_parameters
    prepare_mr_parameters()

    from pet_scf import get_scf_params_change_list
    changes = get_scf_params_change_list(gv.master_bts)
    from BtsShell.file_lib.xml_control import common_xml_operation
    print pathc(bts_source_file(btsid, gv.case.curr_case.scf_file))
    accept_changes = [x for x in changes if not 'delete' in x]
    for change in [x for x in changes if 'delete' in x]:
        try:
            common_xml_operation(pathc(bts_source_file(btsid, gv.case.curr_case.scf_file)), '/tmp/dest_scf', [change])
            accept_changes.append(change)
        except:
            print 'Process  [%s] error' %(change)
            pass

    from pet_scf import show_scf_change_list
    print 'Real Change:'
    show_scf_change_list(accept_changes)
    common_xml_operation(pathc(bts_source_file(btsid, gv.case.curr_case.scf_file)),
        '/tmp/master.xml', accept_changes)
    ####
    btsid = gv.slave_bts.bts_id
    changes = get_scf_params_change_list(gv.slave_bts)
    from BtsShell.file_lib.xml_control import common_xml_operation
    print pathc(bts_source_file(btsid, gv.case.curr_case.scf_file))
    accept_changes = [x for x in changes if not 'delete' in x]
    for change in [x for x in changes if 'delete' in x]:
        try:
            common_xml_operation(pathc(bts_source_file(btsid, gv.case.curr_case.scf_file)), '/tmp/dest_scf', [change])
            accept_changes.append(change)
        except:
            print 'Process  [%s] error' %(change)
            pass

    from pet_scf import show_scf_change_list
    print 'Real Change:'
    show_scf_change_list(accept_changes)
    common_xml_operation(pathc(bts_source_file(btsid, gv.case.curr_case.scf_file)),
        '/tmp/slave.xml', accept_changes)

def test_for_shenick(btsid = '1815', tm500_id = '229', instance_id = '586999'):
    prepare_for_debug(btsid, tm500_id, instance_id)
    from pet_tm500_script import _get_volte_cap_script, get_volte_cap_script
    script = _get_volte_cap_script(gv.master_bts)
    for line in script:
        print line
    from pet_shenick import provision_shenick_group
    provision_shenick_group()

def debug_tm500():
    connections.connect_to_tm500('10.69.67.157')
    try:
        connections.BTSTELNET.tm500_output_file = '/home/work/amy/tm500cmd.log'
        
        output = connections.execute_tm500_command_without_check('#$$START_LOGGING')
        print output
        connections.execute_tm500_command_without_check('HELP')
        connections.execute_tm500_command_without_check('$$DISCONNECT')
    finally:
        connections.disconnect_all_hosts()

def lfiles(workdire):
    for filename in os.listdir(workdire):
        fullname = os.sep.join([workdire, filename])
        if os.path.isfile(fullname):
            lines = open(fullname).readlines()
            if [line for line in lines if '10.69' in line]:
                print '******  '+fullname
                for line in [line for line in lines if '10.69' in line]:
                    print line
        else:
            lfiles(fullname)

def doit():
    lfiles('/home/user/lte_s1_v3e')

def test_for_scf_c(btsid, tm500_id, instance_id):
    prepare_for_debug(btsid, tm500_id, instance_id)

    from pet_scf_c_pet2 import c_pet_scf_c, mix_cap_scf_params
    scf_c = c_pet_scf_c(mix_cap_scf_params)
    changes = scf_c.get_scf_params_change_list(gv.master_bts, gv.case.curr_case)

    from PetShell.file_lib.xml_control import common_xml_operation, ParseXML
    print pathc(bts_source_file(btsid, gv.case.curr_case.scf_file))
    accept_changes = [x for x in changes if not 'delete' in x]
    for change in [x for x in changes if 'delete' in x]:
        try:
            common_xml_operation(pathc(bts_source_file(btsid, gv.case.curr_case.scf_file)), '/tmp/dest_scf', [change])
            accept_changes.append(change)
        except:
            print 'Process  [%s] error' %(change)
            pass

    from pet_scf import show_scf_change_list
    print 'Real Change:'
    show_scf_change_list(accept_changes)
    common_xml_operation(pathc(bts_source_file(btsid, gv.case.curr_case.scf_file)),
        '/home/work/temp/new.xml', accept_changes)

def test():
    import pet_scf_base_c
    from pet_scf_base_c import c_pet_scf_base, scf_parameters, tput_scf_params
    from pet_scf_c_pet2 import mix_cap_scf_params as pmlist, c_pet_scf_c as c_scf, pet2_scf_pms
    import inspect
    pmlist.sort()
    funmap = scf_parameters
    for item in pet2_scf_pms:
        if item in funmap:
            pass

    for param in pmlist:
        funname = 'get_' + param
        attrlist = [x for x in dir(c_scf) if x.startswith('get_')]
        low_attrlist = [x.lower() for x in attrlist]
        print low_attrlist
        index = low_attrlist.index(funname.lower())
        real_funname = attrlist[index]
        lines = inspect.getsourcelines(getattr(c_scf, real_funname))[0]
        # print type(lines)
        # print lines
        print '\nParameter : ', param
        for line in lines:
            print line.replace('\n', '')


if __name__ == '__main__':
    #test()
    test_for_scf('1491', '8', '569527')
    #gv.env.use_ixia = 'true'
    #test_for_tm500_script_generation('1324', '180', '123456')


    pass