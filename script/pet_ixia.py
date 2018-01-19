import os, time, telnetlib
from thread import *
from petbase import *
import pettool
import math
sys.path.append('/home/work/tacase/ixialib')

def connect_to_ixia_control_pc():
    gv.logger.info(gv.ixia.control_pc_lab)
    if not gv.ixia.conn_pc or not ixia_control_pc_conn_is_available():
        gv.ixia.conn_pc = connections.connect_to_host(gv.ixia.control_pc_lab, '23',
            gv.ixia.control_pc_username, gv.ixia.control_pc_password)
    connections.switch_host_connection(gv.ixia.conn_pc)

def execute_command_on_ixia_control_pc(cmds):
    connect_to_ixia_control_pc()
    return connections.execute_shell_command_without_check(cmds)
    # return pettool.execute_command_on_pc(cmds)

def config_ixia_control_pc():
    if gv.env.use_ixia:
        kw('connect_to_ixia_control_pc', ['tlntadmn config timeoutactive=no', 'tlntadmn config maxconn=1000'])

def ixia_control_pc_conn_is_available():
    output = run_local_command_gracely('netstat -na|grep %s:23' %(gv.ixia.control_pc_lab))
    return 'ESTABLISHED' in output

def execute_shell_command_on_catapult(rcmd):
    gv.ixia.catapult_control_pc = "10.68.152.166"
    gv.ixia.catapult_control_pc_username = 'ManualTest'
    gv.ixia.catapult_control_pc_password = 'catapult'
    cmd = "sshpass -p %s ssh %s@%s '%s'" %( gv.ixia.catapult_control_pc_password,
                                            gv.ixia.catapult_control_pc_username,
                                            gv.ixia.catapult_control_pc,
                                            rcmd)
    output = run_local_command_gracely(cmd)
    return output

def read_ixia_config(ixia_id):
    ixiapath = os.path.sep.join([resource_path(), 'config', 'ixia'])
    import sys, importlib
    sys.path.append(ixiapath)
    model = importlib.import_module('ixia_%s'%(ixia_id))
    ixiaconfig = IpaMmlItem()
    for key in model.TOOLS_VAR:
        setattr(ixiaconfig, key.lower(), model.TOOLS_VAR[key])
    ixiaconfig.conn_pc = None
    ixiaconfig.conn_catapult_pc = None
    return ixiaconfig

