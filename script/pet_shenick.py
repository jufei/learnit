import os, time
from lxml import etree

from petbase import *
import pettool

temp_xml_file = '/tmp/TM500.xml'

def _build_shenick_command(clicmd=''):
    return 'sshpass -p %s ssh -p %s %s@%s  -o StrictHostKeyChecking=no  "cli -u %s -p %s %s"' %(
      gv.tm500.shenick_control_password, gv.tm500.shenick_control_port,
      gv.tm500.shenick_control_username, gv.tm500.shenick_control_ip,
      gv.tm500.shenick_username, gv.tm500.shenick_partition, clicmd)

def execute_shenick_cli_command(cmd):
    return run_local_command_gracely(_build_shenick_command(cmd))

def execute_shell_command_on_shenick(rcmd):
    cmd = 'sshpass -p %s ssh -p %s %s@%s "%s"' %( gv.tm500.shenick_control_password,
                                                  gv.tm500.shenick_control_port,
                                                  gv.tm500.shenick_control_username,
                                                  gv.tm500.shenick_control_ip,
                                                  rcmd)
    run_local_command_gracely(cmd)

def _build_shenick_command_local(clicmd):
    return 'cli -u %s -p %s  %s' %(gv.tm500.shenick_username, gv.tm500.shenick_partition, clicmd)

def finish_capture_packet_on_shenck():
    execute_command_on_shenick_by_ssh([_build_shenick_command_local('pcapFinish')])

def start_to_capture_packet_on_shenick(condition, duration, pcap_file):
    cmd1 = 'rm -rf ' + pcap_file
    cmd2 = _build_shenick_command_local('pcapStart Interface=%s/1/0 %s DurationSec=%s %s' %(
        str(9 + int(gv.tm500.shenick_partition)),
        condition,
        duration,
        pcap_file
        ))
    cmd3 =  _build_shenick_command_local('pcapState')
    execute_command_on_shenick_by_ssh([cmd1, cmd2, cmd3])

def stop_capture_packet_on_shenick(condition, duration, pcap_file):
    cmd = 'cli pcapStop'
    execute_shell_command_on_shenick(cmd)


def stop_running_test_group():
    output = execute_shenick_cli_command('help')
    cmd = 'showRunningTestGroup' if 'showRunningTestGroup' in output else 'showActiveState'
    output = execute_shenick_cli_command(cmd)
    gv.logger.debug(output)
    line = [x for x in output.splitlines() if '//' in x]
    if line:
        import re
        running_group =  re.findall(u'//([\S]*)', line[0])[0]
        execute_shenick_cli_command('stopTestGroup %s' %(running_group))
        record_debuginfo('Stop running test group [%s] successfully.' %(running_group))
    else:
        record_debuginfo('There is no RUNNNING test group.')


def start_test_group(groupname):
    execute_shenick_cli_command('startTestGroup %s' %(groupname))

def get_test_group_list():
    output = execute_shenick_cli_command('listTestGroups')
    return [line.split()[0].replace('//', '') for line in output.splitlines() if '//' in line and line.replace('//', '').strip()]

def test_group_exist(groupname):
    return groupname in get_test_group_list()

def delete_test_group(groupname):
    if test_group_exist(groupname):
      output = execute_shenick_cli_command('deleteTestGroup ' + groupname)
      gv.logger.info(output)

def import_test_group(groupname):
    put_file_to_shenick(temp_xml_file, 'TM500.xml')
    plfile = os.path.sep.join([resource_path(), 'config', 'case', 'TM500.pl'])
    put_file_to_shenick(plfile, 'TM500.pl')
    execute_shell_command_on_shenick('chmod +x TM500.pl')
    execute_shell_command_on_shenick('perl TM500.pl TM500.xml %s %s LTE > %s.xml' %(
                                  gv.tm500.shenick_partition, groupname, groupname))
    delete_test_group(groupname)
    execute_shenick_cli_command('importTestGroup //  %s.xml' %(groupname))

def get_shenick_test_group_detail_result(groupname, zipfile):
    execute_shenick_cli_command('saveTestGroupCurrentDetailedResults %s ta.zip' %(groupname))
    get_file_from_shenick('ta.zip', zipfile)

def get_file_from_shenick(rfilename, lfilename):
    cmd = 'sshpass -p %s scp -P %s %s@%s:%s %s' %(gv.tm500.shenick_control_password,
                                                  gv.tm500.shenick_control_port,
                                                  gv.tm500.shenick_control_username,
                                                  gv.tm500.shenick_control_ip,
                                                  rfilename,
                                                  lfilename)
    run_local_command_gracely(cmd)

