from petbase import *
from pet_pa_c import *

'''
This unit will define some keyword for specific device, such as PA/RFSwitch, Prisma, etc
The basic solution is:
      1. Define the device class in the a py model, use class
      2. Define the keywords that use or call the device, provide the keywords for Robot.
'''

'''
    PA Part, provide a keyword to adjust RF signal
'''

def adjust_pa_according_to_palist():
    if pv('ADJUST_PA') == 'Y':
        painfo = get_rf_config()
        adjust_rf_switch_signal_for_bts(painfo)

def get_rf_solution():
    if gv.case.curr_case.pasolution.strip():
        return gv.case.curr_case.pasolution.strip().upper()
    if gv.case.curr_case.ca_type == '' or gv.case.curr_case.ca_type == 'NCA':
        if gv.case.curr_case.tm in ['98X4', '94X4']:
            return '98X4'
        else:
            return 'NCA'
    else:
        return gv.case.curr_case.ca_type

def get_rf_config():
    painfo = []
    rfinfo = gv.adb.get_table_content('v_rfconn')
    # gv.logger.info(rfinfo)
    for acase in rfinfo:
        if acase.btsid not in [x.btsid for x in gv.allbts]:
            continue
        acase.used = False if acase.used == 'N' else True
        acase.loadtoolid = acase.tm500id
        acase.inport = int(acase.inport)
        acase.outport = int(acase.outport) if acase.outport.strip() else 0
        acase.signal = round(float(acase.signals))
        # if acase.outport == 0: #for PA
        if gv.case.curr_case.case_type.upper() == 'MIX_MR' and gv.case.curr_case.ho_type.upper() == 'INTER':
            if acase.btsid == gv.master_bts.bts_id:
                acase.used = int(acase.rruid) == gv.master_bts.workcell
            if gv.slave_bts:
                if acase.btsid == gv.slave_bts.bts_id:
                    acase.used = int(acase.rruid) == gv.slave_bts.workcell
        if gv.env.use_tm500:
            if acase.used and int(acase.loadtoolid) == int(gv.tm500.tm500_id) and acase.outport == 0:
                painfo.append(acase)
            if acase.used and int(acase.loadtoolid) == int(gv.tm500.tm500_id) and acase.outport <>0 and acase.solution.upper() == get_rf_solution().upper():
                painfo.append(acase)
    return painfo

def adjust_rf_switch_signal_for_bts(painfo):
    btsinfoall = []
    for btsid in [x.bts_id for x in gv.allbts]:
        btsinfoall += [x for x in painfo if x.btsid == btsid]
    if len(btsinfoall) == 0:
        raise Exception, 'Could not find the RC connection configuration for this case, case will fail.'
    gv.logger.info(btsinfoall)
    rfswitch_info = gv.adb.get_table_content('tblrfinfo')
    for apa in rfswitch_info:
        rfconnections = [x for x in btsinfoall if x.rfswitch == apa.rfswitch]
        if len(rfconnections) == 0:
            continue
        if 'RF' in apa.rfswitch.upper():
            if apa.type == 'JX':
                device = c_jx_matrix(apa.accessip, str(int(apa.accessport)), apa.inport_count, apa.outport_count)
            if apa.type == 'HB':
                device = c_hb_matrix(apa.accessip, str(int(apa.accessport)), apa.inport_count, apa.outport_count)
            device.clear_all(rfconnections)
        else:
            if apa.type == 'JX':
                device = c_jx_pa(apa.accessip, str(int(apa.accessport)), apa.inport_count, 1)
            if apa.type == 'HB':
                device = c_hb_pa(apa.accessip, str(int(apa.accessport)), apa.inport_count, 1)
            device.clear_all()

        gv.logger.info(rfconnections)
        try:
            for rfconnection in rfconnections:
                device.change_signal(rfconnection.inport, rfconnection.outport, rfconnection.signal)
        finally:
            device.disconnect()

'''
    Prisam Part
'''

def prepare_prisma_before_onair():
    pass

def prepare_prisma_after_onair():
    gv.prisma = None
    if gv.env.loadtool.name.upper().strip() == 'PRISMA':
        from pet_prisma_c import c_pet_prisma
        gv.prisma           = c_pet_prisma(gv.env.loadtool.id)
        gv.prisma.case      = gv.case.curr_case
        gv.prisma.bts_list  = gv.allbts
        gv.prisma.setup()
    # raise Exception, 'Stop by prisam setup'

def setup_asc_before_tm500_restart():
    from pet_tm500_asc import asc_manager
    gv.tm500.asc = asc_manager(gv.tm500)
    gv.tm500.asc.onBeforeTm500Restart()

def setup_asc_after_tm500_restart():
    if gv.tm500.asc:
        gv.tm500.asc.onAfterTm500Restart()

'''
    PB Part
'''

'''
    Artiza Part
'''
def prepare_artiza_before_bts_onair():
    gv.artiza = None
    if gv.env.loadtool.name.upper().strip() == 'ARTIZA':
        from pet_artiza_c import c_pet_artiza
        gv.artiza = c_pet_artiza(gv.env.loadtool.id, gv.logger)
        gv.artiza.set_case(gv.case.curr_case)
        if gv.debug_mode <> 'DEBUG':
            gv.artiza.set_sm_logfile(case_file('artiza.log'))
        gv.artiza.setup()

def prepare_artiza_after_bts_onair():
    if gv.artiza:
        gv.artiza.sm.setup_after_bts_onair()
    pass

if __name__ == '__main__':
    # gv.master_bts =
    # get_rf_config()
    gv.env = IpaMmlItem()
    gv.env.loadtool = IpaMmlItem()
    gv.env.loadtool.name = 'TM500'
    gv.env.loadtool.id = '225'
    gv.case = IpaMmlItem()
    gv.case.curr_case = IpaMmlItem()
    gv.team = 'PET1'
    gv.case.log_directory = '/home/work/jrun/1'
    import pettool
    from pet_db import initlize_db
    initlize_db()
    gv.env.use_tm500 = True
    gv.tm500 = IpaMmlItem()
    gv.tm500.tm500_id = '225'
    gv.case.curr_case = pettool.get_case_config('486347')
    from pet_bts import read_bts_config
    gv.master_bts = read_bts_config('642', 'M', 'P')
    print get_rf_config()
    pass
