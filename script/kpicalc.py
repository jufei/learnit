import os
from petbase import *

latency_t3_define = '''
            15  0   4   13  3
            15  0   9   8   1
            15  1   4   12  2
            15  2   4   11  3
            15  3   4   10  3
            15  4   4   9   2
            15  4   9   14  3
            15  5   4   8   1
            15  5   9   13  3
            15  6   9   12  3
            15  7   9   11  3
            15  8   9   10  3
            15  9   4   14  3
            15  9   9   9   2
            17  0   4   13  2
            17  0   9   8   1
            17  1   4   12  2
            17  2   4   11  2
            17  3   4   10  2
            17  4   4   9   2
            17  4   9   14  2
            17  5   4   8   1
            17  5   9   13  2
            17  6   9   12  2
            17  7   9   11  2
            17  8   9   10  2
            17  9   4   14  2
            17  9   9   9   2
            25  0   3   12  2
            25  1   3   11  2
            25  2   3   10  2
            25  3   3   9   2
            25  3   8   14  2
            25  4   3   8   1
            25  4   8   13  2
            25  5   8   12  2
            25  6   8   11  2
            25  7   8   10  2
            25  8   3   14  2
            25  8   8   9   2
            25  9   3   13  2
            25  9   8   8   1
            27  0   3   12  1
            27  0   9   8   1
            27  1   3   11  1
            27  2   3   10  1
            27  3   3   9   1
            27  3   8   13  1
            27  4   3   8   1
            27  4   8   13  1
            27  5   8   12  1
            27  6   8   11  1
            27  7   8   10  1
            27  8   3   14  1
            27  8   8   9   1
            27  9   3   13  1
            27  9   8   8   1

'''

latency_t4_define = '''
            15  2   4   11  2
            15  3   4   10  1
            15  3   9   15  3
            15  7   9   11  2
            15  8   4   15  3
            15  8   9   10  1
            17  2   4   11  2
            17  3   4   10  1
            17  3   9   15  2
            17  7   9   11  2
            17  8   4   15  3
            17  8   9   10  1
            25  2   3   10  1
            25  2   8   15  2
            25  7   3   15  2
            25  7   8   10  1
            27  2   3   10  1
            27  2   8   15  1
            27  7   3   15  1
            27  7   8   10  1


'''

trigger_t3_define = '''
            15  0   4   13  2
            15  1   4   12  1
            15  4   9   14  3
            15  5   9   13  2
            15  6   9   12  1
            15  9   4   14  3
            17  0   4   13  2
            17  1   4   12  1
            17  4   9   14  2
            17  5   9   13  2
            17  6   9   12  1
            17  9   4   14  2
            25  0   3   12  1
            25  3   8   14  2
            25  4   8   13  2
            25  4   9   14  2
            25  5   8   12  1
            25  8   3   14  2
            25  9   3   13  2
            27  0   3   12  1
            27  3   8   14  1
            27  4   8   13  1
            27  5   8   12  1
            27  8   3   14  1
            27  9   3   13  1


'''


parch_format   = {'sfn':'SFN', 'subframe': 'Subframe'}
dll_format     = {'sfn':'SFN', 'subframe': 'Subframe', 'service_type':'Service Type'}
rxformat       = {'sfn':'SFN', 'subframe': 'Subframe', 'id':'ID', 'len':'Length(Bytes)', 'len2':'Length(Bytes)*2'}
txformat       = {'sfn':'SFN', 'subframe': 'Subframe', 'id':'ID', 'len':'Length(Bytes)', 'len2':'Length(Bytes)*2'}
throughput_format = {'dl':'DL-SCH Throughput(Kbps)', 'ul': 'UL-SCH Throughput(Kbps)',
                    'blerp': 'DL-SCH BLER (PCC)', 'blers':'DL-SCH BLER (SCC)',
                    'ubler': 'UL-SCH BLER', 'bbler':'BCH BLER'}
throughput_format_3cc = {'rat':'RAT', 'dl':'DL-SCH throughput(kbps)', 'bler': 'DL-SCH BLER'}

ho_tx_format = {'time':'Time', 'sfn':'SFN', 'subframe': 'Subframe', 'id':'ID'}
ho_rx_format = {'state':'#State', 'time':'Time', 'sfn':'SFN', 'subframe': 'Subframe', 'id':'ID', 'id2':'ID*2'}

# read_data_file procedure read data from csv file accrding to specific format
# Attention, the format define the map between field name and the title in csv file
# sometimes, the title may be duplicated and we may specific which one is we wanted

def get_index(alist, value, exp_seq):
    count = 0
    for i in range(len(alist)):
        if alist[i] == value:
            count += 1
        if count == exp_seq:
            return i

def _getfilename(keyword):
    filelist = os.listdir(gv.tm500.tm500_log_dir)
    files = [os.sep.join([gv.tm500.tm500_log_dir, x]) for x in filelist if keyword in x and ('.csv' in x or '.log' in x)]
    if files:
        return files[0]
    else:
        raise Exception, 'Could not find the file whose name contain [%s]!' %(keyword)

def read_data_file(filekeyword,  cared_fields, keystr=''):
    import copy
    filename = _getfilename(filekeyword)
    fielddef = copy.deepcopy(cared_fields)
    lines = open(filename, 'r').readlines()
    ret = []
    start = False
    titles = []
    for line in lines:
        if not line.strip():
            continue
        if keystr and keystr not in line:
            continue
        if '#State' in line:
            start = True
            titles = [x.strip() for x in line.split(',')]
            for field in fielddef:
                if '*' in fielddef[field]:
                    max_count = int(fielddef[field].split('*')[1])
                    title = fielddef[field].split('*')[0]
                else:
                    max_count = 1
                    title = fielddef[field]
                count = 0
                for index in range(len(titles)):
                    if title.strip().upper() == titles[index].strip().upper():
                        count += 1
                    if count == max_count:
                        fielddef[field] = index
                        break
            print fielddef
            continue
        if start:
            if line.strip():
                adict = {}
                if len(line.split(',')) >= len(fielddef):
                    if '---' in line:
                        print 'xxxx', line
                    for field in fielddef:
                        if int(fielddef[field])+1 <= len(line.split(',')):
                            adict[field] = line.split(',')[int(fielddef[field])].strip()
                    ret.append(adict)
    return ret


def calc_sfn(data=None, base=None):
    if base:
        if int(data['sfn']) >= base:
            return int(data['sfn'])*10 + int(data['subframe'])
        else:
            return int(data['sfn'])*10 + 10240 + int(data['subframe'])
    else:
        return int(data['sfn'])*10 + int(data['subframe'])

def parse_pcap(filename, str1, str2):
    def _get_timestamp(expstr):
        l1 = [x for x in lines if expstr in x]
        if l1:
            return l1[0].split()[1]
        else:
            kw('report_error', 'Cound not find keyword [%s] in PCAP file, please check it!' %(expstr))
    gv.logger.info('Pcap filename:  '+ filename)
    lines = open(filename).readlines()
    st, et = 0, 0
    st = _get_timestamp(str1)
    et = _get_timestamp(str2)
    return float(et) - float(st)

def parse_pcap_trigger(filename):
    gv.logger.info('Pcap filename:  '+ filename)
    lines = open(filename).readlines()
    lines = [x.replace('\n', '') for x in lines]
    lines = [x for x in lines if x.strip()]

    st, et = 0, 0
    for i in range(len(lines)):
        if 'Service'.upper() in lines[i].upper():
            gv.logger.info('Found service in [%s]' %(lines[i].splitlines()[0]))
            gv.logger.info('Next line is [%s]' %(lines[i+1].splitlines()[0]))
            st = lines[i].split()[1]
            et = lines[i+1].split()[1]
            break
    return float(et) - float(st)