def genrate_running_config(ixia_id, filename):
    config = read_ixia_config(ixia_id)
    lines = []
    case = gv.case.curr_case
    traffic_ue_num,traffic_ue_3cc_num,traffic_ue_ca_num,traffic_ue_nca_num = pet_traffic_ue_count(case.ue_count)
    traffic_time = int(case.case_duration) + 360
    traffic_dl_rate_mbps,traffic_dl_rate_3cc,traffic_dl_rate_ca,traffic_dl_rate_nca = pet_traffic_dl_rate_mbps()
    traffic_ul_rate_mbps,traffic_ul_rate_3cc,traffic_ul_rate_ca,traffic_ul_rate_nca = pet_traffic_ul_rate_mbps(traffic_ue_num)
    traffic_dl_rate_qci6,traffic_dl_rate_qci7,traffic_dl_rate_qci8 = pet_traffic_mdrb(traffic_dl_rate_mbps)
    traffic_ul_rate_qci6,traffic_ul_rate_qci7,traffic_ul_rate_qci8 = pet_traffic_mdrb(traffic_ul_rate_mbps)
    traffic_dl_rate_ca_qci6,traffic_dl_rate_ca_qci7,traffic_dl_rate_ca_qci8 = pet_traffic_mdrb(traffic_dl_rate_ca)
    traffic_ul_rate_ca_qci6,traffic_ul_rate_ca_qci7,traffic_ul_rate_ca_qci8 = pet_traffic_mdrb(traffic_ul_rate_ca)
    traffic_dl_rate_nca_qci6,traffic_dl_rate_nca_qci7,traffic_dl_rate_nca_qci8 = pet_traffic_mdrb(traffic_dl_rate_nca)
    traffic_ul_rate_nca_qci6,traffic_ul_rate_nca_qci7,traffic_ul_rate_nca_qci8 = pet_traffic_mdrb(traffic_ul_rate_nca)
    traffic_ue_3cc_2cc_num = int(traffic_ue_3cc_num) + int(traffic_ue_ca_num)
    pppoe_client_service_name_3cc  = config.pppoe_client_service_name
    pppoe_client_service_name_ca  = config.pppoe_client_service_name.replace("Inc:0","Inc:%s") %(traffic_ue_3cc_num)
    pppoe_client_service_name_nca = config.pppoe_client_service_name.replace("Inc:0","Inc:%s") %(traffic_ue_3cc_2cc_num)

    for attr in [x for x in dir(config) if not x.startswith('_')]:
        if type(getattr(config, attr)) is list:
            lines.append('{}    =   {}'.format(attr, getattr(config, attr)))
        else:
            lines.append('{}    =   "{}"'.format(attr, getattr(config, attr)))

    lines.append('pppoe_client_ue_number    =    {}'.format(traffic_ue_num))
    lines.append('traffic_time    =    {}'.format(traffic_time))
    lines.append('traffic_dl_rate_mbps   =    {}'.format(traffic_dl_rate_mbps))
    lines.append('traffic_ul_rate_mbps   =    {}'.format(traffic_ul_rate_mbps))
    lines.append('pppoe_client_ue_3cc_number =    {}'.format(traffic_ue_3cc_num))
    lines.append('pppoe_client_ue_ca_number =    {}'.format(traffic_ue_ca_num))
    lines.append('pppoe_client_ue_nca_number =    {}'.format(traffic_ue_nca_num))
    lines.append('traffic_dl_rate_3cc_mbps   =    {}'.format(traffic_dl_rate_3cc))
    lines.append('traffic_ul_rate_3cc_mbps   =    {}'.format(traffic_ul_rate_3cc))
    lines.append('traffic_dl_rate_ca_mbps   =    {}'.format(traffic_dl_rate_ca))
    lines.append('traffic_ul_rate_ca_mbps   =    {}'.format(traffic_ul_rate_ca))
    lines.append('traffic_dl_rate_nca_mbps   =    {}'.format(traffic_dl_rate_nca))
    lines.append('traffic_ul_rate_nca_mbps   =    {}'.format(traffic_ul_rate_nca))
    lines.append('traffic_dl_rate_qci6_mbps   =    {}'.format(traffic_dl_rate_qci6))
    lines.append('traffic_dl_rate_qci7_mbps   =    {}'.format(traffic_dl_rate_qci7))
    lines.append('traffic_dl_rate_qci8_mbps   =    {}'.format(traffic_dl_rate_qci8))
    lines.append('traffic_ul_rate_qci6_mbps   =    {}'.format(traffic_ul_rate_qci6))
    lines.append('traffic_ul_rate_qci7_mbps   =    {}'.format(traffic_ul_rate_qci7))
    lines.append('traffic_ul_rate_qci8_mbps   =    {}'.format(traffic_ul_rate_qci8))
    lines.append('traffic_dl_rate_ca_qci6_mbps   =    {}'.format(traffic_dl_rate_ca_qci6))
    lines.append('traffic_dl_rate_ca_qci7_mbps   =    {}'.format(traffic_dl_rate_ca_qci7))
    lines.append('traffic_dl_rate_ca_qci8_mbps   =    {}'.format(traffic_dl_rate_ca_qci8))
    lines.append('traffic_ul_rate_ca_qci6_mbps   =    {}'.format(traffic_ul_rate_ca_qci6))
    lines.append('traffic_ul_rate_ca_qci7_mbps   =    {}'.format(traffic_ul_rate_ca_qci7))
    lines.append('traffic_ul_rate_ca_qci8_mbps   =    {}'.format(traffic_ul_rate_ca_qci8))
    lines.append('traffic_dl_rate_nca_qci6_mbps   =    {}'.format(traffic_dl_rate_nca_qci6))
    lines.append('traffic_dl_rate_nca_qci7_mbps   =    {}'.format(traffic_dl_rate_nca_qci7))
    lines.append('traffic_dl_rate_nca_qci8_mbps   =    {}'.format(traffic_dl_rate_nca_qci8))
    lines.append('traffic_ul_rate_nca_qci6_mbps   =    {}'.format(traffic_ul_rate_nca_qci6))
    lines.append('traffic_ul_rate_nca_qci7_mbps   =    {}'.format(traffic_ul_rate_nca_qci7))
    lines.append('traffic_ul_rate_nca_qci8_mbps   =    {}'.format(traffic_ul_rate_nca_qci8))
    lines.append('pppoe_client_service_name_3cc    =    "{}"'.format(pppoe_client_service_name_3cc))
    lines.append('pppoe_client_service_name_ca    =    "{}"'.format(pppoe_client_service_name_ca))
    lines.append('pppoe_client_service_name_nca    =    "{}"'.format(pppoe_client_service_name_nca))

    gv.logger.info(filename)
    with open(filename, 'w') as f:
        for line in lines:
            print line
            f.write(line+'\n')

