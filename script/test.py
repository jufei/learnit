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
import pet_prisma_c

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
    from pet_bts import read_bts_config
    gv.master_bts_c = read_bts_config(btsid)
    gv.master_bts = gv.mbts()[0]

    gv.case.curr_case = pettool.get_case_config_new(instance_id)
    from petcasebase import re_organize_case
    re_organize_case()
    print gv.case.curr_case
    pet_bts.pet_bts_read_scf_file(btsid)

    tm500path = os.path.sep.join([resource_path(), 'config', 'tm500'])
    import sys, importlib
    sys.path.append(tm500path)
    model = importlib.import_module('tm500_%s'%(tm500_id))
    tm500config = IpaMmlItem()
    for key in model.TOOLS_VAR:
        setattr(tm500config, key.lower(), model.TOOLS_VAR[key])

    tm500config.shenick_volte_group_name = 'TA_VOLTE_IMS_FTP'
    if 'volte_load' in [x.lower().strip() for x in dir(gv.case.curr_case) if x[0] <> '_']:
        if gv.case.curr_case.volte_load:
            tm500config.shenick_volte_group_name = 'TA_VOLTE_IMS_LOAD'
    if gv.case.curr_case.case_type == 'MIX_MR':
        tm500config.shenick_volte_group_name = 'TA_Mixed_UDP_FTP'
    if gv.case.curr_case.case_type.strip().upper() in ['THROUGHPUT_MUE_UL', 'THROUGHPUT_MUE_DL']:
        tm500config.shenick_volte_group_name = 'TA_MUE_UL'

    gv.tm500 = tm500config

def prepare_for_debug_for_ho(btsid = '1703', sbtsid = '537', tm500_id = '233', instance_id = '586999'):
    gv.dbfile = os.path.sep.join([resource_path(), 'config', 'case', 'database.xlsx'])
    gv.master_bts = pet_bts.read_bts_config(btsid)
    gv.slave_bts = pet_bts.read_bts_config(sbtsid, 'S', 'P')

    gv.allbts = [gv.master_bts, gv.slave_bts]
    gv.case.curr_case = pettool.get_case_config_new(instance_id)
    from petcasebase import re_organize_case
    re_organize_case()
    # print gv.case.curr_case

    for attr in [x for x in dir(gv.case.curr_case) if x[0] <> '_']:
        setattr(gv.master_bts, attr, getattr(gv.case.curr_case, attr))
        setattr(gv.slave_bts, attr, getattr(gv.case.curr_case, attr))

    pet_bts.pet_bts_read_scf_file(btsid)
    pet_bts.pet_bts_read_scf_file(sbtsid)

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
        if gv.case.curr_case.volte_load:
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
    from pet_bts import prepare_mr_parameters
    prepare_mr_parameters()
    print gv.master_bts
    from pet_tm500_script import get_tput_mue_attach_script, get_mr_mix_script, _get_volte_cap_script, get_volte_cap_script
    from pet_tm500_script import get_tput_attach_script
    # from pet_tm500_script import get_ulca_attach_script_for_tput
    from pet_tm500_script import get_tput_mue_attach_script, get_mr_mix_script, _get_volte_cap_script, get_volte_cap_script
    from pet_tm500_script import get_volte_performance_script, get_volte_tm500_script
    script = get_volte_tm500_script(gv.master_bts)
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
    prepare_for_debug_for_ho(btsid, slavebtsid, tm500_id, instance_id)
    from pet_bts import prepare_mr_parameters
    prepare_mr_parameters()

    from pet_scf_base_c import c_pet_scf_base as c_pet_scf_c, tput_scf_params, volte_scf_params, mr_sr_params

    case = gv.case.curr_case
    if case.domain == 'CPK':
        paramslist = tput_scf_params
    if case.domain == 'VOLTE':
        paramslist = volte_scf_params
    if case.domain == 'MR':
        paramslist = mr_sr_params
    if case.domain == 'TR':
        paramslist = traffic_model_sr_params
    c_scf = c_pet_scf_c(paramslist)

    print '11111111111111111'
    changes = c_scf.get_scf_params_change_list(gv.master_bts, gv.case.curr_case)
    from PetShell.file_lib.xml_control import common_xml_operation
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
        '/tmp/master.xml', accept_changes)
    ####

    print '22222222222222222222'
    btsid = gv.slave_bts.bts_id
    changes = c_scf.get_scf_params_change_list(gv.slave_bts, gv.case.curr_case)

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
    connections.connect_to_tm500('10.69.71.229')
    try:
        connections.BTSTELNET.tm500_output_file = '/home/work/jrun/CPRI_CAP_00042_10M_ULDL1_SSF7_TM3_TPUT_DRX_2PIPE__2016_04_11__10_19_01/_2PIPE_NO1/tm500cmd.log'
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

    from pet_scf_base_c import c_pet_scf_base, tput_scf_params
    scf_c = c_pet_scf_base(tput_scf_params)
    changes = scf_c.get_scf_params_change_list(gv.master_bts, gv.case.curr_case)
    # changes = get_scf_params_change_list(gv.master_bts, gv.case.curr_case)

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