def _get_latency_wait_time(def_str, uldl, ssf, tx_pos, rx_pos):
    ssf = '7' if str(ssf) in ['3','4','7','9'] else ssf
    key = '%s%s,%s,%s' %(uldl, ssf, str(tx_pos).upper(), rx_pos)
    lines = ['%s,%s,%s,%s' %(x.split()[0], x.split()[1], x.split()[2], x.split()[-1]) for x in def_str.splitlines() if x.strip()]
    lines = [x for x in lines if key in x]
    if lines:
        return float(lines[0].split(',')[-1])
    else:
        return 0

def get_c_plan_trigger_time_pet1():
    filename = _getfilename('_UE0')
    lines = ''.join(open(filename).readlines())
    if not 'serviceRequest : {' in lines:
        kw('report_error', 'Could not find service request message in protocal files!')

    parch_data  = read_data_file('PRACH', parch_format)
    dll_data    = read_data_file('DLL1L2CONTROL', dll_format, 'RACH')
    txdata      = read_data_file('MACTX_', txformat)
    txdata      = [x for x in txdata if 'id' in x.keys()]
    txdata = [x for x in txdata if x['len'].strip() <> '-' ]
    txdata = [x for x in txdata if x['sfn'].strip() <> 'NA']

    rxdata      = read_data_file('MACRX_', rxformat)
    rxdata      = [x for x in rxdata if 'id' in x.keys()]
    rxdata = [x for x in rxdata if x['len'].strip() <> '-']
    rxdata = [x for x in rxdata if x['sfn'].strip() <> 'NA']
    # rxdata = [x for x in rxdata if int(x['len']) >2 ]

    tx_base_sfn = int(txdata[0]['sfn'])
    rx_base_sfn = int(rxdata[0]['sfn'])

    gv.logger.info('Base SFN for Tx [%d], for Rx: [%d]' %(tx_base_sfn, rx_base_sfn))
    # Calculate T1: dll_data is the first data row, parch_data is the last data row
    #T1 for eNodeB, between: Receive "Paging" from MME and send "PCH" paging message to UE
    parch_data = [x for x in parch_data if x['sfn'] <> 'NA']
    t1 = calc_sfn(dll_data[-1]) - calc_sfn(parch_data[-1]) -1
    print 'T1 = '+str(t1)

    #Calculate T2
    #T2 for eNodeB, between: Receive "RRC Connection Request" from UE and send "RRC Connection Setup" to UE
    tx0 = [x for x in txdata if 'id' in x.keys() and x['id'] == '0'][1]
    rx0 = [x for x in rxdata if 'id' in x.keys() and x['id'] == '0'][1]
    print '\nCalculating T2: Dll - Parch:'
    print rx0, tx0
    t2 = calc_sfn(rx0, rx_base_sfn) - calc_sfn(tx0, tx_base_sfn) -1
    print 'T2 = '+str(t2)

    #Calculate T3
    #T3 for eNodeb, between: Receive "RRC conn Setup Control" from UE and send "RRC Conn Reconfig" to UE
    count = 0
    for i in range(len(txdata)):
        if txdata[i]['id'] == '0':
            count +=1
        if count == 2:
            for j in range(1, len(txdata)-i):
                if i+j > len(txdata)-1:
                    break
                if txdata[i+j]['len'] <> '2':
                    tx1 = txdata[i + j]
                    break
                elif txdata[i+j]['len2'].strip() not in ['-', '2']:
                    tx1 = txdata[i + j]
                    break
                else:
                    pass
            break

    count = 0
    for i in range(len(rxdata)):
        if rxdata[i]['id'] == '0':
            count +=1
        if count == 2:
            for j in range(1, len(rxdata)-i):
                if i+j > len(rxdata)-1:
                    break
                if rxdata[i+j]['len'] <> '2':
                    rx1 = rxdata[i + j]
                    break
                elif rxdata[i+j]['len2'].strip() not in ['-', '2']:
                    rx1 = rxdata[i + j]
                    break
                else:
                    pass
            break

    pcapfilename = case_file('local.txt')
    diff = parse_pcap_trigger(pcapfilename)
    print '\nCalculate T3: rx tx diff'
    print rx1, tx1
    print 'Diff in T3 = '+str(diff*1000)
    t3 = calc_sfn(rx1, rx_base_sfn) - calc_sfn(tx1, tx_base_sfn) -diff*1000 -1

    txpos = int(tx1['subframe']) + int(str(diff*100).split('.')[1][0])+1
    txpos = txpos - 10 if txpos >=10 else txpos
    print 'Tx subframe after calculate with diff: ' + str(txpos)
    w3 = _get_latency_wait_time(trigger_t3_define, gv.master_bts.uldl, gv.master_bts.ssf, txpos, int(rx1['subframe']))
    print 'Wait time for T3: '+str(w3)
    print 'T3 = '+str(t3)

    print t1+t2+t3-w3, t1, t2, t3
    gv.kpi.kpi_trigger_ra = round(t1, 5)
    return round(t1+t2+t3-w3, 4)

def get_c_plan_latency_time_pet1():
    parch_data  = read_data_file('PRACH', parch_format)
    dll_data    = read_data_file('DLL1L2CONTROL', dll_format, 'RACH')
    txdata      = read_data_file('MACTX_', txformat)
    txdata      = [x for x in txdata if 'id' in x.keys()]
    rxdata      = read_data_file('MACRX_', rxformat)
    rxdata      = [x for x in rxdata if 'id' in x.keys()]


    tx_base_sfn = int(txdata[0]['sfn'])
    rx_base_sfn = int(rxdata[0]['sfn'])
    print '\nBase SFN for Tx [%d], for Rx: [%d]' %(tx_base_sfn, rx_base_sfn)

    pcapfilename = case_file('local.txt')

    # Calculate T1
    parch_data = [x for x in parch_data if x['sfn'] <> 'NA']
    print '\nT1: dll data and para_data: '
    print dll_data[0], parch_data[-1]
    t1 = calc_sfn(dll_data[0]) - calc_sfn(parch_data[-1]) -1
    print 'T1 = '+ str(t1)

    #Calculate T2
    #T2 for eNodeB between: Receive "RRC Connection Request" from UE and send "RRC Connection Setup" to UE
    tx0 = [x for x in txdata if x['id'] == '0'][0]
    rx0 = [x for x in rxdata if x['id'] == '0'][0]
    print '\nT2: Rx data and Tx data: '
    print rx0, tx0
    t2 = calc_sfn(rx0, rx_base_sfn) - calc_sfn(tx0, tx_base_sfn) -1
    print 'T2 = '+ str(t2)

    #Calculate T3
    #T3 for eNodeB between: Receive "RRC Conn setup Complete" from UE and send "RRC Security Mode Conn"
    # for T3, need to delete the time used by core network, get the time from pcap file
    tx1 = [x for x in txdata if x['id'] == '1'][0]
    # rx1 = [x for x in rxdata if x['id'] == '1' and x['len'] in ['10', '20']][0]
    rx1 = [x for x in rxdata if x['id'] == '1' and (x['len'] in ['10', '20'] or x['len2'] in ['10', '20'])][0]
    diff = parse_pcap(pcapfilename, 'Attach request', 'Attach accept')
    print '\nT3: Rx data and Tx data: '
    print rx1, tx1
    print 'Diff in T3: '+ str(diff*1000)
    t3 = calc_sfn(rx1, rx_base_sfn) - calc_sfn(tx1, tx_base_sfn) -diff*1000 -1
    txpos = int(tx1['subframe']) + int(str(diff*100).split('.')[1][0])+1
    print txpos
    txpos = txpos - 10 if txpos >=10 else txpos
    print 'Tx subframe after calculate with diff: ' + str(txpos)
    w3 = _get_latency_wait_time(latency_t3_define, gv.master_bts.uldl, gv.master_bts.ssf, txpos, int(rx1['subframe']))
    print 'Wait time for T3: ' + str(w3)
    print 'T3 = '+ str(t3)

    #Calculate T4
    #T4 for eNodeB between: Receive "RRC Security Command" from UE and send "RRC Conn Reconfig" to UE
    len_max = max([int(x['len']) for x in rxdata if x['id'] == '1'])
    rx4 = [x for x in rxdata if  x['len'] == str(len_max)][0]
    # l1 =  [int(x['sfn'])*10+int(x['subframe']) for x in txdata if 'sfn' in x.keys() and x['id'].isdigit()]
    # print l1
    # tx4 = [{'sfn': round(int(x)/10), 'subframe': int(str(x)[-1])} for x in l1 if x <= int(rx4['sfn'])*10+int(rx4['subframe'])][-1]
    tx4 = [x for x in txdata if 'sfn' in x.keys() and x['id'].isdigit() and calc_sfn(rx4, rx_base_sfn)-calc_sfn(x, tx_base_sfn) >0][-1]

    print '\nT4: Rx data and Tx data: '
    print rx4, tx4
    t4 = calc_sfn(rx4, rx_base_sfn) - calc_sfn(tx4, tx_base_sfn) -1
    print 'T4 = '+ str(t4)
    w4 = _get_latency_wait_time(latency_t4_define, gv.master_bts.uldl, gv.master_bts.ssf, int(tx4['subframe']), int(rx4['subframe']))
    print 'Wait time for T4: ' + str(w4)

    gv.kpi.kpi_latency_ra = round(t1, 5)
    print '\nFinally Result: '
    print t1+t2+t3+t4-w3-w4, t1, t2, t3-w3, t4-w4
    return round(t1+t2+t3+t4-w3-w4, 5)