def ixia_setup():
    gv.logger.info('IXIA SETUP')
    gv.ixia = kw('read_ixia_config',pv('IXIA_ID'))
    kw('start_hltapi_if_needed')
    if gv.env.use_catapult and gv.case.curr_case.ue_is_m678:
        gv.logger.info('Restart Catapult')
        kw('restart_catapult')

def _start_hltapi():
    connect_to_ixia_control_pc()
    htlapi_dir = gv.ixia.tcl_api_path
    pmstr = ' -tclPort 8009 -restPort 11009 -restOnAllInterfaces'
    hltapipath = '"%s" %s' %(htlapi_dir, pmstr)
    client = r'C:\\Python27\\lib\\site-packages\\BtsShell\\resources\\tools\\Server_Client\\client.exe'
    cmd  = '"%s" localhost %s \n' %(client, hltapipath)
    gv.logger.info(cmd)
    try:
        connections.execute_shell_command_without_check(cmd)
    except:
        pass
    kw('wait_until_port_is_listening', '8009', '60')
    gv.ixia.conn_hltapi = None

def _kill_hltapi():
    connect_to_ixia_control_pc()
    kw("kill_process", ['IxNetwork.exe', 'IxNetwork.RBProtocols.exe', 'IxNetwork.LMHost.exe', 'IxNetwork.TestAssistant.exe', 'IxStatsService.exe'])

def _hltapi_is_running():
    output = execute_command_on_ixia_control_pc('tasklist |grep IxNetwork')
    for line in output.splitlines():
        if 'IxNetwork.exe'.lower() in line.lower():
            return True
    return False

def _hltapi_is_listening():
    output = execute_command_on_ixia_control_pc('netstat -na|grep 8009')
    return 'LISTEN' in output

def start_hltapi_if_needed():
    if _hltapi_is_listening():
        kw('log', 'HLTAPI is listening.')
    else:
        kw('log', 'HLTAPI is not running, TA will start it')
        _kill_hltapi()
        _start_hltapi()

def _kill_catapult():
    output = execute_shell_command_on_catapult('ps -ef|grep ddrive')
    for line in [x for x in output.splitlines() if "ddriver" in x]:
        pid = line.split()[1]
        gv.logger.info('catapult kill pid=%s' %(pid))
        execute_shell_command_on_catapult('kill -9 %s' %(pid))
    output = execute_shell_command_on_catapult('ps -ef|grep launch')
    for line in [x for x in output.splitlines() if "launch" in x or "display" in x]:
        pid = line.split()[1]
        gv.logger.info('catapult kill pid=%s' %(pid))
        execute_shell_command_on_catapult('kill -9 %s' %(pid))