def put_file_to_shenick(lfilename, rfilename):
    cmd = 'sshpass -p %s scp -P %s %s %s@%s:%s' %(gv.tm500.shenick_control_password,
                                                  gv.tm500.shenick_control_port,
                                                  lfilename,
                                                  gv.tm500.shenick_control_username,
                                                  gv.tm500.shenick_control_ip,
                                                  rfilename)
    run_local_command_gracely(cmd)

def _get_bitrate_level(bitrate_type, bitrate):
    rate_def = '''
    NB  1   4.75
    NB  2   5.15
    NB  3   5.90
    NB  4   6.70
    NB  5   7.40
    NB  6   7.95
    NB  7   10.20
    NB  8   12.20
    WB  1   6.60
    WB  2   8.85
    WB  3   12.65
    WB  4   14.25
    WB  5   15.85
    WB  6   18.25
    WB  7   19.85
    WB  8   23.05
    WB  9   23.85
    '''
    lines = [line.strip() for line in rate_def.splitlines() if line.strip()]
    lines = [line for  line in lines if line.split()[0] == bitrate_type and\
             line.split()[-1] == '%0.2f' %(float(bitrate))]
    if len(lines) == 0:
        kw('report_error', 'Could not find the bitrate level')
    else:
        return lines[0].split()[1]


def generate_shenick_group_file(maxue = 5,
                                startsipuser = '861800003874',
                                bitrate_type = 'NB',
                                bitrate_level = '3'):
    def _get_item_by_tag(tag):
        return [x for x in root.iter() if str(x.tag).upper() == tag.upper()][0]

    src_file = os.path.sep.join([resource_path(), 'config', 'case', 'TM500_template.xml'])
    tree = etree.parse(src_file)
    root = tree.getroot()
    _get_item_by_tag('Total_UEs').text = str(maxue*2)
    _get_item_by_tag('FTP_Get').attrib['UE'] = '0..%d' %(maxue*2-1)
    _get_item_by_tag('FTP_Put').attrib['UE'] = '0..%d' %(maxue*2-1)
    _get_item_by_tag('VoIP').attrib['UE'] = '1000..%d' %(1000+maxue-1)
    _get_item_by_tag('username').text = '+%s+'%(startsipuser) +r'%UE_ID%'
    gv.logger.info('+%s+'%(startsipuser) +r'%UE_ID%')

    _get_item_by_tag('SIP_Auth_Username').text = '+%s+'%(startsipuser) +r'%UE_ID%@atcahzims.nsn.com'
    for item in [x for x in root.iter() if str(x.tag).upper() == 'TeraFlow'.upper()]:
        item.attrib['UE'] = '0..%d' %(maxue*2-1)
    _get_item_by_tag('Codec_Name').text = 'Default AMR-' + bitrate_type
    _get_item_by_tag('Codec_Type').text = 'AMR-' + bitrate_type
    _get_item_by_tag('Change_Entry').text = str(bitrate_level)
    tree.write(temp_xml_file)

def prepare_shenick_test_group(maxue = 5, groupname = ''):
    # generate_shenick_group_file(maxue)
    import_test_group(groupname)

def add_ftp_get_uegroup(startue = 0, ue_count = 10):
    node = etree.Element('FTP_Get', PDN="0", UE='%d..%d' %(startue, startue + ue_count-1))
    etree.SubElement(node, 'Server_Host_Name').text = 'ExtFTPServer'
    etree.SubElement(node, 'Path').text = '1GB.bin'
    etree.SubElement(node, 'Delay_Between_Commands').text = '200'
    etree.SubElement(node, 'Delay_Between_Sessions').text = '500'
    etree.SubElement(node, 'File_Size').text = '1073741824'
    etree.SubElement(node, 'FTP_Mode').text = 'Passive'
    return node

def add_ftp_put_uegroup(startue = 0, ue_count = 10):
    node = etree.Element('FTP_Put', PDN="0", UE='%d..%d' %(startue, startue+ue_count-1))
    etree.SubElement(node, 'Server_Host_Name').text = 'ExtFTPServer'
    etree.SubElement(node, 'Path').text = ''
    etree.SubElement(node, 'Delay_Between_Commands').text = '200'
    etree.SubElement(node, 'Delay_Between_Sessions').text = '200'
    etree.SubElement(node, 'Ftp_Put_Path_Shared').text = 'ftpupload/1GB.bin'
    etree.SubElement(node, 'File_Size').text = '1073741824'
    etree.SubElement(node, 'FTP_Mode').text = 'Passive'
    return node