def backup_config_for_suite(filename):
    def _get_suites(suite):
        if len(suite.suites) <> 0:
            return suite.suites
        else:
            return [suite]

    dest_dire = '/home/work/fileserver/library'
    result = ExecutionResult(filename)
    schecker = SuiteChecker()
    result.visit(schecker)
    psuite = schecker.suite
    result = []
    from lxml import etree
    tree = etree.parse(filename)
    suites = _get_suites(psuite)
    for asuite in suites:
        if len(asuite.suites) == 0 and asuite.status=='PASS':
            suitename = str(asuite)
            # print suitename
            suite = tree.xpath('//suite[@name="%s"]' %(suitename))[0]
            suite.xpath('.//*[contains(text(),"Suite Log directory")]')[0].text
            workdire = suite.xpath('.//*[contains(text(),"Suite Log directory")]')[0].text.split('[')[-1].replace(']', '')
            url = os.sep.join([x for x in workdire.split('workspace')[-1].split('/') if x.strip()][:2])
            url = os.sep.join([url.split(os.sep)[0], 'ws', url.split(os.sep)[1]])
            url = 'http://10.69.2.134/job/' + url
            workdire = os.sep.join(workdire.split(os.sep)[:-1])
            print url
            return workdire, url

def debug_robot(filename = '/home/work/taupload/back_by_report_server/PROCESSED_20170511012622_4682_603315_ULDL2_SSF7_20M_TM3_64QAM_41_1601__output.xml'):
    for filename in os.listdir('/home/work/taupload'):
        fullname = os.sep.join(['/home/work/taupload', filename])
        newfullname = fullname.replace('.xml', '_output.xml')

        print fullname, newfullname
        os.system('mv %s %s' %(fullname, newfullname))



import signal
import time

def test_request(arg=None):
    """Your http request."""
    time.sleep(2)
    return arg

class Timeout():
    """Timeout class using ALARM signal."""
    class Timeout(Exception):
        pass

    def __init__(self, sec):
        self.sec = sec

    def __enter__(self):
        signal.signal(signal.SIGALRM, self.raise_timeout)
        signal.alarm(self.sec)

    def __exit__(self, *args):
        signal.alarm(0)    # disable alarm

    def raise_timeout(self, *args):
        raise Timeout.Timeout()

def main_timeout():
    # Run block of code with timeouts
    with Timeout(3):
        print test_request("Request 1")
    with Timeout(1):
        print test_request("Request 2")