def _start_catapult():
    catapult_display_port = pv('CATAPULT_DISPLAY')
    gv.logger.info('catapult display port =%s' %(catapult_display_port))
    launchcmd  = 'bash -c "export DISPLAY=%s; /home/dct2000/21.0_LTE/launch -a /home/ManualTest/Total_NSN/EPC_NSN_Single.lch -r"' %(catapult_display_port)  
    catacmd= "nohup sshpass -p %s ssh %s@%s '%s' >/home/work/catapult.log 2>&1 &" %(gv.ixia.catapult_control_pc_password,
                                            gv.ixia.catapult_control_pc_username,
                                            gv.ixia.catapult_control_pc,
                                            launchcmd)
    run_local_command_gracely(catacmd)
    time.sleep(10)
    launch_output = run_local_command_gracely('cat /home/work/catapult.log')
    run_local_command_gracely('sshpass -p catapult scp ManualTest@10.68.152.166:/home/ManualTest/Total_NSN/MME25_3.out /home/work/')
    mme_output = run_local_command_gracely('cat /home/work/MME25_3.out')
    if "Complete" in launch_output: 
        gv.logger.info('launch complete')
    else:
        kw('report_error','restart catapult fail!')
    if "init enb fail" in mme_output:
        kw('report_error','catapult init enb fail!')
    else:
        gv.logger.info('mme complete')

def restart_catapult():
    _kill_catapult()
    _start_catapult()
    time.sleep(120)
    
def pet_ixia_start():
    gv.logger.info ('START IXIA')
    case = gv.case.curr_case
    genrate_running_config(gv.ixia.ixia_id, case_file('ixia.py'))

    if (case.ue_has_nca and case.ue_is_ca and not case.ue_is_3cc) or (case.ue_is_3cc and case.ue_is_ca and not case.ue_has_nca):
        module_file = 'pet_ixia_ca_nca.py'
    elif case.ue_has_nca and case.ue_is_ca and case.ue_is_3cc:
        module_file = 'pet_ixia_3cc_ca_nca.py'
    else:
        module_file = 'pet_ixia_pure.py'

    if case.ue_is_m678:
        if case.ue_has_nca and case.ue_is_ca:
            module_file = 'pet_ixia_678_ca_nca.py'
        else:
            module_file = 'pet_ixia_678_pure.py'

    cmd = 'python %s/tools/ixia_module/%s %s > %s &' %(resource_path(), module_file, case_file('ixia.py'), case_file('ixia_run.log'))
    gv.logger.info(cmd)
    run_local_command(cmd)

def pet_traffic_ue_count(ue_count):
    traffic_ue_num = ue_count-200 if ue_count in [600, 800] else ue_count
    traffic_ue_num = 250 if ue_count == 400 else ue_count
    traffic_ue_3cc_num = int(gv.case.curr_case.ue_3cc_count)
    traffic_ue_ca_num = int(gv.case.curr_case.ue_ca_count)
    traffic_ue_nca_num = int(traffic_ue_num) - int(traffic_ue_3cc_num) - int(traffic_ue_ca_num)
    return traffic_ue_num,traffic_ue_3cc_num,traffic_ue_ca_num,traffic_ue_nca_num