def add_udp_upload_uegroup(startue = 0, ue_count = 10):
    node = etree.Element('TeraFlow', PDN="0", UE='%d..%d' %(startue, startue+ue_count-1))
    etree.SubElement(node, 'Alias').text = 'UL_UDP'
    etree.SubElement(node, 'Server_Host_Name').text = 'ExtTFServer'
    etree.SubElement(node, 'Start_After').text = '10'
    etree.SubElement(node, 'Stop_After').text = '6000'
    etree.SubElement(node, 'Throughput').text = '1'
    etree.SubElement(node, 'Throughput_Metric').text = 'mbps'
    etree.SubElement(node, 'TeraFlow_Payload_Size').text = '8192'
    etree.SubElement(node, 'Number_of_Sessions').text = '1'
    return node

def add_udp_download_uegroup(startue = 0, ue_count = 10):
    node = etree.Element('TeraFlow', PDN="0", UE='%d..%d' %(startue, startue+ue_count-1))
    etree.SubElement(node, 'Alias').text = 'DL_UDP'
    etree.SubElement(node, 'Server_Host_Name').text = 'ExtTFServer'
    etree.SubElement(node, 'Server_on_PPPoE').text = 'true'
    etree.SubElement(node, 'Start_After').text = '10'
    etree.SubElement(node, 'Stop_After').text = '6000'
    etree.SubElement(node, 'Throughput').text = '4096'
    etree.SubElement(node, 'TeraFlow_Payload_Size').text = '8192'
    etree.SubElement(node, 'Number_of_Sessions').text = '1'
    return node

def add_volte_uegroup(startue = 0, ue_count = 10, start_sip_number = '861800003874',
                      bitrate_type = 'NB', bitrate_level = '3'):
    node = etree.Element('VoIP', PDN="1", UE='%d..%d' %(startue, startue+ue_count-1))

    sip_server = etree.Element('SIP_Server')
    etree.SubElement(sip_server, 'Server_Host_Name').text = 'ExtVoIPServer'
    etree.SubElement(sip_server, 'Username').text = '+%s+%%UE_ID%%' %(start_sip_number)
    etree.SubElement(sip_server, 'Password').text = 'ims123456'
    etree.SubElement(sip_server, 'Domain').text = 'atcahzims.nsn.com'
    etree.SubElement(sip_server, 'SIP_Transport_Type').text = 'TCP'
    etree.SubElement(sip_server, 'SIP_Auth_Username').text = '+%s' %(start_sip_number) + '+%UE_ID%@atcahzims.nsn.com'
    node.append(sip_server)

    etree.SubElement(node, 'Call_Duration').text = '7200000'
    etree.SubElement(node, 'Initial_Call_Delay').text = '1000'

    media_profile = etree.Element('VoIP_Media_Profile')
    etree.SubElement(media_profile, 'Media_Type').text = 'Multimedia'
    etree.SubElement(media_profile, 'RTP_Data').text = 'Full Duplex'
    etree.SubElement(media_profile, 'Silence_Suppression').text = 'true'
    etree.SubElement(media_profile, 'Silence_Ratio').text = '50'
    etree.SubElement(media_profile, 'Silence_Length').text = '10000'
    codec = etree.Element('Codec')
    etree.SubElement(codec, 'Codec_Name').text = 'Default AMR-' + bitrate_type
    media_profile.append(codec)

    amr_list = etree.Element('Adaptive_AMR_List')
    etree.SubElement(amr_list, 'Codec_Type').text = 'AMR-'+ bitrate_type
    etree.SubElement(amr_list, 'Use_Default_List').text = 'true'
    etree.SubElement(amr_list, 'Change_Interval').text = '40'
    change_list = etree.Element('Change_List')
    etree.SubElement(change_list, 'Change_Entry').text = bitrate_level
    amr_list.append(change_list)
    media_profile.append(amr_list)
    node.append(media_profile)

    etree.SubElement(node, 'Allow_Delay_Between_Calls').text = 'false'
    etree.SubElement(node, 'Mobile_Originated_Pattern').text = 'Even'
    etree.SubElement(node, 'Destination_Call_URI_Is_SIP').text = 'true'

    voip_passive_analysis = etree.Element('VoIP_Passive_Analysis', Pattern = 'List')
    etree.SubElement(voip_passive_analysis, 'Playout_Jitter').text = '40'
    etree.SubElement(voip_passive_analysis, 'Max_Jitter').text = '80'
    etree.SubElement(voip_passive_analysis, 'Media_Type').text = 'Voice'
    node.append(voip_passive_analysis)
    return node