def get_throughput_kpi(service_type='dl', tm500_log_dir=''):
    def _analysis_bler(datas, fieldname, prompt):
        blers = [x for x in datas if x[fieldname].strip() <> '-' ]
        if blers:
            blercount = len(blers)
            bler = [x[fieldname] for x in blers if float(x[fieldname]) <> 0]
            kw('log', prompt)
            kw('log', '%s ratio: %s%%' %(prompt, len(bler)*100/blercount))
            if bler:
                kw('log', 'BLER list: %s' %(str(bler)))
            kw('log', 'Average Bler: %s%%' %(str(100*float(datas[-1][fieldname]))))

    if gv.case.curr_case.ca_type.upper().strip() == '3CC' and gv.case.curr_case.case_type.upper().strip() == 'FTP_DOWNLOAD':
        return get_download_throughput_for_3cc(service_type, tm500_log_dir)
    if gv.case.curr_case.case_type.upper().strip() == 'CPK_MUE_DL_COMBIN':
        return get_download_throughput_for_3cc(service_type, tm500_log_dir)

    if gv.case.curr_case.case_type.upper().strip() == 'THROUGHPUT_MUE_DL':
        return get_download_throughput_for_mue('DOWN', tm500_log_dir)
    if gv.case.curr_case.case_type.upper().strip() == 'THROUGHPUT_MUE_UL':
        return get_download_throughput_for_mue('UP', tm500_log_dir)
    if gv.case.curr_case.case_type in ['FTP_UPLOAD'] and gv.case.curr_case.tm500_version in ['L']:
        return get_download_throughput_for_mue('UP', tm500_log_dir)

    kw('run_keyword_and_ignore_error', 'show_signal_values')
    kpi = 0
    data_filename = '_UEOVERVIEW_NA_'
    data_format = {'dl':'DL-SCH Throughput(Kbps)', 'ul': 'UL-SCH Throughput(Kbps)',
                    'blerp': 'DL-SCH BLER (PCC)', 'blers':'DL-SCH BLER (SCC)',
                    'ubler': 'UL-SCH BLER', 'bbler':'BCH BLER'}
    gv.tm500.tm500_log_dir = tm500_log_dir if tm500_log_dir.strip() else gv.tm500.tm500_log_dir
    datas = read_data_file(data_filename, data_format)
    last_row = datas[-1]
    kpi = float(last_row[service_type])/1000
    try:
        _analysis_bler(datas, 'blerp', 'DL-SCH BLER PCC')
        _analysis_bler(datas, 'blers', 'DL-SCH BLER SCC')
        _analysis_bler(datas, 'ubler', 'UL-SCH BLER ')
        _analysis_bler(datas, 'bbler', 'BCH BLER ')
    finally:
        pass
    return kpi

def _analysis_bler_data(datas):
    try:
        bler = [x for x in datas if x['bler'].strip() not in  ['-', 'NA']]
        if bler:
            blercount = len(bler)
            bler = [x['bler'] for x in bler if float(x['bler']) <> 0]
            kw('log', 'BLER ratio: %s%%' %(len(bler)*100/blercount))
            if bler:
                kw('log', 'BLER list: %s' %(str(bler)))
            kw('log', 'Average DL Bler: %s%%' %(str(100*float(datas[-1]['bler']))))
    finally:
        pass

def get_download_throughput_for_3cc(service_type='STREAM', tm500_log_dir=''):
    kw('run_keyword_and_ignore_error', 'show_signal_values')
    kpi = 0
    gv.tm500.tm500_log_dir = tm500_log_dir if tm500_log_dir.strip() else gv.tm500.tm500_log_dir
    datas = read_data_file('_L1DLSTATS_NA_', {'rat':'RAT', 'dl':'DL-SCH throughput(kbps)', 'bler': 'DL-SCH BLER'})
    last_row = datas[-1]
    dl_datas = [float(x['dl']) for x in datas if x['rat'].strip() == '-']
    if len(dl_datas) == 0:
        kw('report_error', 'Could not find valid download data record in L1DLSTATS_NA file, please check it.')
    kpi = sum(dl_datas)/((len(dl_datas))*1000)
    _analysis_bler_data(datas)
    return kpi

def get_download_throughput_for_mue(direction = 'DOWN', tm500_log_dir=''):
    gv.tm500.tm500_log_dir = tm500_log_dir if tm500_log_dir.strip() else gv.tm500.tm500_log_dir
    kpi = 0
    data_format = {'tput':'DL-SCH throughput(kbps)'} if direction == 'DOWN' else {'tput':'UL-SCH Throughput(kbps)'}
    # data_format = {'tput':'Aggregate DL-SCH throughput(kbps)'} if direction == 'DOWN' else {'tput':'UL-SCH Throughput(kbps)'}
    bler_format = {'bler':'DL-SCH BLER'} if direction == 'DOWN' else {'bler':'UL-SCH BLER'}
    bler_filename = '_L1DLSTATS_' if direction == 'DOWN' else '_L1ULSTATS_'
    kpi = float(read_data_file('_SYSOVERVIEW_', data_format)[-1]['tput'])/1000
    try:
        datas = read_data_file(bler_filename, bler_format)
        _analysis_bler_data(datas)
    except:
        pass
    return kpi

def get_ue_num_for_mue(tm500_log_dir=''):
    gv.tm500.tm500_log_dir = tm500_log_dir if tm500_log_dir.strip() else gv.tm500.tm500_log_dir
    kpi = 0
    data_format = {'uenum':'Configured UEs'}
    kpi = float(read_data_file('_SYSOVERVIEW_', data_format)[-1]['uenum'])
    return kpi

