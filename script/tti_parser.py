import os, sys, time, datetime
import subprocess
from  optparse import *
from thread import *
from petbase import *
from threading  import Thread

tti_file_list = []
service_done = False

debug_filename = '/tmp/mixcap.log'
output_log = ''
filelock = threading.Lock()
datafilelock = threading.Lock()
write_lock = threading.Lock()

def debuginfo(info):
    import datetime
    now = datetime.datetime.now()
    astr = '%s  %-100s ' %(now.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3], info)
    with write_lock:
        print astr

def get_tti_correct_name(filename, cores):
    corelist = cores.split(',')
    ullist = [x for x in corelist if corelist.index(x)%2 == 0]
    dllist = [x for x in corelist if corelist.index(x)%2 == 1]
    for core in ullist:
        if core in filename:
            return filename.replace('_dl', '_ul')
    for core in dllist:
        if core in filename:
            return filename.replace('_ul', '_dl')

def pet_tti_file_monitor_thread(path, cores):
    filelist = []
    while not service_done:
        known_file_list = [x.name for x in filelist]
        for basename in os.listdir(path):
            if basename.endswith('.dat'):
                filename =  os.sep.join([path, basename])
                if basename in known_file_list:
                    thefile = [x for x in filelist if x.name == basename][0]
                    if not thefile.finished:
                        if int(os.path.getsize(thefile.longname)) == int(thefile.size) and int(thefile.size) > 1000:
                            thefile.name = get_tti_correct_name(thefile.name, cores)
                            newfilename  = get_tti_correct_name(thefile.longname, cores)
                            if newfilename.upper().strip() <> thefile.longname.upper().strip():
                                # debuginfo(newfilename)
                                # debuginfo(thefile.longname)
                                debuginfo('Rename dat file  {} to: {}'.format(thefile.name, os.path.basename(newfilename)))
                                os.rename(thefile.longname, newfilename)
                                thefile.longname = newfilename
                            thefile.finished = True
                            tti_file_list.append(thefile)
                else:
                    thefile = IpaMmlItem()
                    thefile.name = basename
                    thefile.size = os.path.getsize(filename)
                    thefile.longname = filename
                    thefile.converted = False
                    thefile.finished = False
                    thefile.calculated = False
                    thefile.ongoing = False
                    filelist.append(thefile)
        time.sleep(30)

def pet_tti_parse_thread(parser, num):
    threadname = 'P'+str(num)
    while not service_done:
        thefile = lock_a_dat_file_to_process()
        if thefile:
            thefile.csvfile = thefile.longname.replace('.dat', '.csv')
            debuginfo('{}   Parse file:          {}'.format(threadname, thefile.name))
            if os.path.getsize(thefile.longname) > 1024*1024:
                cmd = '%s %s %s >> /tmp/tti.log' %(parser, thefile.longname, thefile.csvfile)
                os.system(cmd)
            else:
                debuginfo('{}   The dat file:        {} size is too small ({}bytes), skip it.'.format(threadname, thefile.name, os.path.getsize(thefile.longname)))
                thefile.calculated = True
            free_a_dat_file(thefile)

def pet_tti_calc_thread(cells, bands, fd20, btstype, num):
    if btstype == 'FDD':
        return 0
    threadname = 'C'+str(num)
    while not service_done:
        thefile = lock_a_csv_file_to_process()
        if thefile:
            debuginfo('{}   Calcualte file:      {}'.format(threadname, os.path.basename(thefile.csvfile)))
            if not os.path.exists(thefile.csvfile):
                debuginfo('CSV file does not exit')
            else:
                if '_dl_' in thefile.csvfile:
                    calc_dl_tti_kpi(thefile.csvfile, cells, bands, fd20)
                else:
                    calc_ul_tti_kpi(thefile.csvfile, cells, bands, fd20)
                if os.path.exists(thefile.csvfile):
                    os.remove(thefile.csvfile)
                if os.path.exists('{}.harq'.format(thefile.csvfile)):
                    os.remove('{}.harq'.format(thefile.csvfile))
            free_a_csv_file(thefile)