def generate_tm500_xml_file(filename, service_list=[]):
    def _get_item_by_tag(tag):
        return [x for x in root.iter() if str(x.tag).upper() == tag.upper()][0]

    src_file = os.path.sep.join([resource_path(), 'config', 'case', 'TM500_empty.xml'])
    tree = etree.parse(src_file)
    root = tree.getroot()
    default_node = [x for x in root.iter() if str(x.tag).upper() == 'Default'.upper()][0]
    ue_count = 0
    for service in service_list:
        if service.name.upper() == 'ftp_get'.upper():
            default_node.append(add_ftp_get_uegroup(int(service.startue), int(service.ue_count)))
        if service.name.upper() == 'ftp_put'.upper():
            default_node.append(add_ftp_put_uegroup(int(service.startue), int(service.ue_count)))
        if service.name.upper() == 'udp_upload'.upper():
            default_node.append(add_udp_upload_uegroup(int(service.startue), int(service.ue_count)))
        if service.name.upper() == 'udp_download'.upper():
            default_node.append(add_udp_download_uegroup(int(service.startue), int(service.ue_count)))
        if service.name.upper() == 'volte'.upper():
            default_node.append(add_volte_uegroup(int(service.startue), int(service.ue_count),
                service.start_sip_number, service.bitrate_type, service.bitrate_level))
            _get_item_by_tag('PDNs_per_UE').text = '2'
        ue_count = ue_count + int(service.ue_count)

    _get_item_by_tag('Total_UEs').text = str(ue_count)
    tree.write(filename)

def provision_shenick_group():
    if gv.shenick_groups:
        generate_tm500_xml_file(temp_xml_file, gv.shenick_groups)
        import_test_group('TA_GROUP')

def execute_command_on_shenick_by_ssh(command_list):
    conn = connections.connect_to_ssh_host(gv.tm500.shenick_control_ip,
                                           gv.tm500.shenick_control_port,
                                           gv.tm500.shenick_control_username,
                                           gv.tm500.shenick_control_password,
                                           '$')
    connections.switch_ssh_connection(conn)
    output = ''
    for command in command_list:
        print command
        output += connections.execute_ssh_command_without_check(command)
    connections.disconnect_from_ssh()
    return output



def test_kw():
    # cmd = 'sshpass -p diversifEye ssh -p 2322 cli@10.69.71.229 "cli -u tm500 -p 6 %s"' %('showRunningTestGroup')
    # cmd = 'sshpass -p diversifEye scp -P 2322 cli@10.69.71.229:ta.zip /tmp/a.zip'
    # # cmd = 'sshpass -p diversifEye scp -P 2322 cli@10.69.71.229:ta.zip /home/work/Jenkins_local/workspace/TL16_VOLTE/20151211_1827/TA.TL16FSIH.OBSAI.CAP_00142_15M_ULDL1_SSF7_TM3_VOLTE_LTE1406__2015_12_11__18_28_56/P_DATA_NO1/MonitorData_2015_12_11__18_42_25.zip'
    # cmd = "sshpass -p 'oZPS0POrRieRtu' scp toor4nsn@10.69.65.97:/flash/FileDirectory.xml /home/work/Jenkins_local/workspace/TL16_VOLTE/20151211_1827/TA.TL16FSIH.OBSAI.CAP_00142_15M_ULDL1_SSF7_TM3_VOLTE_LTE1406__2015_12_11__18_28_56/BTS228/FileDirectory.xml"
    # output = os.popen(cmd).readlines()

    # import pettool
    # print pettool.ssh_is_enable('10.69.65.97', '22', 'toor4nsn', 'oZPS0POrRieRtu')
    print time.ctime()
    prepare_shenick_test_group(maxue=400, group_name='TA_Jufei')
    print time.ctime()

if __name__ == '__main__':
    # generate_shenick_group_file()
    # g1 = IpaMmlItem()
    # g1.name = 'ftp_get'
    # g1.startue = 23
    # g1.ue_count = 34

    # g2 = IpaMmlItem()
    # g2.name = 'ftp_put'
    # g2.startue = 2
    # g2.ue_count = 55

    # g3 = IpaMmlItem()
    # g3.name = 'volte'
    # g3.startue = 0
    # g3.ue_count = 10
    # g3.start_sip_number = '861800003874'
    # g3.bitrate_type = 'NB'
    # g3.bitrate_level = '3'

    # generate_tm500_xml_file('/tmp/TM500.xml', [g1, g2, g3])

    pass