def get_ftp_download():
    return get_throughput_kpi('dl', case_file('Tmftpdl'))

def get_ftp_upload():
    return get_throughput_kpi('ul', case_file('Tmftpul'))

def get_c_plan_latency_time_ra():
    get_c_plan_latency_time()
    return gv.kpi.kpi_latency_ra

def get_c_plan_trigger_time_ra():
    get_c_plan_trigger_time()
    return gv.kpi.kpi_trigger_ra

def show_signal_values():
    try:
        filename = _getfilename('_L1DLRSPOWER_0000')
        indexs = {}
        lines = open(filename).readlines()
        for line in lines:
            if '#State' in line:
                titles = line.split(',')
                for i in range(len(titles)):
                    if 'Total BW Reference Signal Power' in titles[i]:
                        indexs[titles[i]] = i
                for i in range(len(titles)):
                    if 'Reference signal SIR' in titles[i]:
                        indexs[titles[i]] = i
                break
        lastline = lines[-1]
        print lastline
        for signal in indexs.keys():
            kw('log', 'Signal value: [%s] is: [%s]' %(signal, lastline.split(',')[indexs[signal]]))
    finally:
        pass

def get_volte_call_setup_ratio():
    return 0

def get_volte_call_drop_ratio():
    kw('log', gv.kpi.kpi_volte_call_drop_ratio)
    if has_attr(gv.kpi, 'kpi_volte_call_drop_ratio') and gv.kpi.kpi_volte_call_drop_ratio <> 'INVALID':
        gv.kpi.kpi_volte_call_drop_ratio = 0
        kw('log', gv.kpi.kpi_volte_call_drop_ratio)
        return gv.kpi.kpi_volte_call_drop_ratio
    else:
        kw('report_error', 'Call setup case failed, so call drop case should be failed either.')

def get_volte_perm_mos():
    gv.kpi.kpi_volte_perm_mos = sum(gv.kpi.kpi_volte_perm_mos_list)/len(gv.kpi.kpi_volte_perm_mos_list)
    kw('log', gv.kpi.kpi_volte_perm_mos)
    return gv.kpi.kpi_volte_perm_mos

def get_volte_loss_ratio():
    if has_attr(gv.kpi, 'kpi_volte_perm_loss_ratio') and gv.kpi.kpi_volte_perm_loss_ratio <> 'INVALID':
        gv.kpi.kpi_volte_perm_loss_ratio = sum(gv.kpi.kpi_volte_perm_loss_ratio_list)/len(gv.kpi.kpi_volte_perm_loss_ratio_list)
        kw('log', gv.kpi.kpi_volte_perm_loss_ratio)
        return gv.kpi.kpi_volte_perm_loss_ratio
    else:
        kw('report_error', 'VOLTE Related case failed, so packet loss ratio case should be failed either.')

def check_each_kpi_and_verify_it_is_acceptable():
    reportstr = '*****KPI Result***** '
    gv.logger.info(gv.case.curr_case.kpi)
    gv.logger.info(gv.kpi)
    for kpistr in gv.case.curr_case.kpi.replace(',',';').split(';'):
        kpiname = kpistr.split(':')[0].strip()
        target = float(kpistr.split(':')[1].strip())
        kpidef = [x for x in kpi_defination if x.name.upper() == kpiname.upper()]
        gv.logger.info('Process KPI: '+kpiname)
        gv.logger.info(kpidef)
        if not kpidef:
            kw('report_error', 'Unknown KPI: [%s]' %(kpiname))
        if 'get_' in kpidef[0].funname:
            test_result = round(kw(kpidef[0].funname), 5)
        else:
            gv.logger.info(kpidef[0].funname)

            if hasattr(gv, kpidef[0].funname):
                test_result = round(getattr(gv, kpidef[0].funname), 5)
            elif hasattr(gv.kpi, kpidef[0].funname):
                gv.logger.info(str(getattr(gv.kpi, kpidef[0].funname)))
                test_result = round(float(getattr(gv.kpi, kpidef[0].funname)), 5)

        if test_result < 0:
            kwg('report_error', 'The KPI [%s] is [%s] and is unreasonable!' %(kpiname, test_result))

        if kpidef[0].big_is_good:
            if test_result < target:
                kwg('report_error', 'The KPI [%s] is lower than expected value, [%s] vs [%s]!' %(kpiname, test_result, target))
            if gv.case.curr_case.case_type in ['FTP_DOWNLOAD', 'FTP_UPLOAD', 'THROUGHPUT_MUE_DL_UL', 'THROUGHPUT_MUE_DL', 'THROUGHPUT_MUE_UL']:
                mtarget = target*(1 + 0.05)
                if test_result > mtarget:
                    kwg('report_error', 'The KPI [%s] is too much high than expected value, [%s] vs [%s]!' %(kpiname, test_result, mtarget))
        else:
            if test_result > target:
                kwg('report_error', 'The KPI [%s] is larger than expected value, [%s] vs [%s]!' %(kpiname, test_result, target))
        if kpidef[0].report:
            reportstr += '%s:%2.2f%s/%2.2f%s; ' %(kpidef[0].prefix, float(test_result), kpidef[0].unit, float(target), kpidef[0].unit)
    kw('log', reportstr)

def get_handover_kpis():
    if gv.case.curr_case.case_type.upper() == 'HO_Intra_eNB'.upper():
        return get_intra_enb_handover_kpis()
    else:
        return get_inter_enb_handover_kpis()