def get_column_index(title, column_name):
    ltitles = [x.upper() for x in title if x.strip()]
    if column_name.upper() in ltitles:
        return ltitles.index(column_name.upper())
    else:
        return -1

def calc_dl_tti_kpi(csvfile, cells, bands, fd20):
    dldata = []
    title = []
    lines = open(csvfile).readlines()
    title = lines[1].split(',')
    index_esfn      = get_column_index(title, 'ETtiTraceDlParCell_esfn')
    index_cellid    = get_column_index(title, 'ETtiTraceDlParCell_cellId')
    index_numuefd   = get_column_index(title, 'ETtiTraceDlParCell_numUesFd')
    debuginfo('Found three column index: {}, {}, {}'.format(index_esfn, index_cellid, index_numuefd))
    if index_esfn == -1 or index_cellid == -1 or index_numuefd == -1:
        debuginfo('Invalid Column index found.')
        return 0

    for line in open(csvfile).readlines()[2:]:
        esfn    = line.split(',')[index_esfn]
        cellid  = line.split(',')[index_cellid]
        numuefd = line.split(',')[index_numuefd]
        if esfn == '-' or cellid in ['-', '0'] or numuefd == '-':
            continue
        adata = IpaMmlItem()
        adata.esfn, adata.cellid, adata.numuefd = esfn, cellid, numuefd
        dldata.append(adata)

    if dldata:
        cellid = dldata[0].cellid
        cell_index = cells.split(',').index(cellid)
        band = bands.split(',')[cell_index]
        snumuefd = '8' if band == '20' else '7'
        snumuefd = '12' if fd20 in ['Y', '1'] else snumuefd
        nnumuefd = '12' if band == '20' else '10'
        nnumuefd = '20' if fd20 in ['Y', '1'] else nnumuefd
        kpi_sf_dl = round(len([x for x in dldata if x.esfn in ['1', '6'] and x.numuefd == snumuefd]) *100/len([x for x in dldata if x.esfn in ['1', '6']]), 4)
        kpi_nf_dl = round(len([x for x in dldata if x.esfn not in ['1', '6'] and x.numuefd == nnumuefd]) *100/len([x for x in dldata if x.esfn not in ['1', '6']]), 4)
        debuginfo( 'DL Special Frame and DL Normal Frame ratio: {}, {}'.format(kpi_sf_dl, kpi_nf_dl))
        with write_lock:
            with open(output_log, 'a') as f:
                f.write('DL,%s,%s,%s,%s\n' %(cellid, kpi_sf_dl, kpi_nf_dl, os.path.basename(csvfile)))
        return dldata[0].cellid, kpi_sf_dl, kpi_nf_dl
    else:
        debuginfo('No valid data in csv file.')