if __name__ == '__main__':
    # main_timeout()
    # pass
    # debug_robot()
    # path = '/home/work/taupload/back_by_report_server'
    # backup_config_for_suite('/home/work/taupload/back_by_report_server/PROCESSED_20170511012622_4682_603315_ULDL2_SSF7_20M_TM3_64QAM_41_1601__output.xml')
    # for filename in os.listdir(path):
    #     fullpath = os.sep.join([path, filename])
    #     print fullpath
    #     backup_config_for_suite(fullpath)
    # prepare_for_debug('1601', '229', '391886')
    # from pet_tm500 import get_tm500_card
    # gv.tm500_radio_card = 'RC0'
    # print gv.case.curr_case
    # print get_tm500_card()
    # debug_tm500()
    # test_for_scf('1816', '88', '670000')
    # # prepare_for_debug('642', '219', '586996')

    # from pet_bts import read_bts_config
    # gv.ms_bts = read_bts_config('537','M', 'S')
    # test_for_tm500_script_generation('239', '88', '529732') #common mr
    # test_for_tm500_script_generation('537', '229', '477167') #ho case
    # test_for_tm500_script_generation('642', '225', '472700') # volte
    # test_for_pa('642', '219', '586996')
    # test_for_shenick('228', '233', '591601')
    # test_for_scf('2150', '229', '407018') #inter mr MJ
    # test_for_scf_c('1601', '56', '280279') #inter mr MJ

    test_for_tm500_script_generation('642', '225', '555596')
    # test_for_scf('1724', '780', '603438')
    # test_for_scf('1601', '219', '603300')
    # test_for_scf2('1306', '1306', '225', '574491')
    # gv.logger.info('AAAA')
    # prepare_for_debug('1703', '219', '578077')
    # from pet_bts import pet_enable_ssh
    # bts = gv.master_bts
    # output = pet_enable_ssh(bts.bts_control_pc_lab, bts.bts_ftm_username, bts.bts_ftm_password)
    # if not 'SSH Service Enabled Successfully' in output:
    #     kw('report_error', 'Enable SSH of BTS failed, please check it first.')

    # print time.ctime()

    # g1 = IpaMmlItem()
    # g1.name = 'ftp_get'
    # g1.startue = 0
    # g1.ue_count = 10

    # g2 = IpaMmlItem()
    # g2.name = 'ftp_put'
    # g2.startue = 0
    # g2.ue_count = 10

    # g3 = IpaMmlItem()
    # g3.name = 'volte'
    # g3.startue = 0
    # g3.ue_count = 10
    # g3.start_sip_number = '861800003874'
    # g3.bitrate_type = 'NB'
    # g3.bitrate_level = '3'


    # from pet_shenick import prepare_shenick_test_group, generate_tm500_xml_file

    # generate_tm500_xml_file('/tmp/TM500.xml', [g2])

    # prepare_shenick_test_group(maxue=10, groupname='TA_GROUP')
    # print time.ctime()

    # call_cgi_script_on_ftm("protected/enableSsh.cgi", service_type="sshservice")
    # call_cgi_script_on_ftm("10.69.65.76")


    # import json
    # json.dump(scenarios, open('/tmp/data.txt', 'w'))
    # scenario = [x for x in scenarios.values() if x['id'] == 436]
    # k =  scenario[0].keys()
    # k.sort()
    # for name in k:
    #     print name
    # lines = open('pet_scf_new.py').readlines()
    # new = []
    # for line in lines:
    #     if 'def get_' in line or 'def _get_' in line:
    #         new.append(line.replace('bts', 'self, bts'))
    #     else:
    #         new.append(line)
    # with open('pet_scf_new1.py', 'w') as f:
    #     for line in new:
    #         f.write(line)
    # files = os.listdir('/home/work/taupload/back_by_report_server')
    # files = ['/home/work/taupload/back_by_report_server/'+x for x in files if 'xml' in x]
    # cmds = ['python /home/work/tacase/Resource/tools/save_run_result.py '+x for x in files]
    # print len(cmds)
    # for cmd in cmds:
    #     print cmd
    #     os.system(cmd)
    # print cmds[0]


    pass