def get_inter_enb_handover_kpis():
    def _get_btslog_timestamp(expstr):
        etstr = [float(x) for x in expstr.split()[6].split('T')[-1].replace('Z','').replace('>','').split(':')]
        print expstr.split()[7].replace('>','')
        return (etstr[0]*3600 + etstr[1]*60 + etstr[2])*1000

    def _get_tm500_log_time(timestr):
        estr = [float(x) for x in timestr.split(':')]
        return (estr[0]*3600+estr[1]*60+estr[2]+estr[3]/1000)*1000

    # Result defination:
    # total enb delay = T1+T2+T3
    # DL delay = T1 + T3 + T4 -3.5
    # UL delay = Dl delay + 7

    #for T1:
    # T1 from btslog:
    # T1 = time of "sendRrcConnectionReconf()" - time of last reacord "X2AP_HANDOVER_REQUEST_ACKNOWLEDGE"

    filename = case_file('btslog2.log')
    # filename = '/tmp/btslog_1412.log'
    btslog = open(filename, 'r').readlines()
    btslog = [x.replace('\n', '') for x in btslog]
    alist = [x for x in btslog if 'sendRrcConnectionReconf' in x]
    if alist:
        # print alist[-1]
        et = _get_btslog_timestamp(alist[-1])
    else:
        kw('report_error', 'Counld not find [sendRrcConnectionReconf] in btslog')

    alist = [x for x in btslog if 'X2AP_HANDOVER_REQUEST_ACKNOWLEDGE, status= BASE_SUCCESS' in x]
    if alist:
        # print alist[-1]
        st = _get_btslog_timestamp(alist[-1])
    else:
        kw('report_error', 'Counld not find [X2AP_HANDOVER_REQUEST_ACKNOWLEDGE, status= BASE_SUCCESS] in btslog')

    t1 = et - st
    print 'T1 = ' + str(t1)

    txdata      = read_data_file('_MACTX_NA_', ho_tx_format)
    txdata      = [x for x in txdata if 'id' in x.keys()]
    rxdata      = read_data_file('_MACRX_NA_', ho_rx_format)
    rxdata      = [x for x in rxdata if 'id' in x.keys()]

    tx_base_sfn = int(txdata[0]['sfn'])
    rx_base_sfn = int(rxdata[0]['sfn'])
    print '\nBase SFN for Tx [%d], for Rx: [%d]' %(tx_base_sfn, rx_base_sfn)

    # T4 is from TM500 log = T4x - R4x - Delta

    # Search 2 records in Rx and TX, they have same SFN and Subframe
    # Deta = (Tx_time-Rx_Time)

    # T4x is record  id = 1, SFN = '-', get its time as Time4x,
    # Time4r is just large than Time 4x and SFN = '-'
    # R4x : time is Time4r, from this record, up to find the record that id == '1' and SFN <> '-'

    # So we got T4

    # Calculate the delta first
    print 'Calculate the delta first:'
    delta_time = 0
    for tx in txdata:
        rx_with_same_sfn = [rx for rx in rxdata if rx['sfn'] == tx['sfn'] and rx['subframe'] == tx['subframe']]
        if rx_with_same_sfn:
            delta =  _get_tm500_log_time(tx['time']) - _get_tm500_log_time(rx_with_same_sfn[0]['time'])
            print 'Delta record Tx  and RTx:'
            print tx, rx_with_same_sfn[0]
            print 'delta: %s' %(delta)
            break

    txdata = [x for x in txdata if 'id' in x.keys() and x['id'] == '1']
    rxdata = [x for x in rxdata if not '-' in x['time']]

    #Calculate T4:
    t4x = [tx for tx in txdata if tx['sfn'].strip() == '-' and tx['id'] == '1']
    if t4x:
        t4x = t4x[0]
    else:
        kw('report_error', 'Could not find the blank subframe in TxData')

    time4x = t4x['time']
    time4r = [rx['time'] for rx in rxdata if rx['time'] >= time4x and rx['sfn'] == '-'][0]
    print 'time4x, time4r:'
    print time4x, time4r
    r4x = [rx for rx in rxdata if rx['time'] <= time4r and 'id' in x.keys() and rx['id'] == '1' and rx['sfn'] <> '-']
    if r4x:
        r4x = r4x[-1]
    else:
        kw('report_error', 'Could not find the correct record in RxData')

    t4 = _get_tm500_log_time(t4x['time']) - _get_tm500_log_time(r4x['time']) - delta

    print 'T4 records r4x and t4x:'
    print r4x, t4x
    print 'T4 = ' + str(t4)

    # T3 = R3x - T4x
    # R3x is record for id1 = 3, sfn = '-' and time >= Time4r
    # So we got T3

    #Calculate T3:
    r3x = [rx for rx in rxdata if rx['id'] == '3' and rx['sfn'].strip() == '-' and rx['time'] >= time4r]
    if r3x:
        r3x = r3x[0]
    else:
        kw('report_error', 'Could not find the blank subframe in RxData with id1 = 3')

    t3 = _get_tm500_log_time(r3x['time']) - _get_tm500_log_time(t4x['time'])
    print 'T3 records Rx and Tx:'
    print r3x, t4x
    print 'T3 = ' + str(t3)

    gv.kpi.kpi_total_enb_delay = t1 + 5.5 + t3
    gv.kpi.kpi_uplan_dl_interruption = t1 + t3 + t4 - 3.5
    gv.kpi.kpi_uplan_ul_interruption = gv.kpi.kpi_uplan_dl_interruption + 7
    print 'total enb delay : ' + str(gv.kpi.kpi_total_enb_delay)
    print 'U Plan DL interruption : ' + str(gv.kpi.kpi_uplan_dl_interruption)
    print 'U Plan UL interruption : ' + str(gv.kpi.kpi_uplan_ul_interruption)

def get_intra_enb_handover_kpis():
    def _get_btslog_timestamp(expstr):
        etstr = [float(x) for x in expstr.split()[6].split('T')[-1].replace('Z','').replace('>','').split(':')]
        return (etstr[0]*3600 + etstr[1]*60 + etstr[2])*1000

    def _get_tm500_log_time(timestr):
        estr = [float(x) for x in timestr.split(':')]
        return (estr[0]*3600+estr[1]*60+estr[2]+estr[3]/1000)*1000

    # Result defination:
    # total enb delay = T1+T2+T3
    # DL delay = T1 + T3 + T4 -3.5
    # UL delay = Dl delay + 7

    #for T1:
    # T1 from btslog:
    # T1 = time of "sendRrcConnectionReconf()" - time of last reacord "X2AP_HANDOVER_REQUEST_ACKNOWLEDGE"

    filename = case_file('btslog2.log')
    # filename = '/tmp/ta/btslog2.log'
    btslog = open(filename, 'r').readlines()
    btslog = [x.replace('\n', '') for x in btslog]

    alist = [x for x in btslog if 'handleMsg: started, l_msgId=0x249d' in x]
    if alist:
        st = _get_btslog_timestamp(alist[-1])
    else:
        kw('report_error', 'Counld not find [handleMsg: started, l_msgId=0x249d] in btslog')

    alist = [x for x in btslog if 'TUP_SrbSendReq' in x]
    if alist:
        et = _get_btslog_timestamp(alist[-1])
    else:
        kw('report_error', 'Counld not find [TUP_SrbSendReq] in btslog')

    t1 = et - st
    print 'T1 = ' + str(t1)

    txdata      = read_data_file('_MACTX_NA_', ho_tx_format)
    txdata      = [x for x in txdata if 'id' in x.keys()]
    rxdata      = read_data_file('_MACRX_NA_', ho_rx_format)
    rxdata      = [x for x in rxdata if 'id' in x.keys()]

    tx_base_sfn = int(txdata[0]['sfn'])
    rx_base_sfn = int(rxdata[0]['sfn'])
    print '\nBase SFN for Tx [%d], for Rx: [%d]' %(tx_base_sfn, rx_base_sfn)

    # T4 is from TM500 log = T4x - R4x - Delta

    # Search 2 records in Rx and TX, they have same SFN and Subframe
    # Deta = (Tx_time-Rx_Time)

    # T4x is record  id = 1, SFN = '-', get its time as Time4x,
    # Time4r is just large than Time 4x and SFN = '-'
    # R4x : time is Time4r, from this record, up to find the record that id == '1' and SFN <> '-'

    # So we got T4

    # Calculate the delta first
    print 'Calculate the delta first:'
    delta_time = 0
    for tx in txdata:
        rx_with_same_sfn = [rx for rx in rxdata if rx['sfn'] == tx['sfn'] and rx['subframe'] == tx['subframe']]
        if rx_with_same_sfn:
            delta =  _get_tm500_log_time(tx['time']) - _get_tm500_log_time(rx_with_same_sfn[0]['time'])
            print 'Delta record Tx  and RTx:'
            print tx, rx_with_same_sfn[0]
            print 'delta: %s' %(delta)
            break

    txdata = [x for x in txdata if 'id' in x.keys() and x['id'] == '1']
    rxdata = [x for x in rxdata if not '-' in x['time']]

    #Calculate T4:
    t4x = [tx for tx in txdata if tx['sfn'].strip() == '-' and tx['id'] == '1']
    if t4x:
        t4x = t4x[0]
    else:
        kw('report_error', 'Could not find the blank subframe in TxData')

    time4x = t4x['time']
    time4r = [rx['time'] for rx in rxdata if rx['time'] >= time4x and rx['sfn'] == '-'][0]
    print 'time4x, time4r:'
    print time4x, time4r
    r4x = [rx for rx in rxdata if rx['time'] <= time4r ]
    print 'KKKK'
    print len(r4x)
    for item in r4x:
        print item
    # print r4x
    print r4x[-1]
    r4x = [rx for rx in rxdata if rx['time'] <= time4r and 'id' in x.keys() and rx['id'] == '1' and rx['sfn'] <> '-']
    if r4x:
        print len(r4x)
        print r4x
        r4x = r4x[-1]
        print 'AAAA'
        print r4x
    else:
        kw('report_error', 'Could not find the correct record in RxData')

    t4 = _get_tm500_log_time(t4x['time']) - _get_tm500_log_time(r4x['time']) - delta

    print 'T4 records r4x and t4x:'
    print r4x, t4x
    print 'T4 = ' + str(t4)

    # T3 = R3x - T4x
    # R3x is record for id1 = 3, sfn = '-' and time >= Time4r
    # So we got T3

    #Calculate T3:
    r3x = [rx for rx in rxdata if rx['id'] == '3' and rx['sfn'].strip() == '-' and rx['time'] >= time4r]
    if r3x:
        r3x = r3x[0]
    else:
        kw('report_error', 'Could not find the blank subframe in RxData with id1 = 3')

    t3 = _get_tm500_log_time(r3x['time']) - _get_tm500_log_time(t4x['time'])
    print 'T3 records Rx and Tx:'
    print r3x, t4x
    print 'T3 = ' + str(t3)

    gv.kpi.kpi_total_enb_delay = t1 + 5.5 + t3
    gv.kpi.kpi_uplan_dl_interruption = t1 + t3 + t4 - 3.5
    gv.kpi.kpi_uplan_ul_interruption = gv.kpi.kpi_uplan_dl_interruption + 7
    print 'total enb delay : ' + str(gv.kpi.kpi_total_enb_delay)
    print 'U Plan DL interruption : ' + str(gv.kpi.kpi_uplan_dl_interruption)
    print 'U Plan UL interruption : ' + str(gv.kpi.kpi_uplan_ul_interruption)