def calc_ul_tti_kpi(csvfile, cells, bands, fd20):
    uldata = []
    title = []
    lines = open(csvfile).readlines()
    title = lines[1].split(',')
    index_esfn      = get_column_index(title, 'ETtiTraceUlParCell_esfn')
    index_cellid    = get_column_index(title, 'ETtiTraceUlParCell_cellId')
    index_numuefd   = get_column_index(title, 'ETtiTraceUlParCell_numUesFd')
    debuginfo('Found three column index: {}, {}, {}'.format(index_esfn, index_cellid, index_numuefd))
    if index_esfn == -1 or index_cellid == -1 or index_numuefd == -1:
        debuginfo('Invalid Column index found.')
        return 0, 0

    for line in lines[2:]:
        esfn    = line.split(',')[index_esfn]
        cellid  = line.split(',')[index_cellid]
        numuefd = line.split(',')[index_numuefd]
        if esfn == '-' or cellid in ['-', '0'] or numuefd == '-':
            continue
        if index_esfn == -1  or index_cellid == -1 or index_numuefd == -1:
            print 'Invalid column index'
            return 0, 0
        adata = IpaMmlItem()
        adata.esfn = esfn
        adata.cellid = cellid
        adata.numuefd = numuefd
        uldata.append(adata)
    cellid = uldata[0].cellid
    cell_index = cells.split(',').index(cellid)
    band = bands.split(',')[cell_index]
    nnumuefd = '12' if band == '20' else '10'
    nnumuefd = '20' if fd20 in ['Y', '1'] else nnumuefd
    kpi_nf_ul = round(len([x for x in uldata if x.esfn not in ['1', '6'] and x.numuefd == nnumuefd]) *100/len([x for x in uldata if x.esfn not in ['1', '6']]), 4)
    debuginfo('UL Normal Frame ratio: {}'.format(kpi_nf_ul))
    with write_lock:
        with open(output_log, 'a') as f:
            f.write('UL,%s,0,%s,%s\n' %(cellid, kpi_nf_ul, os.path.basename(csvfile)))
    return cellid, kpi_nf_ul

def lock_a_csv_file_to_process():
    with filelock:
        files = [x for x in tti_file_list if x.converted and not x.calculated and not x.ongoing]
        if files:
            thefile = files[0]
            thefile.ongoing = True
            return thefile
        else:
            return None

def free_a_csv_file(thefile):
    with filelock:
        thefile.calculated = True
        thefile.ongoing = False

def lock_a_dat_file_to_process():
    with datafilelock:
        files = [x for x in tti_file_list if not x.converted and not x.ongoing]
        if files:
            thefile = files[0]
            thefile.ongoing = True
            return thefile
        else:
            return None

def free_a_dat_file(thefile):
    with datafilelock:
        thefile.converted = True
        thefile.ongoing = False


def main(args = sys.argv[1:]):
    parser = OptionParser()
    parser.add_option("-d",  dest="dire", default='', help='The dat file directory')
    parser.add_option("-t",  dest="parser", default='', help='the parser tool')
    parser.add_option("-c",  dest="cells", default='101', help='cell id list, like: 101,102')
    parser.add_option("-b",  dest="bands", default='20', help='band list, like: 10,20')
    parser.add_option("-r",  dest="cores", default='1236,1235', help='band list, like: 10,20')
    parser.add_option("-f",  dest="fd20",  default='N', help='feature for FD 20UE')
    parser.add_option("-m",  dest="btstype",  default='TDD', help='BTS Type, like TDD or FDD')
    (options, args) = parser.parse_args()
    global output_log, filelock, datafilelock
    output_log = os.sep.join([options.dire, 'tti_result.log'])
    filelock = threading.Lock()
    datafilelock = threading.Lock()
    with open(output_log, 'w') as f:
        f.write('Direction,cellid,sf,nf\n')
    start_new_thread(pet_tti_file_monitor_thread, (options.dire, options.cores,))
    for i in range(4):
        start_new_thread(pet_tti_parse_thread, (options.parser, i+1, ))
    for i in range(6):
        start_new_thread(pet_tti_calc_thread, (options.cells, options.bands, options.fd20, options.btstype, i+1,))
    while True:
        with open(os.sep.join([options.dire, 'leftdat.log']), 'w') as f:
            for thefile in [x for x in tti_file_list if not x.calculated]:
                f.write(thefile.name+'\n')
        time.sleep(10)
        pass


if __name__ == '__main__':
    main()
    #filename = '/home/work/Jenkins2/workspace/PET2_TL17_2188/36/TA_TL17PET2_CAP_00166_20M_ULDL2_SSF7_TM4X2_DRX_CAP__2016_10_24__22_07_22/S_POOL_NO1/tti/TtiTrace_20161024141501_1235_ul_0080.csv'
    #calc_dl_tti_kpi(filename, '101', '20', 'N')