def pet_traffic_dl_rate_mbps():
    case = gv.case.curr_case
    if case.traffic_3cc != 0 or case.traffic_ca != 0 or case.traffic_nca != 0:
        if case.ue_is_3cc and case.ue_is_ca and not case.ue_has_nca:#pet_ixia_ca_nca
            traffic_dl_rate_3cc = 0
            traffic_dl_rate_ca = case.traffic_3cc 
            traffic_dl_rate_nca = case.traffic_ca           
        else:
            traffic_dl_rate_3cc = case.traffic_3cc 
            traffic_dl_rate_ca = case.traffic_ca
            traffic_dl_rate_nca = case.traffic_nca
        traffic_dl_rate_mbps = int(traffic_dl_rate_3cc) + int(traffic_dl_rate_ca) + int(traffic_dl_rate_nca)
        return traffic_dl_rate_mbps,traffic_dl_rate_3cc,traffic_dl_rate_ca,traffic_dl_rate_nca
    if case.ue_is_3cc and case.ue_is_ca and case.ue_has_nca: #pet_ixia_3cc_ca_nca
        traffic_dl_rate_3cc = 200
        traffic_dl_rate_ca = 150
        traffic_dl_rate_nca = 110
    elif case.ue_is_3cc and not case.ue_is_ca and not case.ue_has_nca: #pet_ixia_pure
        traffic_dl_rate_ca = 0
        traffic_dl_rate_3cc = 400
        traffic_dl_rate_nca = 0
    elif not case.ue_is_3cc and not case.ue_is_ca and case.ue_has_nca: #pet_ixia_pure
        traffic_dl_rate_ca = 0
        traffic_dl_rate_3cc = 0
        traffic_dl_rate_nca = 120
    elif case.ue_is_3cc and case.ue_is_ca and not case.ue_has_nca: #pet_ixia_ca_nca
        traffic_dl_rate_3cc = 0
        traffic_dl_rate_ca = 240
        traffic_dl_rate_nca = 150
    elif not case.ue_is_3cc and case.ue_is_ca and  case.ue_has_nca: #pet_ixia_ca_nca
        traffic_dl_rate_3cc = 0
        traffic_dl_rate_ca = 150
        traffic_dl_rate_nca = 110
    elif not case.ue_is_3cc and case.ue_is_ca and not case.ue_has_nca: #pet_ixia_pure
        traffic_dl_rate_3cc = 0
        traffic_dl_rate_ca = 230
        traffic_dl_rate_nca = 0
    else:
        traffic_dl_rate_ca = 0
        traffic_dl_rate_3cc = 0
        traffic_dl_rate_nca = 120
    traffic_dl_rate_mbps = int(traffic_dl_rate_3cc) + int(traffic_dl_rate_ca) + int(traffic_dl_rate_nca)
    return traffic_dl_rate_mbps,traffic_dl_rate_3cc,traffic_dl_rate_ca,traffic_dl_rate_nca

def pet_traffic_ul_rate_mbps(traffic_ue_num):
    case = gv.case.curr_case
    traffic_ul_rate_mbps = 20
    if gv.master_bts.btstype == 'FDD':
        traffic_ul_rate_mbps = 30
    if case.ue_is_ulca:
        traffic_ul_rate_mbps = traffic_ul_rate_mbps*2
    # traffic_ul_rate_3cc =  int(math.ceil(float(traffic_ul_rate_mbps)*int(gv.case.curr_case.ue_3cc_count)/int(traffic_ue_num)))
    # traffic_ul_rate_ca = int(math.ceil(float(traffic_ul_rate_mbps)*int(gv.case.curr_case.ue_ca_count)/int(traffic_ue_num)))
    # traffic_ul_rate_nca =  int(math.ceil(float(traffic_ul_rate_mbps)*(int(traffic_ue_num) - int(gv.case.curr_case.ue_3cc_count) - int(gv.case.curr_case.ue_ca_count))/int(traffic_ue_num)))
    traffic_ul_rate_3cc =  40
    traffic_ul_rate_ca = 20
    traffic_ul_rate_nca =  20
    return traffic_ul_rate_mbps,traffic_ul_rate_3cc,traffic_ul_rate_ca,traffic_ul_rate_nca

def pet_traffic_mdrb(traffic_rate):
    return int(math.ceil(float(traffic_rate)/8)),int(math.ceil(float(traffic_rate)/4)),int(math.ceil(5*float(traffic_rate)/8))

if __name__ == '__main__':
    gv.ixia = read_ixia_config('8')
    gv.case.curr_case = IpaMmlItem()
    gv.case.curr_case.ue_count = 400
    gv.case.curr_case.ue_ca_count = 100
    gv.case.curr_case.ue_nca_count = 150
    gv.case.curr_case.case_duration = 3000
    gv.case.curr_case.ca_type = '2CC'
    gv.case.curr_case.ue_is_m678 = True
    gv.case.curr_case.ue_is_ulca = False
    gv.case.curr_case.ue_has_nca = True
    gv.case.curr_case.uldl = '2'
    #gv.master_bts.btstype = "TDD"
    genrate_running_config('8', '/tmp/a.py')