def tm500_log_is_valid_for_handover():
    txdata = read_data_file('_MACTX_NA_', ho_tx_format)
    txdata = [x for x in txdata if 'id' in x.keys()]
    txdata = [x for x in txdata if x['id'] == '1']
    txdata = [x for x in txdata if x['sfn'].strip() == '-']

    filename = _getfilename('_MACRX_NA_')
    lines = open(filename).read()
    return len(txdata) > 0 and '-----' not in lines

def get_volte_tti_kpi():
    import os
    workpath = gv.case.log_directory
    filelist = os.listdir(workpath)
    ulfiles = [filename for filename in filelist if '_ul.dat' in filename]
    if len(ulfiles) == 0:
        for filename in filelist:
            print filename
        kw('report_error', 'Cound not find the tti trace file, please check it.')

    ulfile = os.sep.join([workpath, ulfiles[0]])
    try:
        run_local_command('%s %s %s/uldata.csv' %(gv.master_bts.tti.ttiparser, ulfile, workpath))
        bts = gv.master_bts
        uldata = {}
        for line in open('%s/uldata.csv' %(workpath)).readlines()[2:]:
            if line.split(',')[2].strip() == '-' or line.split(',')[17].strip() == '-' or line.split(',')[-4].strip() == '-':
                continue
            adata = IpaMmlItem()
            if line.split(',')[1] <> '-':
                adata.esfn = int(line.split(',')[2].strip())
                adata.user = int(line.split(',')[14].strip())
                uldata[str(len(uldata))] = adata

        ulnfn_value = 12 if bts.band in ['15', '20'] else 10
        ulnfn_value = 20 if bts.max_tti_user else ulnfn_value
        if gv.case.curr_case.ul_sps:
            ulnfn_value = ulnfn_value + 4
        print '\nulnfn_value:     ', ulnfn_value
        ul_total_nfn = len([x for x in uldata.values()])
        ul_good_nfn  = len([x for x in uldata.values() if x.user >= ulnfn_value])
        print 'ul_total_nfn:    ', ul_total_nfn
        print 'ul_good_nfn:     ', ul_good_nfn
        gv.kpi.kpi_tti_ul = 0
        if ul_total_nfn == 0:
            kwg('report_error', 'ul_total_nfn is 0, counld not calcaulte the kpi_tti_ul')
        else:
            gv.kpi.kpi_tti_ul = ul_good_nfn*100/ul_total_nfn
            print 'kpi_tti_ul:      ', gv.kpi.kpi_tti_ul, r'%'
    finally:
        import os
        if os.path.exists('%s/dldata.csv' %(workpath)):
            os.remove('%s/dldata.csv' %(workpath))
        if os.path.exists('%s/uldata.csv' %(workpath)):
            os.remove('%s/uldata.csv' %(workpath))

def get_kpi_tti_ul():
    get_volte_tti_kpi()
    return gv.kpi.kpi_tti_ul

def get_kpi_cpuload():
    from pet_bts import download_bts_cpuload_file
    download_bts_cpuload_file(gv.master_bts.bts_id)
    from pet_cpu import c_cpuload_manager
    manager = c_cpuload_manager(case_file('loadfile'))
    manager.parse_data_files()
    cpuload = manager.calculate_kpi()
    try:
        std = manager.calculate_standard_deviation()
        gv.logger.info('The stand deviation is: [%0.2f]' %(std))
    except:
        pass
    return cpuload

def get_kpi_fspload():
    return float(sum(gv.kpi.fspcpu_list)/len(gv.kpi.fspcpu_list))

def set_kpi(name='', funname='', big_is_good='', prefix='', unit='', report=True):
    akpi = IpaMmlItem()
    akpi.name = name
    akpi.funname = funname
    akpi.big_is_good = big_is_good
    akpi.prefix=prefix
    akpi.unit = unit
    akpi.report = report
    return akpi

def get_c_plan_trigger_time():
    if gv.case.curr_case.team == 'PET3':
        return get_c_plan_trigger_time_pet3()
    else:
        try:
            cal_result_pet3 = get_c_plan_trigger_time_pet3()
            gv.logger.info('cal ue trigger result:pet3 ')
            print '%s' %(cal_result_pet3)
        except:
            pass
        return get_c_plan_trigger_time_pet1()

def get_c_plan_latency_time():
    if gv.case.curr_case.team == 'PET3':
        return get_c_plan_latency_time_pet3()
    else:
        try:
            gv.logger.info('cal result : pet3 ')
            print get_c_plan_latency_time_pet3()
        except:
            pass
        return get_c_plan_latency_time_pet1()

def get_errolog_ratio():
    count = len(gv.master_bts.error_log_list)
    timer = gv.master_bts.btslog_monitor_end - gv.master_bts.btslog_monitor_start
    return round(count/timer, 2)

def get_mix_cap_dl_tput():
    return get_download_throughput_for_mue('DOWN')

def get_mix_cap_ul_tput():
    return get_download_throughput_for_mue('UP')

def get_mix_cap_ue_num():
    return get_ue_num_for_mue()

kpi_defination = [
    set_kpi('kpi_attach_ratio',                     'kpi_attach_ratio',             True,   'RA',       r'%'),
    set_kpi('kpi_c_plan_networktrigger_latency',    'get_c_plan_trigger_time',      False,  'Total',   'ms'),
    set_kpi('kpi_c_plan_uetrigger_latency',         'get_c_plan_trigger_time',      False,  'Total',   'ms'),
    set_kpi('kpi_cplan_latency',                    'get_c_plan_latency_time',      False,  'Total',   'ms'),
    set_kpi('kpi_erab_ratio',                       'kpi_erab_ratio',               True,   'ER',       r'%'),
    set_kpi('kpi_ftp_dl',                           'get_ftp_download',             True,   'DL',       'Mbps'),
    set_kpi('kpi_ftp_ul',                           'get_ftp_upload',               True,   'UL',       'Mbps'),
    set_kpi('kpi_handover_ratio',                   'kpi_handover_ratio',           True,   'HO',       r'%'),
    set_kpi('kpi_latency_ra',                       'get_c_plan_latency_time_ra',   False,  'RA',        'ms'),
    set_kpi('kpi_paging_ratio',                     'kpi_paging_ratio',             True,   'PG',       r'%'),
    set_kpi('kpi_ping_latency_1400',                'ping_avg_time',                False,  'Total',   'ms'),
    set_kpi('kpi_ping_latency_1500',                'ping_avg_time',                False,  'Total',   'ms'),
    set_kpi('kpi_ping_latency_32',                  'ping_avg_time',                False,  'Total',   'ms'),
    set_kpi('kpi_qci1_ratio',                       'kpi_qci1_ratio',               True,   'ER',       r'%'),
    set_kpi('kpi_rrc_ratio',                        'kpi_rrc_ratio',                True,   'RC',       r'%'),
    set_kpi('kpi_service_rt_mt_ratio',              'kpi_service_rt_mt_ratio',      True,   'SVR',      r'%'),
    set_kpi('kpi_total_enb_delay',                  'get_handover_kpis',            True,   '',         ''),
    set_kpi('kpi_trigger_ra',                       'get_c_plan_trigger_time_ra',   False,  'RA',       'ms'),
    set_kpi('kpi_tti_ul',                           'get_kpi_tti_ul',               True,   'MaxUeULPerTTI', ''),
    set_kpi('kpi_uplan_dl_interruption',            'get_handover_kpis',            True,   '',         ''),
    set_kpi('kpi_uplan_ul_interruption',            'get_handover_kpis',            True,   '',         ''),
    set_kpi('kpi_volte_call_drop_ratio',            'get_volte_call_drop_ratio',    True,   'DR',       r'%'),
    set_kpi('kpi_volte_call_setup_ratio',           'get_volte_call_setup_ratio',   True,   'SR',       r'%'),
    set_kpi('kpi_volte_perm_loss_ratio',            'get_volte_loss_ratio',         True,   'PLR',      r'%'),
    set_kpi('kpi_volte_perm_mos',                   'get_volte_perm_mos',           True,   'Mos',      ''),
    set_kpi('kpi_volte_ho_ratio',                   'kpi_volte_ho_ratio',           True,   'HO',       r'%'),
    set_kpi('kpi_duration',                         'kpi_case_duration',            True,   'Duration', 'mins'),
    set_kpi('kpi_cap',                              'kpi_cap',                      True,   'CAPS',     ''),
    set_kpi('kpi_volte_cap',                        'kpi_volte_cap',                True,   'Capacity', ''),
    set_kpi('kpi_tr',                               'kpi_tr',                       True,   'TR',       ''),
    set_kpi('kpi_cpuload',                          'get_kpi_cpuload',              False,  'SystemCpu', r'%'),

    #for PRFOA
    set_kpi('kpi_prf_sr',                           'kpi_prf_sr',                   True,   'SR',           r'%'),
    set_kpi('kpi_prf_s1_sr',                        'kpi_prf_s1_sr',                True,   'SR',           r'%', False),
    set_kpi('kpi_prf_dr',                           'kpi_prf_dr',                   True,   'DR',           r'%'),
    set_kpi('kpi_prf_ho',                           'kpi_prf_ho',                   True,   'HO',           r'%'),
    set_kpi('kpi_prf_caps',                         'kpi_prf_caps',                 True,   'CAPS',         r''),
    set_kpi('kpi_prf_fctcpu',                       'get_kpi_cpuload',              False,  'FCTCPU',       r'%'),
    set_kpi('kpi_prf_fspcpu',                       'get_kpi_fspload',              False,  'FSPCPU',       r'%'),
    set_kpi('kpi_prf_duration',                     'kpi_case_duration',            True,   'Duration',     r'mins'),

    #For Volte Perm
    set_kpi('kpi_volte_vp_plr',                     'kpi_volte_vp_plr',             False,  'PLR',           r'%'),
    set_kpi('kpi_volte_vp_pd',                      'kpi_volte_vp_pd',              False,  'PD',            r''),
    set_kpi('kpi_volte_vp_pdv',                     'kpi_volte_vp_pdv',             False,  'PDV',           r''),
    set_kpi('kpi_volte_vp_pdv_99',                  'kpi_volte_vp_pdv_99',          False,  'PDV_99',        r''),
    set_kpi('kpi_volte_vp_pdv_999',                 'kpi_volte_vp_pdv_999',         False,  'PDV_999',       r''),

    #For Volte Mix Service
    set_kpi('kpi_volte_vp_qci1_plr',                'kpi_volte_vp_qci1_plr',        False,  'QCI1 PLR',      r'%'),
    set_kpi('kpi_volte_vp_qci2_plr',                'kpi_volte_vp_qci2_plr',        False,  'QCI2 PLR',      r'%'),

    #For VOLTE CAP
    set_kpi('kpi_volte_mos',                        'kpi_volte_mos',                True,   'Mos',           r''),
    set_kpi('kpi_volte_cap_qci1_plr',               'kpi_loss_ratio',               False,  'QCI1 PLR',      r'%'),


    #For Pet2
    set_kpi('kpi_errlog_ratio',                     'get_errolog_ratio',            False,  'ETO',           r''),
    set_kpi('kpi_pcell_dl_sf_fd',                   'kpi_pcell_dl_sf_fd',           True,   'DL_SF_FD',      r'%'),
    set_kpi('kpi_pcell_dl_nf_fd',                   'kpi_pcell_dl_nf_fd',           True,   'DL_FD',         r'%'),
    set_kpi('kpi_pcell_ul_nf_fd',                   'kpi_pcell_ul_nf_fd',           True,   'UL_FD',         r'%'),
    set_kpi('kpi_scell_dl_sf_fd',                   'kpi_scell_dl_sf_fd',           True,   'S_DL_SF_FD',    r'%'),
    set_kpi('kpi_scell_dl_nf_fd',                   'kpi_scell_dl_nf_fd',           True,   'S_DL_FD',       r'%'),
    set_kpi('kpi_scell_ul_nf_fd',                   'kpi_scell_ul_nf_fd',           True,   'S_UL_FD',       r'%'),
    set_kpi('kpi_dl_tput',                          'get_mix_cap_dl_tput',          True,   'DL_TPUT',       r''),
    set_kpi('kpi_ul_tput',                          'get_mix_cap_ul_tput',          True,   'UL_TPUT',       r''),
    set_kpi('kpi_ue_num',                           'get_mix_cap_ue_num',           True,   'UE_NUM',        r''),
    set_kpi('kpi_uptime',                           'pet_get_bts_uptime',           True,   'UPTIME',        r'min'),

    set_kpi('kpi_mos',                              'kpi_volte_mos',                True,   'Mos',           r''),


]


def get_c_plan_trigger_time_pet3():
    gv.logger.info('get_c_plan_trigger_time_pet3')
    parch_data  = read_data_file('PRACH', parch_format)
    t1 = float(calc_sfn(parch_data[1]))/10

    dll_data    = read_data_file('DLL1L2CONTROL', dll_format, 'RACH')
    t2 = float(calc_sfn(dll_data[1]))/10

    T1 = (t2-t1)*10-1
    print t1, t2, T1

    rxdata      = read_data_file('MACRX_', rxformat)
    rxdata      = [x for x in rxdata if 'id' in x.keys()]
    txdata      = read_data_file('MACTX_', txformat)
    txdata      = [x for x in txdata if 'id' in x.keys()]


    rxdata1 = [x for x in rxdata if x['id'] in ['0', '1']]
    txdata1 = [x for x in txdata if x['id'] in ['0', '1']]
    t3 = float(calc_sfn([x for x in rxdata1 if x['id'] == '0'][1]))/10
    t4 = float(calc_sfn([x for x in txdata1 if x['id'] == '0'][1]))/10
    print t3, t4
    T2 = (t3-t4)*10-1
    print T2

    count = 0
    for i in range(len(rxdata1)):
        if rxdata1[i]['id'] == '0':
            if count == 0:
                count = 1
            else:
                leftlines = rxdata1[i+1:]
                for temp in leftlines:
                    print temp
                print leftlines[0]
                t5 =  float(calc_sfn([x for x in leftlines if x['len'] in ['10', '20']][0]))/10
                break
    print 't5: ', t5

    count = 0
    for i in range(len(txdata1)):
        if txdata1[i]['id'] == '0':
            if count == 0:
                count = 1
            else:
                leftlines = txdata1[i+1:]
                print leftlines[0]
                t6 =  float(calc_sfn([x for x in leftlines if x['id'] in ['1']][0]))/10
                break
    print 't6: ', t6
    T3 = (t5-t6)*10
    print T3

    filename= pathc(case_file('local.txt'))
    #filename = os.sep.join([gv.tm500_log_dir, 'local.txt'])
    T4 = round(parse_pcap_trigger(filename)*1000, 3)
    print T4

    T5 = T3 - T4
    print T1, T2, T3, T4, T5

    T = T1 + T2 + T5
    print T
    gv.kpi.kpi_trigger_ra = round(T1, 5)
    return round(T, 5)


def get_c_plan_latency_time_pet3():
    gv.logger.info('get_c_plan_latency_time_pet3')
    parch_data  = read_data_file('PRACH', parch_format)
    t1 = float(calc_sfn(parch_data[0]))/10
    print t1
    dll_data    = read_data_file('DLL1L2CONTROL', dll_format, 'RACH')
    t2 = float(calc_sfn(dll_data[0]))/10
    print t2

    T1 = (t2-t1)*10 -1
    print T1

    rxdata      = read_data_file('MACRX_', rxformat)
    rxdata      = [x for x in rxdata if 'id' in x.keys()]
    txdata      = read_data_file('MACTX_', txformat)
    txdata      = [x for x in txdata if 'id' in x.keys()]

    rxdata1 = [x for x in rxdata if x['id'] in ['0', '1']]
    txdata1 = [x for x in txdata if x['id'] in ['0', '1']]

    t3 = float(calc_sfn([x for x in rxdata1 if x['id'] == '0'][0]))/10
    t4 = float(calc_sfn([x for x in txdata1 if x['id'] == '0'][0]))/10
    print t3, t4
    T2 = (t3-t4)*10-1
    print T2

    count = 0

    for i in range(len(rxdata1)):
        if rxdata1[i]['len'] == '20':
            t5 =  float(calc_sfn(rxdata1[i]))/10
            break
        elif rxdata1[i]['len'] == '10':
            if count == 0:
                count = 1
            else:
                t5 =  float(calc_sfn(rxdata1[i]))/10
                break
    print 't5: ', t5

    t6 =  float(calc_sfn([x for x in txdata1 if x['id'] in ['1']][0]))/10
    print 't6: ', t6
    T3 = (t5-t6)*10 if t5 >= t6 else (1023-t6+t5)*10
    print T3

    #filename = os.sep.join([gv.tm500_log_dir, 'local.txt'])
    filename= pathc(case_file('local.txt'))
    T4 = round(parse_pcap(filename, 'Attach request', 'Attach accept') * 1000, 3)
    print T4

    T5 = T3 - T4
    print T5

    maxlen =  max([int(x['len']) for x in rxdata1])
    t9 =  float(calc_sfn([x for x in rxdata1 if x['len'] == str(maxlen)][0]))/10
    print t9

    print [calc_sfn(x) for x in txdata1 if calc_sfn(x) < t9 *10]
    #t10_data=x for x in txdata1 if calc_sfn(x) < t9 *10
    t10_a=max([(calc_sfn(x),x['len'],x['len2']) for x in txdata1 if (t9 *10 + 10240 - calc_sfn(x)) % 10240 < 10240 / 2])
    print 'T10_a:',t10_a
    if t10_a:
        if (int(t10_a[1]) > 2) or (int(t10_a[2] > 2)):
            t10=float(t10_a[0])/10
            print t10
            T6 = (t9-t10)*10-1
            gv.kpi.kpi_latency_ra = round(T1, 5)
            print 'T1: %0.3f, T2: %0.3f, T3: %0.3f, T4: %0.3f, T5: %0.3f, T6: %0.3f' %(T1, T2, T3, T4, T5, T6)
            return round(T1+T2+T5+T6, 5)
        else:
            print "Error logs"

            return "Error logs"

    #t10 = float(max([calc_sfn(x) for x in txdata1 if calc_sfn(x) < t9*10 and int(x['len']) > 2 ]))/10
    #print t10

##    T6 = (t9-t10)*10-1
##
##    gv.kpi_latency_ra = T1
##    print 'T1: %0.3f, T2: %0.3f, T3: %0.3f, T4: %0.3f, T5: %0.3f, T6: %0.3f' %(T1, T2, T3, T4, T5, T6)
##    return T1+T2+T5+T6

if __name__ == '__main__':
    # for kw in [kw for kw in dir(__file__) if not kw.startwith('_')]:
    #     print kw

    gv.tm500 = IpaMmlItem()
    gv.tm500.tm500_log_dir = '/home/work/Jenkins2/workspace/YSF_TL17SP_F_T/67/529732_2017_06_16__14_38_03/529732_07_01_03_S/Tmftpdl'
    # gv.case.log_directory = '/home/work/Jenkins2/workspace/TL17_TPUT_FSIH/20161012_1225/TA_CAP_00111_20M_ULDL2_SSF5_TM3_UE_TRIGGER__2016_10_12__12_41_11/F5_1UE_NO1'
    # from pet_bts import     new_parse_pcap_file
    gv.master_bts = IpaMmlItem()
    gv.master_bts.uldl = '2'
    gv.master_bts.ssf = '5'
    print get_download_throughput_for_3cc()



    # r1 = r'D:\temp\1\handover'
    # gv.case_log_directory = r1 + r'\TEST_FOR_LATENCY'
    # gv.tm500_log_dir = '/tmp/ta'
    # print tm500_log_is_valid_for_handover()
    # get_intra_enb_handover_kpis()
    # read_data_file('_UEOVERVIEW_NA_', throughput_format_3cc)
    # print parse_pcap(pcapfilename, 'Attach request', 'Attach accept')
    # print get_c_plan_latency_time()
    # print parse_pcap(r'd:\temp\04\local.txt')
    # gv.tm500_log_dir = r'd:\temp\tm501'
    # gv.case_log_directory = r'd:\temp\tm501'
    # print get_c_plan_trigger_time()
    # print gv.kpi_through_ul
    # gv.master_bts = IpaMmlItem()
    # gv.master_bts.max_tti_user = ''
    # gv.master_bts.ssf = '7'
    # gv.master_bts.band = '20'
    # gv.master_bts.ul_sps = ''
    # get_kpi_tti_dl_nfn()

    # get_volte_tti_kpi()
    # for kpi in kpi_defination:
    #     print kpi.name
    # kpis = kpi_keywords.keys()
    # kpis.sort()
    # for kpi in kpis:
    #     print "set_kpi('%s', '%s', True)," %(kpi, kpi_keywords[kpi])
    pass
