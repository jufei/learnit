from petbase import *
import pet_tm500_script_builder

def _add_usim(startusim, number):
    return str(int(startusim) + int(number))

def _get_usim_str(startusim):
    tsr = 'forw mte UsimConfig 1([%s+1 2] [] [] [] []) [] [] '%(startusim)
    tsr += '[00112233445566778899AABBCCDDEEFF] [01020304050607080910111213141516 '
    tsr += '00000000000000000000000000000000 00000000000000000000000000000001 '
    tsr += '00000000000000000000000000000002 00000000000000000000000000000004 '
    tsr += '00000000000000000000000000000008 64 0 32 64 96 []] [] []'
    return tsr

def _get_usim_str_single(startusim):
    tsr = ' 1([%s 2] [] [] [] []) [] [] '%(startusim)
    tsr += '[00112233445566778899AABBCCDDEEFF] [01020304050607080910111213141516 '
    tsr += '00000000000000000000000000000000 00000000000000000000000000000001 '
    tsr += '00000000000000000000000000000002 00000000000000000000000000000004 '
    tsr += '00000000000000000000000000000008 64 0 32 64 96 []] [] []'
    return tsr

def add_shenick_group(service, startue, uecount):
    g = IpaMmlItem()
    g.name = service
    g.startue = startue
    g.ue_count = uecount
    gv.shenick_groups.append(g)

def set_enb_position_entity2(cell_id = 0,dl_frequency = 0, cell_range = 0,ref_signal_power = 0):
    return '%s %s %s [] [%s]' %(cell_id, dl_frequency, cell_range, ref_signal_power)

def add_volte_shenick_group(startue = '', uecount = 10, start_sip_number = '861800003874',
                      bitrate_type = 'NB', bitrate_level = '3'):
    g = IpaMmlItem()
    g.name = 'volte'
    g.startue = startue
    g.ue_count = uecount
    g.start_sip_number = start_sip_number
    g.bitrate_type = bitrate_type
    g.bitrate_level = bitrate_level
    gv.shenick_groups.append(g)

def get_tput_attach_script(bts):
    if gv.case.curr_case.tm500_attach_file:
        filename = bts_source_file(bts.bts_id, gv.case.curr_case.tm500_attach_file)
        return open(filename, 'r').readlines()
    if gv.case.curr_case.ca_type.strip() == '3CC':
        script = get_3cc_attach_script_for_tput(bts)
    elif gv.case.curr_case.ulca:
        script = get_ulca_attach_script_for_tput(bts)
    else:
        script = get_general_script_for_tput(bts)
    return script

def get_general_script_for_tput(bts):
    case = gv.case.curr_case
    script = [      'SETP L2_MAC_ENABLE_CR379_R2_094167 1',
                    'SETP L2_MAC_ENABLE_REL_9_CR409 1',
                    'SETP RRC_ENABLE_RELEASE_11 1',
                    'SETP NAS_ENABLE_R10 1',
                    'SETP L2_MAC_DISABLE_SR_INIT_RACH_IF_SR_NOT_CFG 1',]
    if str(bts.bandname) in ['41']:
        script += ['forw mte RrcAptOverrideBandSupport 2{41 [1 24960 39650 1940 24960 39650 1940] [],41 [1 24960 39650 1940 24960 39650 1940] []} [0]',
                   'forw mte Activate -1 [] [1]']
    if bts.btstype == 'TDD' and case.ca_type.strip() == '2CC':
        script += ['forw l1 MapFreqToRadioContext 0 1 %d %d' %(int(bts.dl_frequency_pcell)-100, int(bts.dl_frequency_pcell)+100),
                   'forw l1 MapFreqToRadioContext 1 1 %d %d' %(int(bts.dl_frequency_scell)-100, int(bts.dl_frequency_scell)+100),]
    else:
        if bts.btstype == 'TDD':
            script += ['forw mte PhyConfigUlTiming 0',]


    tm1 = 4 if case.tm in ['4X2'] else 2
    tm2 = 1 if case.tm in ['1'] else 2
    bandlist = case.band.upper().replace('M', '').split('-')
    ms_bandlist = case.ms_band.upper().replace('M', '').split('-')


    if bts.btstype == 'FDD' and case.ca_type in ['2CC']:
        script += ['forw mte SetMueRadioContextCell 0 %s %s %s [%s] [] [%s]' %(
                        bts.phycellid_list[0], bts.dl_frequency_pcell, bandlist[1],
                        tm1, tm2)]
        script += ['forw mte SetMueRadioContextCell 1 %s %s %s [%s] [] [%s]' %(
                            bts.phycellid_list[1], bts.dl_frequency_scell, bandlist[0],
                            tm1, tm2)]
    if gv.ms_bts:
        tm1 = 4 if case.ms_tm in ['4X2', '4X2-4X2'] else 2
        tm2 = 1 if case.ms_tm in ['1'] else 2

        if gv.ms_bts.btstype =='TDD' and case.ca_type in ['2CC']:
            script += ['forw mte SetMueRadioContextCell 2 %s %s %s [%s] [%s %s] [%s]' %(
                            gv.ms_bts.phycellid_list[0], gv.ms_bts.dl_frequency_pcell, ms_bandlist[0],
                            tm1, case.ms_uldl, case.ms_ssf, tm2)]
            script += ['forw mte SetMueRadioContextCell 3 %s %s %s [%s] [%s %s] [%s]' %(
                            gv.ms_bts.phycellid_list[1], gv.ms_bts.dl_frequency_scell, ms_bandlist[1],
                            tm1, case.ms_uldl, case.ms_ssf, tm2)]

    if bts.btstype == 'FDD' and case.ca_type in ['2CC']:
        script += ['forw mte PhyConfigUlPowerOffset 1{-1 85 80 [80] []}']
        script += ['forw mte MtsConfigUeGroup 0 0 1{0}']
    if (case.ca_type == '2CC' and case.tm =='4X4-4X4') or (bts.btstype == 'FDD' and case.ca_type in ['2CC']):
        gv.tm500.shenick_volte_group_name = 'MUE_UDP'
        script += [ 'forw mte DeConfigRdaStartTestCase 0 %s [%s] [%s]' %(gv.tm500.shenick_hostname,
                            gv.tm500.shenick_partition, gv.tm500.shenick_volte_group_name)]
        script += ['WAIT FOR "I: CMPI DTE RDA TEST GROUP STARTED IND:"']
    if bts.btstype == 'TDD':
        script += ['forw mte PhySetTDDCfg %s %s' %(case.uldl, case.ssf)]

    value = '4' if case.tm in ['4X2', '4X4', '94X4', '4X2-4X2', '4X4-4X4'] else '2'
    value = '1' if case.tm in  ['1', '1-1'] else value
    value = '4' if bts.btstype == 'FDD' and case.ca_type in ['2CC'] else value
    script += ['SETP RRC_NUM_DL_ANTENNAS %s' %(value),]

    value = '2 6 6' if case.ca_type.strip() else '2 4 4'
    value = '2 4 5' if case.cat5 else value
    value = '4 5 5' if case.tm in ['4X4', '94X4', '98X4'] else value
    value = '4 16 5' if case.tm in ['4X4-4X4'] else value
    value = '2 15 4' if bts.btstype == 'FDD' and case.ca_type in ['2CC'] else value
    if case.ca_type.strip() == '2CC':
        band = case.band.strip().replace('M','')
        if band == '20-20':
            script += [ 'forw mte RrcAptConfigUeCap [[] [] [] [] [] [] [1{0 %s}]]' %(bts.uecap_20m_20m),
                    'forw mte Activate -1 [] [1]']
        if band == '20-10':
            script += [ 'forw mte RrcAptConfigUeCap [[] [] [] [] [] [] [1{0 %s}]]' %(bts.uecap_20m_10m),
                    'forw mte Activate -1 [] [1]']
        if band == '10-20':
            script += [ 'forw mte RrcAptConfigUeCap [[] [] [] [] [] [] [1{0 %s}]]' %(bts.uecap_10m_20m),
                    'forw mte Activate -1 [] [1]']

    if case.ue_cap:
        script += ['forw mte RrcAptConfigUeCap [[] [] [] [] [] [] [1{0 %s}]] [4]' %(gv.case.curr_case.ue_cap) ,
                   'forw mte Activate -1']

    if case.cat5:
        script += [ 'forw mte RrcAptConfigUeCap [[] [] [] [] [] [] [1{0 823FF400940003F068C41000}]]',
                    'forw mte Activate -1 [] [1]']
    if case.tm in ['4X4', '94X4', '98X4']:
        script += [ 'forw mte RrcAptConfigUeCap [[] [] [] [] [] [] [1{0 CA3E0441954010381FF8376260008017A31000072800209FF900000A2000}]]',
                    'forw mte Activate -1 [] [1]']

    script += [     'forw mte PhyConfigSysCap %s' %(value),]
    script += [     'forw mte UsimConfig ' + _get_usim_str_single(bts.start_ue_imsi)]
    script += [     'forw mte NasConfigEmmRegister 0(0 [0] [] [] [] [] [] [] [])',
                    'forw mte NasAptConfigPlmnSelection 26203',
                    'forw mte NasAptConfigCapability',
                    'forw mte RrcAptConfigCapability',                    ]
    script += [     'forw mte RrcAptConfigCellSelection %s' %(bts.dl_frequency_pcell),
                    'forw mte Activate -1',]
    return script


def get_volte_tm500_script(bts):
    if gv.case.curr_case.tm500_attach_file:
        filename = bts_source_file(bts, gv.case.curr_case.tm500_attach_file)
        return open(filename, 'r').readlines()
    if gv.case.curr_case.volte_crg:
        return get_volte_cap_crg_script(bts)
    elif gv.case.curr_case.case_type in ['VOLTE_PERM', 'VOLTE_MIX']:
        return get_volte_performance_script(bts)
    else:
        return _get_volte_cap_script(bts)

def get_volte_cap_crg_script(bts):
    script = []
    tm1, tm2 = 2, 2
    if bts.tm in ['4X2']:
        tm1 = 4
    if bts.tm in ['1']:
        tm1, tm2 = 1, 1

    tm1 = 4 if bts.tm in ['4X2'] else 2
    tm2 = 1 if bts.tm in ['1'] else 2
    bandlist = bts.band.upper().replace('M', '').split('-')
    script += ['forw mte SetMueRadioContextCell 0 %s %s %s [%s] [%s %s] [%s]' %(
                        bts.phycellid_list[0], bts.dl_frequency_pcell, bandlist[0],
                        tm1, bts.uldl, bts.ssf, tm2),
               'SETP RRC_NUM_DL_ANTENNAS %s' %(tm1),]
    script += [ 'forw mte DeConfigRdaStartTestCase 0 %s [%s] [%s]' %(gv.tm500.shenick_hostname,
                            gv.tm500.shenick_partition, gv.tm500.shenick_volte_group_name),
                'SETP NAS_DISABLE_REPLAY_PROTECTION 1',
                'WAIT FOR "I: CMPI DTE RDA TEST GROUP STARTED IND:"',]
    script += [
                'SETP RRC_TEST_DISABLE_CONNECTED_MEAS_PROCESSING 0',
                'FORW L1 Msg4BypassContentionResolution 1',
                'SETP NAS_ENABLE_INDICATIONS_IN_MTS_MODE 1',
                'SETP RRC_PUCCH_CLOSE_LOOP_POWER_CONTROL 0',
                'forw mte PhyConfigUlPowerOffset 1{-1 80 80 [100] []}',
                'forw mte MtsClearMts',]

    group_ue_count = int(gv.case.curr_case.ue_count)/len(gv.tm500.crg_usims)
    group_ue_count = (group_ue_count/2)*2
    for i in range(len(gv.tm500.crg_usims)):
        groupid = str(i)
        startue = i*group_ue_count
        endue = startue + group_ue_count - 1
        startusim = gv.tm500.crg_usims[i]
        script += [ 'forw mte MtsConfigUeGroup %s 0 1{%s-%s}' %(groupid, startue, endue),
                    'forw mte SetUEGroupContext %s' %(groupid),
                    'forw mte UsimConfig 1([%s+1 2] [] [] [] []) [] [] [00112233445566778899AABBCCDDEEFF] [01020304050607080910111213141516 00000000000000000000000000000000 00000000000000000000000000000001 00000000000000000000000000000002 00000000000000000000000000000004 00000000000000000000000000000008 64 0 32 64 96 []] [] []' %(startusim),
                    ]
    gv.case.curr_case.real_ue_count = int(group_ue_count)*len(gv.tm500.crg_usims)
    script += [
                'forw mte MtsConfigUeGroup 4 0 1{0-%s}' %(gv.case.curr_case.real_ue_count-1),
                'forw mte SetUEGroupContext 4',
                'forw mte PhyConfigSysCap 2 4 4',
                'forw mte RrcAptConfigCapability',
                'forw mte NasAptConfigCapability [] [224] [224]',
                'forw mte RrcAptConfigCellSelection %s [%s]' %(bts.dl_frequency_pcell, bts.phycellid_list[0]),
                'forw mte MtsConfigTrafficProfile 0 2{internet.nsn.com 0{} [] [],srvcc.nsn.com 1{0(cvoip -1) 1 [0 0 1]} [] []} []',
                'forw mte MtsConfigTraffic 0 4 0 [15 0 0 -1(200)]',
                'forw mte MtsConfigScenario 1{0 0 1{0 0} []} [] [0] [0]',
                'forw mte Activate -1',
                ]
    for line in script:
        gv.logger.info(line)
    return script

def get_volte_cap_script(bts):
    from pet_bts import pet_bts_read_scf_file
    pet_bts_read_scf_file(gv.master_bts.bts_id, gv.master_bts.scf_filename)
    script = []
    tm1, tm2 = 2, 2
    if bts.tm in ['4X2']:
        tm1 = 4
    if bts.tm in ['1']:
        tm1, tm2 = 1, 1
    bandlist = bts.band.upper().replace('M', '').split('-')
    gv.case.curr_case.real_ue_count = int(gv.case.curr_case.ue_count)
    bandlist = bts.band.upper().replace('M', '').split('-')
    gv.logger.info(bandlist)
    if str(bts.bandname) in ['41']:
        script += ['forw mte RrcAptOverrideBandSupport 1{41 [1 24960 39650 1940 24960 39650 1940] }',
                    'forw mte Activate -1']
    if bts.ca_type.strip() == '2CC' and bts.domain.strip().upper() == 'VOLTE':
        script += ['forw mte SetMueRadioContextCell 0 %s %s %s [%s] [%s %s] [%s] [%s]' %(
                            bts.phycellid_list[0], bts.dl_frequency_pcell, bandlist[0],
                            tm1, bts.uldl, bts.ssf, tm2, bts.dl_frequency_pcell)]
        script += ['forw mte SetMueRadioContextCell 1 %s %s %s [%s] [%s %s] [%s] [%s]' %(
                            bts.phycellid_list[1], bts.dl_frequency_scell, bandlist[1],
                            tm1, bts.uldl, bts.ssf, tm2, bts.dl_frequency_scell)]
    else:
        script += ['forw mte SetMueRadioContextCell 0 %s %s %s [%s] [%s %s] [%s]' %(
                            bts.phycellid_list[0], bts.dl_frequency_pcell, bandlist[0],
                            tm1, bts.uldl, bts.ssf, tm2)]
    script += [ 'forw mte DeConfigRdaStartTestCase 0 %s [%s] [%s]' %(gv.tm500.shenick_hostname,
                            gv.tm500.shenick_partition, gv.tm500.shenick_volte_group_name),
                'WAIT FOR "I: CMPI DTE RDA TEST GROUP STARTED IND:"',]
    script += [ 'FORW L1 Msg4BypassContentionResolution 1',
                'SETP RRC_TEST_DISABLE_CONNECTED_MEAS_PROCESSING 0',
                'SETP NAS_ENABLE_INDICATIONS_IN_MTS_MODE 1',
                'SETP RRC_PUCCH_CLOSE_LOOP_POWER_CONTROL 0',
                'SETP NAS_DISABLE_REPLAY_PROTECTION 1',
                'forw mte PhyConfigUlPowerOffset 1{-1 80 100 [100] []}',
                'forw mte MtsClearMts',]
    value = '4' if '4X2' in bts.tm else '2'
    value = '1' if bts.tm in  ['1', '1-1'] else value
    script += ['SETP RRC_NUM_DL_ANTENNAS %s' %(value),]


    script += [ 'forw mte MtsConfigUeGroup 0 0 1{0-%s}' %(int(gv.case.curr_case.ue_count)-1),
                'forw mte SetUEGroupContext 0',
                'forw mte UsimConfig 1([%s+1 2] [] [] [] []) [] [] [00112233445566778899AABBCCDDEEFF] [01020304050607080910111213141516 00000000000000000000000000000000 00000000000000000000000000000001 00000000000000000000000000000002 00000000000000000000000000000004 00000000000000000000000000000008 64 0 32 64 96]' %(bts.start_ue_imsi),]

    if gv.case.curr_case.ul_sps:
        script += [ 'forw mte SetUEGroupContext 0',
                    'forw mte RrcAptConfigUeCap [[] [] [] [] [] [] [1{0 C9BFF4429542684088220BFF068C4F0014C0FC404181E5000019400072800040F280000D00007A00000650003D00000340000E8000081E600001A0001811044110441104404FFC800005FAC00801021080}]] [2]',
                    ]
    else:
        script += [ 'forw mte SetUEGroupContext 0',
                    'forw mte RrcAptConfigUeCap [[] [] [] [] [] [] [1{0 C23FF441953010381DF834626800A017E45E000000003BDF800000}]]',
                    ]

    if int(gv.case.curr_case.load_ue_count):
        sue = _add_usim(bts.start_ue_imsi, int(gv.case.curr_case.ue_count))
        script += [ 'forw mte MtsConfigUeGroup 9 0 1{400-%s}' %(400 + int(gv.case.curr_case.load_ue_count)-1),
                    'forw mte SetUEGroupContext 9',
                    'forw mte UsimConfig 1([%s+1 2] [] [] [] []) [] [] [00112233445566778899AABBCCDDEEFF] [01020304050607080910111213141516 00000000000000000000000000000000 00000000000000000000000000000001 00000000000000000000000000000002 00000000000000000000000000000004 00000000000000000000000000000008 64 0 32 64 96]' %(sue),]

    script += [ 'forw mte PhyConfigSysCap 2 4 4',
                'forw mte RrcAptConfigCapability',
                'forw mte NasAptConfigCapability [] [224] [224]',
                'forw mte RrcAptConfigCellSelection %s [%s]' %(bts.dl_frequency_pcell, bts.phycellid_list[0]),
                'forw mte NasAptConfigPlmnSelection 26203',

                'forw mte MtsConfigUeGroup 1 2 1{0-%d}' %(int(gv.case.curr_case.ue_count)-1),
                'forw mte MtsConfigTrafficProfile 0 2{internet.nsn.com 0{} [] [],srvcc.nsn.com 1{0(cvoip -1) 1 [0 0 1]} [] []} []',
                # 'forw mte MtsConfigTrafficProfile 0 2{internet.nsn.com 2{0(cftp_get -1 ) 0 [0 0 1],0(cftp_put -1 ) 0 [0 0 1]} [] [] [],srvcc.nsn.com 0{} [] [] [] } []',
                'forw mte MtsConfigTraffic 0 1 0 [30 0 10 -1(200)] [] [0]',
                ]

    if int(gv.case.curr_case.load_ue_count):
        script += [
                    'forw mte MtsConfigUeGroup 2 2 1{400-%d}'%(400 + int(gv.case.curr_case.load_ue_count)-1),
                    # 'forw mte MtsConfigTrafficProfile 1 2{internet.nsn.com 2{0(DL_UDP_lp0 -1) 0 [0 0 1],0(UL_UDP -1) 0 [0 0 1]} [] [],srvcc.nsn.com 0{} [] []} []',
                    'forw mte MtsConfigTrafficProfile 1 2{internet.nsn.com 2{0(cftp_get -1 ) 0 [0 0 1],0(cftp_put -1 ) 0 [0 0 1]} [] [] [],srvcc.nsn.com 0{} [] [] [] } []',
                    'forw mte MtsConfigTraffic 1 2 1 [0 0 0 -1(100)]',
                    'forw mte MtsConfigScenario 1{0 0 2{0 0,1 0} []} [] [0] [0]',
                    'forw mte Activate -1',
                ]
    else:
        script += ['forw mte MtsConfigScenario 1{0 0 1{0 0} []}',
                   'forw mte Activate -1',                              ]

    for line in script:
        gv.logger.info(line)
    return script

def get_volte_performance_script(bts):
    case = gv.case.curr_case
    from pet_tm500_script_builder import c_tm500_script_builder
    from pet_bts import pet_bts_read_scf_file
    pet_bts_read_scf_file(gv.master_bts.bts_id, gv.master_bts.scf_filename)
    builder = c_tm500_script_builder(bts)
    builder.config_rf_card(0, bts, bts.phycellid_list[0], bts.frequency_list[0], builder.bandlist[0])
    builder.config_shenick()
    builder.config_raw('SETP L2_MAC_ENABLE_CR379_R2_094167 1')
    builder.config_raw('SETP L2_MAC_ENABLE_REL_9_CR409 1')
    builder.config_raw('SETP RRC_ENABLE_RELEASE_11 1')
    builder.config_raw('SETP NAS_ENABLE_R10 1')
    builder.config_raw('SETP NAS_ENABLE_INDICATIONS_IN_MTS_MODE 1')
    builder.config_raw('FORW L1 Msg4BypassContentionResolution 1')
    builder.config_ul_offset(75, 75, 75)
    if case.volte_rf_condition.upper() in ['AVERAGE', 'BAD']:
        builder.config_raw('forw mte PhyConfigUlInterference -27 [] [0]')
    if case.is_mix:
        groupid = builder.config_ue_group(0, 0, 110, bts.volte_imsi, '')
    else:
        groupid = builder.config_ue_group(0, 0, case.ue_count, bts.volte_imsi, '')
    builder.config_phy_cap()
    builder.config_nas_plmn()
    builder.config_execute_script()
    position_def = [builder.set_enb_position_entity(id = 0, x = 0,
                                         cell_range = 5000,
                                         cell_id = bts.phycellid_list[0],
                                         ref_signal_power = 10,
                                         sector_off = 3,
                                         dl_frequency = bts.frequency_list[0])]

    # builder.config_enb_position(position_def)
    builder.config_raw('forw mte MtsConfigEnb 1{0 0 0 1{43 26050 5000 [] [10] [] [9000]}}')
    path_paging         = builder.config_path({'1':(gv.case.curr_case.ue_position,'0')})
    builder.config_mobility(ioc='105', fading='3')
    apn1 = builder.build_a_apn('internet.nsn.com', [])
    apn2 = builder.build_a_apn('srvcc.nsn.com', [builder.set_service(application='cvoip', bear_alloc='1', service_delay =120,
                          service_duration = 180)])
    apn3 = builder.build_a_apn('srvcc.nsn.com', [builder.set_service2(application='cvoip', bear_alloc='1')])

    if case.is_mix:
        group1 = builder.config_ue_group3(2, 10, 100)
        group2 = builder.config_ue_group3(2, 0,  case.ue_count)
        traffic_profile1 = builder.config_traffic_profile2(2, [apn1, apn3])
        traffic_profile2 = builder.config_traffic_profile2(2, [apn1, apn3])
        builder.config_uegroup_traffic_profile(groupid = group1, attach_duration=case.case_duration,
                        traffic_profile_id = traffic_profile1, stagger_timer = '100', time_distribution = '-1')
        builder.config_uegroup_traffic_profile(groupid = group2, attach_duration=case.case_duration,
                        traffic_profile_id = traffic_profile2, stagger_timer = '100', time_distribution = '-1')
        builder.config_mts_scenario(int(gv.case.curr_case.case_duration))
    else:
        traffic_profile = builder.config_traffic_profile2(2, [apn1, apn2])
        builder.config_uegroup_traffic_profile(groupid = '0',
                        traffic_profile_id = traffic_profile, stagger_timer = '40', time_distribution = '-1')
        builder.config_mts_scenario(259200)
    builder.config_execute_script()
    return builder.script


def _get_volte_cap_script(bts):
    from pet_tm500_script_builder import c_tm500_script_builder
    from pet_bts import pet_bts_read_scf_file
    pet_bts_read_scf_file(gv.master_bts.bts_id, gv.master_bts.scf_filename)
    case = gv.case.curr_case
    builder = c_tm500_script_builder(bts)
    builder.config_shenick()
    builder.clear_scenarios()
    builder.env_config_for_mts()
    # builder.config_env_value('L2_MAC_ENABLE_CR379_R2_094167',   '1')
    # builder.config_env_value('L2_MAC_ENABLE_REL_9_CR409',       '1')
    # builder.config_env_value('RRC_ENABLE_RELEASE_10',       '1')
    # builder.config_env_value('NAS_ENABLE_R10',       '1')
    # builder.config_env_value('NAS_ENABLE_INDICATIONS_IN_MTS_MODE',       '1')
    # builder.config_raw('FORW L1 Msg4BypassContentionResolution 1')
    builder.config_rf_card(0, bts, bts.phycellid_list[0], bts.frequency_list[0], builder.bandlist[0])

    builder.config_ul_offset(80, 100, 100)

    g0 = builder.config_ue_group2(0, 0, gv.case.curr_case.total_ue_count, bts.volte_imsi, '')
    builder.config_phy_cap()
    builder.config_nas_plmn()
    builder.config_execute_script()

    # position_def = [builder.set_enb_position_entity(id = 0, x = 0, sector_off=3,
    #                                      cell_id = bts.phycellid_list[bts.workcell-1],
    #                                      dl_frequency = bts.frequency_list[bts.workcell-1])]
    # builder.config_enb_position(position_def)

    builder.config_raw('forw mte MtsConfigEnb 1{0 0 0 1{%s %s 5000 [] [10] [] [9000]}}' %(
        bts.phycellid_list[bts.workcell-1], bts.frequency_list[bts.workcell-1]))

    path_volte          = builder.config_path({'1':(gv.case.curr_case.ue_position,'0')})
    builder.config_mobility(groupid = g0, ioc = case.ioc, fading=3)

    apn1 = builder.build_a_apn('internet.nsn.com', [])
    apn2 = builder.build_a_apn('srvcc.nsn.com', [builder.set_service(application='cvoip', bear_alloc='1', service_repeat='0')])
    apn3 = builder.build_a_apn('internet.nsn.com', [builder.set_service(application='cftp_get', service_repeat = '0'),
                                                    builder.set_service(application='cftp_put', service_repeat = '0')])

    traffic_profile1 = builder.config_traffic_profile2(2, [apn1, apn2])
    traffic_profile2 = builder.config_traffic_profile2(1, [apn3])

    g1 = builder.config_ue_group3(2, 10, case.ue_count)
    builder.config_uegroup_traffic_profile(groupid = g1, attach_start_delay = '10',
                    traffic_profile_id = traffic_profile1, stagger_timer = '200', time_distribution = '-1')

    g2 = builder.config_ue_group3(2, 0, case.load_ue_count)
    builder.config_uegroup_traffic_profile(groupid = g2, attach_start_delay = '10',
                    traffic_profile_id = traffic_profile2, stagger_timer = '200', time_distribution = '-1')


    builder.config_mts_scenario(int(gv.case.curr_case.case_duration))
    builder.config_execute_script()
    return builder.script

def get_3cc_attach_script_for_tput(bts):
    script = [
            'SETP L2_MAC_ENABLE_CR379_R2_094167 1',
            'SETP L2_MAC_ENABLE_REL_9_CR409 1',
            'SETP RRC_ENABLE_RELEASE_12 1',
            'SETP NAS_ENABLE_R10 1',
            'forw mte RrcAptOverrideBandSupport 3{41 [1 24960 39650 1940 24960 39650 1940],41 [1 24960 39650 1940 24960 39650 1940],41 [1 24960 39650 1940 24960 39650 1940] }',
            'forw mte Activate -1',
            'WAIT FOR "ACTIVATE"',
        ]
    tm1, tm2 = 2, 2
    if bts.tm.strip().upper() in ['4X2','4X2-4X2','4X2-4X2-4X2']:
        tm1 = 4
    if bts.tm.strip().upper() in ['1', '1-1', '1-1-1']:
        tm1, tm2 = 1, 1
    bandlist = bts.band.upper().replace('M', '').split('-')
    script += ['forw mte SetMueRadioContextCell 0 %s %s %s [%s] [%s %s] [%s]' %(
                        bts.phycellid_list[0], bts.dl_frequency_pcell, bandlist[0],
                        tm1, bts.uldl, bts.ssf, tm2)]
    script += ['forw mte SetMueRadioContextCell 1 %s %s %s [%s] [%s %s] [%s]' %(
                        bts.phycellid_list[1], bts.dl_frequency_scell, bandlist[1],
                        tm1, bts.uldl, bts.ssf, tm2)]
    script += ['forw mte SetMueRadioContextCell 2 %s %s %s [%s] [%s %s] [%s]' %(
                        bts.phycellid_list[2], bts.dl_frequency_tcell, bandlist[2],
                        tm1, bts.uldl, bts.ssf, tm2)]

    value = '4' if bts.tm.strip().upper() in ['4X2','4X2-4X2','4X2-4X2-4X2'] else '2'
    value = '1' if bts.tm.strip().upper() in ['1', '1-1', '1-1-1'] else value
    script += ['SETP RRC_NUM_DL_ANTENNAS %s' %(value),]
    script += ['forw mte PhyConfigUlPowerOffset 1{-1 70 70 [70] []}',
               'forw mte MtsConfigUeGroup 0 0 1{0}',
              ]
    # if bts.ca_type.strip() == '3CC':
    #     band = bts.band.strip().replace('M','')
    #     if band == '20-20-20':
    #         script += [ 'forw mte RrcAptConfigUeCap [[] [] [] [] [] [] [1{0 CDBFF001194010381FF8346278008607E204120F400000D00003A000020BA000006800340001E800001A0040F400004D00003A0000303A0040203A0040307A00400680103D0020134000481C0E070381C0E020202027FF400002C84004}]] [3]',
    #                     'forw mte Activate -1 [] [1]']
    #     else:
    #         script += [ 'forw mte RrcAptConfigUeCap [[] [] [] [] [] [] [1{0 CE3FF041034410381DF834620000A006830103A0000303A0000214801080}]] [3]',
    #                     'forw mte Activate -1 [] [1]']


    script += [     'forw mte UsimConfig ' + _get_usim_str_single(bts.start_ue_imsi)]
    script += [     'forw mte PhyConfigSysCap 2 15 13',]
    script += [     'forw mte RrcAptConfigCellSelection %s [%s]' %(bts.dl_frequency_pcell,bts.phycellid_list[0]),
                    'forw mte NasAptConfigPlmnSelection 26203',
                    'forw mte NasAptConfigCapability [] [224] [224]',
                    'forw mte Activate -1',
                    'forw mte NasConfigEmmRegister 0(0 [0] [] [] [] [] [] [] [])',
                    'forw mte Activate -1',]
    return script


def get_ulca_attach_script_for_tput(bts):
    script = [
            'SETP L2_MAC_ENABLE_CR379_R2_094167 1',
            'SETP L2_MAC_ENABLE_REL_9_CR409 1',
            'SETP RRC_ENABLE_RELEASE_12 1',
            'SETP NAS_ENABLE_R10 1',
        ]
    case = gv.case.curr_case
    tm1, tm2 = 2, 2
    if bts.tm.strip().upper() in ['4X2','4X2-4X2','4X2-4X2-4X2']:
        tm1 = 4
    if bts.tm.strip().upper() in ['1', '1-1', '1-1-1']:
        tm1, tm2 = 1, 1
    bandlist = bts.band.upper().replace('M', '').split('-')
    script += ['forw mte SetMueRadioContextCell 0 %s %s %s [%s] [%s %s] [%s] [] [%s]' %(
                        bts.phycellid_list[0], bts.dl_frequency_pcell, bandlist[0],
                        tm1, bts.uldl, bts.ssf, tm2, bandlist[0])]
    script += ['forw mte SetMueRadioContextCell 1 %s %s %s [%s] [%s %s] [%s] [] [%s]' %(
                        bts.phycellid_list[1], bts.dl_frequency_scell, bandlist[1],
                        tm1, bts.uldl, bts.ssf, tm2, bandlist[1])]

    value = '4' if bts.tm.strip().upper() in ['4X2','4X2-4X2','4X2-4X2-4X2'] else '2'
    value = '1' if bts.tm.strip().upper() in ['1', '1-1', '1-1-1'] else value
    script += ['SETP RRC_NUM_DL_ANTENNAS %s' %(value),]
    script += ['forw mte PhyConfigUlPowerOffset 1{-1 70 70 [70] []}',
               'forw mte MtsConfigUeGroup 0 0 1{0}',
              ]

    if case.ulca and case.ue_cap:
        script += ['forw mte RrcAptConfigUeCap [[] [] [] [] [] [] [1{0 %s}]] [2]' %(gv.case.curr_case.ue_cap) ,
                   'forw mte Activate -1']
    # elif case.ulca:
    #     script += [ 'forw mte RrcAptConfigUeCap [[] [] [] [] [] [] [1{0 CA3FF041034410381DF834620000A006810603A0040303A0040207A00402680003D00200340080E80000C1E800009A0000F400000D0020}]] [2]',
    #                 'forw mte Activate -1']

    script += [     'forw mte UsimConfig ' + _get_usim_str_single(bts.start_ue_imsi)]
    value = '13' if case.cat5 else '4'
    script += [     'forw mte PhyConfigSysCap 2 15 %s' %(value),]
    script += [     'forw mte RrcAptConfigCellSelection %s [%s]' %(bts.dl_frequency_pcell, bts.phycellid_list[0]),
                    'forw mte NasAptConfigPlmnSelection 26203',
                    'forw mte NasAptConfigCapability [] [224] [224] [] [] [3]',
                    'forw mte Activate -1',
                    'forw mte NasConfigEmmRegister 0(0 [0] [] [] [] [] [] [] [])',
                    'forw mte Activate -1',]
    return script


def get_tput_mue_attach_script(bts):
    from pet_tm500_script_builder import c_tm500_script_builder
    if gv.case.curr_case.case_type in ['CPK_MUE_DL_COMBIN']:
        return get_tput_mue_attach_script_combin(bts)
    builder = c_tm500_script_builder(bts)
    builder.config_rf_card(0, bts, bts.phycellid_list[0], bts.frequency_list[0], builder.bandlist[0])
    if gv.case.curr_case.ca_type.strip() == '2CC':
        builder.config_rf_card(1, None, bts.phycellid_list[1], bts.frequency_list[1], builder.bandlist[1])

    builder.env_config_for_mts()
    gv.tm500.shenick_volte_group_name = 'TA_GROUP'
    builder.config_shenick()

    groupid = builder.config_ue_group(0, 0, gv.case.curr_case.ue_count, bts.volte_imsi, '')
    builder.config_phy_cap()
    if gv.case.curr_case.ue_cap:
       builder.config_ue_cap(gv.case.curr_case.ue_cap)
    else:
        builder.config_raw('forw mte RrcAptConfigCapability')
    builder.config_raw('forw mte NasAptConfigCapability')
    if gv.case.curr_case.ca_type.strip() == '2CC':
        builder.config_raw('forw mte RrcAptConfigCellSelection %s [%s]' %(bts.frequency_list[0], bts.phycellid_list[0]))

    builder.config_nas_plmn()

    position_def = [builder.set_enb_position_entity(id = 0, x = 0,
                                             cell_id = bts.phycellid_list[0],
                                             dl_frequency = bts.frequency_list[0])]


    builder.config_enb_position(position_def)

    builder.config_ul_offset(83, 83, 83)
    wpx =  '1' if gv.case.curr_case.wpx else '0'
    if gv.case.curr_case.sinr:
        path = builder.config_path({'1':(gv.case.curr_case.ue_position,'0')})
        builder.config_mobility(groupid=groupid,pathid=path, ioc=gv.case.curr_case.ioc,fading=3)
    else:
        path = builder.config_path({'1':(wpx,'0')})
        builder.config_mobility(groupid=groupid,pathid=path, ioc=105,fading=3)

    app = 'cftp_get' if gv.case.curr_case.case_type == 'THROUGHPUT_MUE_DL' else 'cftp_put'
    if 'unidirection' in gv.case.curr_case.case_name and 'UL_DL' in gv.case.curr_case.case_name:
        traffic_profile1 = builder.config_traffic_profile(servicelist = [builder.set_service(application=app),
            builder.set_service(application='cftp_get')], apn='')
    else:
        traffic_profile1 = builder.config_traffic_profile(servicelist = [builder.set_service(application=app)],
            apn='')
    builder.config_uegroup_traffic_profile(groupid=groupid,
        traffic_profile_id=traffic_profile1, stagger_timer=1000, time_distribution=-1)
    builder.config_mts_scenario(int(gv.case.curr_case.case_duration) + 1000)
    builder.config_execute_script()
    gv.shenick_groups = []
    #add_shenick_group(app[1:], 0, gv.case.curr_case.ue_count)
    return builder.script

def get_tput_mue_attach_script_combin(bts):
    case = gv.case.curr_case
    script = [      'SETP L2_MAC_ENABLE_CR379_R2_094167 1',
                    'SETP L2_MAC_ENABLE_REL_9_CR409 1',
                    'SETP RRC_ENABLE_RELEASE_11 1',
                    'SETP NAS_ENABLE_R10 1',
                    'SETP L2_MAC_DISABLE_SR_INIT_RACH_IF_SR_NOT_CFG 1',]
    if str(bts.bandname) in ['41']:
        script += ['forw mte RrcAptOverrideBandSupport 2{41 [1 24960 39650 1940 24960 39650 1940] [],41 [1 24960 39650 1940 24960 39650 1940] []} [0]',
                   'forw mte Activate -1 [] [1]']
    if bts.btstype == 'TDD' and case.ca_type.strip() == '2CC':
        script += ['forw l1 MapFreqToRadioContext 0 1 %d %d' %(int(bts.dl_frequency_pcell)-100, int(bts.dl_frequency_pcell)+100),
                   'forw l1 MapFreqToRadioContext 1 1 %d %d' %(int(bts.dl_frequency_scell)-100, int(bts.dl_frequency_scell)+100),]
    else:
        if bts.btstype == 'TDD':
            script += ['forw mte PhyConfigUlTiming 0',]


    tm1 = 4 if case.tm in ['4X2'] else 2
    tm2 = 1 if case.tm in ['1'] else 2
    bandlist = case.band.upper().replace('M', '').split('-')
    ms_bandlist = case.ms_band.upper().replace('M', '').split('-')


    if bts.btstype == 'FDD' and case.ca_type in ['2CC']:
        script += ['forw mte SetMueRadioContextCell 0 %s %s %s [%s] [] [%s]' %(
                        bts.phycellid_list[0], bts.dl_frequency_pcell, bandlist[1],
                        tm1, tm2)]
        script += ['forw mte SetMueRadioContextCell 1 %s %s %s [%s] [] [%s]' %(
                            bts.phycellid_list[1], bts.dl_frequency_scell, bandlist[0],
                            tm1, tm2)]
    if gv.ms_bts:
        tm1 = 4 if case.ms_tm in ['4X2', '4X2-4X2'] else 2
        tm2 = 1 if case.ms_tm in ['1'] else 2

        if gv.ms_bts.btstype =='TDD' and case.ca_type in ['2CC']:
            script += ['forw mte SetMueRadioContextCell 2 %s %s %s [%s] [%s %s] [%s]' %(
                            gv.ms_bts.phycellid_list[0], gv.ms_bts.dl_frequency_pcell, ms_bandlist[0],
                            tm1, case.ms_uldl, case.ms_ssf, tm2)]
            script += ['forw mte SetMueRadioContextCell 3 %s %s %s [%s] [%s %s] [%s]' %(
                            gv.ms_bts.phycellid_list[1], gv.ms_bts.dl_frequency_scell, ms_bandlist[1],
                            tm1, case.ms_uldl, case.ms_ssf, tm2)]

    if bts.btstype == 'FDD' and case.ca_type in ['2CC']:
        script += ['forw mte PhyConfigUlPowerOffset 1{-1 85 80 [80] []}']
        script += ['forw mte MtsConfigUeGroup 0 0 1{0}']
    if (case.ca_type == '2CC' and case.tm =='4X4-4X4') or (bts.btstype == 'FDD' and case.ca_type in ['2CC']):
        gv.tm500.shenick_volte_group_name = 'MUE_UDP'
        script += [ 'forw mte DeConfigRdaStartTestCase 0 %s [%s] [%s]' %(gv.tm500.shenick_hostname,
                            gv.tm500.shenick_partition, gv.tm500.shenick_volte_group_name)]
        script += ['WAIT FOR "I: CMPI DTE RDA TEST GROUP STARTED IND:"']
    if bts.btstype == 'TDD':
        script += ['forw mte PhySetTDDCfg %s %s' %(case.uldl, case.ssf)]

    value = '4' if case.tm in ['4X2', '4X4', '94X4', '4X2-4X2', '4X4-4X4'] else '2'
    value = '1' if case.tm in  ['1', '1-1'] else value
    value = '4' if bts.btstype == 'FDD' and case.ca_type in ['2CC'] else value
    script += ['SETP RRC_NUM_DL_ANTENNAS %s' %(value),]

    value = '2 6 6' if case.ca_type.strip() else '2 4 4'
    value = '2 4 5' if case.cat5 else value
    value = '4 5 5' if case.tm in ['4X4', '94X4', '98X4'] else value
    value = '4 16 5' if case.tm in ['4X4-4X4'] else value
    value = '2 15 4' if bts.btstype == 'FDD' and case.ca_type in ['2CC'] else value

    if case.ue_cap:
        script += ['forw mte RrcAptConfigUeCap [[] [] [] [] [] [] [1{0 %s}]] [4]' %(gv.case.curr_case.ue_cap) ,
                   'forw mte Activate -1']

    script += [     'forw mte PhyConfigSysCap %s' %(value),]
    script += [     'forw mte UsimConfig ' + _get_usim_str_single(bts.start_ue_imsi)]
    script += [     'forw mte NasConfigEmmRegister 0(0 [0] [] [] [] [] [] [] [])',
                    'forw mte NasAptConfigPlmnSelection 26203',
                    'forw mte NasAptConfigCapability',
                    'forw mte RrcAptConfigCapability',                    ]

    # script += [     'forw mte MtsConfigUeGroup 1 2 1{0-0}',
    #                 'forw mte MtsConfigTrafficProfile 0 1{"" 1{0(DL_UDP_lp0 -1) 0 [0 0 1]} [] [] []} []',
    #                 'forw mte MtsConfigTraffic 0 0 0 [0 0 0 -1(1000)]',
    #                 'forw mte MtsConfigScenario 1{3605 0 1{0 0} []} [] [0] [0] [] [0]',   ]


    script += [     'forw mte RrcAptConfigCellSelection %s' %(bts.dl_frequency_pcell),
                    'forw mte Activate -1',]
    return script

def get_mr_mix_script(bts = None, sbts = None):
    def _get_case_attr(attrname):
        if str(getattr(gv.case.curr_case, attrname)).strip():
            return int(getattr(gv.case.curr_case, attrname))
        return 0

    def splitgroup(uecount=0, numbers=10):
        uelist = []
        uelist = [numbers]*int(uecount/numbers)
        if uecount > len(uelist)*numbers:
            uelist.append(uecount - len(uelist)*numbers)
        return uelist


    from pet_tm500_script_builder import c_tm500_script_builder

    def _config_a_group(builder             = None,
                        ue_count            = 0,
                        traffic_profile     = None,
                        attach_duration     = 0,
                        deattach_duration   = 0,
                        time_distribution   = -1,
                        stagger             = 25,
                        increase_delay      = 5,
                        mobility_path       = 0,
                        pathend             = 0,
                        position_distribution = 0,
                        speed               = 0,
                        speed_distribution  = 0,
                        ioc                 = 140,
                        fading              = 0):
        if ue_count:
            aptstring = ''
            if gv.case.curr_case.customer.upper() == 'SPRINT':
                aptstring = '[[] [] [] [] [] [] [1{0 C9A0044395327500C180300600C1F834621000A0142021000000}]] [2]'
            groupid = builder.config_ue_group(0, builder.startue, ue_count, builder.startusim, aptstring)
            builder.config_uegroup_traffic_profile(groupid, traffic_profile, builder.start_delay,
                attach_duration, deattach_duration, time_distribution, int(stagger))
            builder.startue  += ue_count
            builder.start_delay += increase_delay
            builder.startusim = _add_usim(builder.startusim, ue_count)
            builder.config_mobility(groupid, mobility_path, pathend, position_distribution,
                                    speed, speed_distribution, ioc, fading)

    case = gv.case.curr_case
    paging_count                = _get_case_attr('mr_paging_ue_count')
    paging_impair_count         = _get_case_attr('mr_paging_impair_ue_count')
    cd_count                    = _get_case_attr('mr_call_drop_ue_count')
    cd_impair_count             = _get_case_attr('mr_cd_impair_ue_count')
    ho_count                    = _get_case_attr('mr_intra_ho_ue_count')
    ho_impair_count             = _get_case_attr('mr_ho_impair_ue_count')
    volte_count                 = _get_case_attr('mr_volte_ue_count')
    volte_impair_count          = _get_case_attr('mr_volte_impair_ue_count')
    volte_ho_count              = _get_case_attr('mr_volte_ho_ue_count')
    volte_ho_impair_count       = _get_case_attr('mr_volte_ho_impair_ue_count')

    gv.kpi.kpi_cap = 10000
    if case.real_paging_ue_count:
        gv.kpi.kpi_cap = min(gv.kpi.kpi_cap, int(1000/int(case.paging_stagger)))
    if case.real_cd_ue_count:
        gv.kpi.kpi_cap = min(gv.kpi.kpi_cap, int(1000/int(case.cd_stagger)))
    if case.real_ho_ue_count:
        gv.kpi.kpi_cap = min(gv.kpi.kpi_cap, int(1000/int(case.ho_stagger)))
    if case.real_volte_ue_count:
        gv.kpi.kpi_cap = min(gv.kpi.kpi_cap, int(1000/int(case.mr_volte_stagger)))
    if case.real_ho_volte:
        gv.kpi.kpi_cap = min(gv.kpi.kpi_cap, int(1000/int(case.mr_volte_ho_stagger)))

    if case_attr('tm500_attach_file'):
        return open(bts_source_file(bts.bts_id, case_attr('tm500_attach_file')), 'r').readlines()

    builder = c_tm500_script_builder(bts, sbts)
    builder.startusim = bts.start_ue_imsi

    builder.env_config_for_mts()

    #Config RF Card for TM500 first & bts position,
    builder.config_rf_card(0, bts, bts.phycellid_list[0], bts.frequency_list[0], builder.bandlist[0])
    if gv.case.curr_case.ca_type == '2CC':
        builder.config_rf_card(1, bts, bts.phycellid_list[1], bts.frequency_list[1], builder.bandlist[1])
    position_def = [builder.set_enb_position_entity(id = 0, x = -500,
                                         cell_id = bts.phycellid_list[bts.workcell-1],
                                         dl_frequency = bts.frequency_list[bts.workcell-1])]

    if gv.case.curr_case.real_ho_ue_count + gv.case.curr_case.real_ho_volte >0 :
        if case.is_inter:
            dst_bts = gv.slave_bts
            dworkcell = dst_bts.workcell
        else:
            dst_bts = gv.master_bts
            dworkcell = 3 if case.ca_type == '2CC' else 2
            dworkcell = 4 if case.ca_type == '3CC' else dworkcell

        cell_id     = dst_bts.phycellid_list[dworkcell-1]
        frequency   = dst_bts.frequency_list[dworkcell-1]
        builder.config_rf_card(1, None, cell_id, frequency, builder.bandlist[0])
        position_def += [builder.set_enb_position_entity(id = 1, x = 500,
                                             cell_id = cell_id, dl_frequency = frequency)]

    builder.config_shenick()
    builder.clear_scenarios()

    ul_offset = int(bts.ul_power_offset) if has_attr(bts, 'ul_power_offset') else 66
    builder.config_ul_offset(ul_offset, ul_offset, ul_offset)

    builder.config_phy_cap()
    builder.config_nas_plmn()

    builder.config_enb_position(position_def)

    path_paging         = builder.config_path({'1':('-1100','0')})
    path_paging_impair  = builder.config_path({'1':('-1080','0')})
    path_cd             = builder.config_path({'1':('-1100','0')})
    path_cd_impair      = builder.config_path({'1':('-1080','0')})
    path_ho             = builder.config_path({'1':('-300','0'), '2':('300', '0')})
    path_ho_impair      = builder.config_path({'1':('-300','0'), '2':('300', '0')})
    path_volte          = builder.config_path({'1':('-500','0'), '2':('500', '0')})
    path_volte_impair   = builder.config_path({'1':('-500','0'), '2':('500', '0')})

    impair_fadding = '6(1 [0] [0])' if case.epa5 else '0'
    impair_pathend = '0'            if case.epa5 else '0'

    traffic_profile1 = builder.config_traffic_profile(servicelist = [builder.set_service(application='DL_UDP_lp0')])
    traffic_profile2 = builder.config_traffic_profile(servicelist = [builder.set_service(application='DL_UDP_lp0'),
                                                                     builder.set_service(application='cftp_get'),
                                                                     builder.set_service(application='cftp_put')])

    apn1 = builder.build_a_apn('internet.nsn.com', [builder.set_service(application='cftp_get'),
                                                    builder.set_service(application='cftp_put')])
    apn2 = builder.build_a_apn('srvcc.nsn.com', [builder.set_service(application='cvoip', bear_alloc='1', service_delay =60,
                          service_duration = 120)])
    apn3 = builder.build_a_apn('srvcc.nsn.com', [builder.set_service(application='cvoip', bear_alloc='1')])

    traffic_profile3 = builder.config_traffic_profile2(2, [apn1, apn2])
    traffic_profile_volte_ho = builder.config_traffic_profile2(2, [apn1, apn3])

    if paging_count:
        uelist = splitgroup(paging_count, 10)
        for ues in uelist:
            _config_a_group(builder             = builder,
                            ue_count            = ues,
                            traffic_profile     = traffic_profile1,
                            stagger             = case.paging_stagger,
                            mobility_path       = 0,
                            pathend             = 0,
                            ioc                 = bts.mr_paging_ioc,
                            fading              = 0)

    if paging_impair_count:
        uelist = splitgroup(paging_impair_count, 10)
        for ues in uelist:
            _config_a_group(builder             = builder,
                            ue_count            = ues,
                            traffic_profile     = traffic_profile1,
                            stagger             = case.paging_stagger,
                            mobility_path       = path_paging_impair,
                            pathend             = impair_pathend,
                            ioc                 = bts.mr_paging_impair_ioc,
                            fading              = impair_fadding)

    if cd_count:
        _config_a_group(builder             = builder,
                        ue_count            = cd_count,
                        traffic_profile     = traffic_profile2,
                        attach_duration     = 20,
                        deattach_duration   = 10,
                        stagger             = case.cd_stagger,
                        mobility_path       = path_paging,
                        pathend             = 0,
                        ioc                 = bts.mr_call_drop_ioc,
                        fading              = 0)
    if cd_impair_count:
        _config_a_group(builder             = builder,
                        ue_count            = cd_impair_count,
                        traffic_profile     = traffic_profile2,
                        attach_duration     = 20,
                        deattach_duration   = 10,
                        stagger             = case.cd_stagger,
                        mobility_path       = path_cd_impair,
                        pathend             = impair_pathend,
                        ioc                 = bts.mr_call_drop_impair_ioc,
                        fading              = impair_fadding)

    if ho_count:
        _config_a_group(builder             = builder,
                        ue_count            = ho_count,
                        traffic_profile     = traffic_profile2,
                        stagger             = case.ho_stagger,
                        mobility_path       = path_ho,
                        pathend             = 1,
                        position_distribution = 2,
                        speed               = 100,
                        speed_distribution  = 3,
                        ioc                 = bts.mr_ho_ioc,
                        fading              = 3)

    if ho_impair_count:
        _config_a_group(builder             = builder,
                        ue_count            = ho_impair_count,
                        traffic_profile     = traffic_profile2,
                        stagger             = case.ho_stagger,
                        mobility_path       = path_ho_impair,
                        pathend             = 1,
                        position_distribution = 2,
                        speed               = 100,
                        speed_distribution  = 3,
                        ioc                 = bts.mr_ho_impair_ioc,
                        fading              = impair_fadding)

    builder.startusim = bts.volte_imsi

    if volte_count:
        groupid = builder.config_ue_group(0, builder.startue, volte_count, builder.startusim, '')
        builder.config_uegroup_traffic_profile(groupid = groupid,
            traffic_profile_id = traffic_profile3, stagger_timer = case.mr_volte_stagger, time_distribution = '-1')
        builder.startue  += volte_count
        builder.startusim = _add_usim(builder.startusim, volte_count)
        builder.config_mobility(groupid=groupid, pathid = path_volte, ioc = bts.mr_volte_ioc)

    if volte_impair_count:
        groupid = builder.config_ue_group(0, builder.startue, volte_impair_count, builder.startusim, '')
        builder.config_uegroup_traffic_profile(groupid = groupid,
            traffic_profile_id = traffic_profile3, stagger_timer = case.mr_volte_stagger, time_distribution = '-1')
        builder.startue  += volte_impair_count
        builder.startusim = _add_usim(builder.startusim, volte_impair_count)
        builder.config_mobility(groupid=groupid, pathid = path_volte, pathend = impair_pathend,
                                 ioc = bts.mr_volte_impair_ioc)

    if volte_ho_count:
        groupid = builder.config_ue_group(0, builder.startue, volte_ho_count, builder.startusim, '')
        builder.config_uegroup_traffic_profile(groupid = groupid,
            traffic_profile_id = traffic_profile_volte_ho, stagger_timer = case.mr_volte_stagger, time_distribution = '-1')
        builder.startue  += volte_ho_count
        builder.startusim = _add_usim(builder.startusim, volte_ho_count)

        builder.config_mobility(groupid, path_volte, 1, 2, 100, 3, bts.mr_volte_ioc, 3) #TOBECONTINUE

    if volte_ho_impair_count:
        groupid = builder.config_ue_group(0, builder.startue, volte_ho_impair_count, builder.startusim, '')
        builder.config_uegroup_traffic_profile(groupid = groupid,
            traffic_profile_id = traffic_profile_volte_ho, stagger_timer = case.mr_volte_stagger, time_distribution = '-1')
        builder.startue  += volte_ho_impair_count
        builder.startusim = _add_usim(builder.startusim, volte_ho_impair_count)
        builder.config_mobility(groupid, path_volte, 1, 2, 100, 3, bts.mr_volte_impair_ioc, 3) #TOBECONTINUE

    builder.config_mts_scenario(int(gv.case.curr_case.case_duration) + 60)
    builder.config_execute_script()

    gv.shenick_groups = []
    all_ue_count = paging_count + paging_impair_count + cd_count + cd_impair_count + ho_count + ho_impair_count
    add_shenick_group('udp_download', 0, int(all_ue_count))
    add_shenick_group('ftp_get', 0, int(all_ue_count))
    return builder.script

def get_tm500_script(bts):
    script = ''
    if case_attr('tm500_attach_file'):
        return open(bts_source_file(bts, case_attr('tm500_attach_file')), 'r').readlines()
    if caseis('domain', 'CPK'):
        if caseis('ca_type', '3CC'):
            return get_3cc_attach_script_for_tput(bts)
        if caseis('ulca'):
            return get_ulca_attach_script_for_tput(bts)
        if case_attr('case_type') in ['THROUGHPUT_MUE_DL', 'THROUGHPUT_MUE_UL']:
            return get_tput_mue_attach_script(bts)
        return get_general_script_for_tput(bts)

def get_mix_cap_script(bts):
    print 'get_mix_cap_script'
    if gv.case.curr_case.shenick_group_name:
        gv.tm500.shenick_group_name = gv.case.curr_case.shenick_group_name
        gv.tm500.shenick_volte_group_name = gv.case.curr_case.shenick_group_name
    print "shenick_group_name = %s ,shenick_volte_group_name = %s" %(gv.tm500.shenick_group_name,gv.tm500.shenick_volte_group_name)
    script = ''
    if case_attr('tm500_attach_file'):
        return open(bts_source_file(bts.bts_id, case_attr('tm500_attach_file')), 'r').readlines()

    ul_offset = int(bts.ul_power_offset) if has_attr(bts, 'ul_power_offset') else 75
    print 'ul_offset=%s' %(ul_offset)

    from pet_tm500_script_builder import c_tm500_script_builder
    from pet_bts import pet_bts_read_scf_file
    pet_bts_read_scf_file(gv.master_bts.bts_id, gv.master_bts.scf_filename)
    builder = c_tm500_script_builder(bts)

    if str(bts.bandname) in ['41']:
        print "get_mix_cap_script band 41 need add override "
        if gv.tm500.card_band_is_narrow_band == 'True':
            builder.config_raw('forw mte RrcAptOverrideBandSupport 1{41 [1 25700 40390 500 25700 40390 500] }')
        else:
            builder.config_raw('forw mte RrcAptOverrideBandSupport 1{41 [1 24960 39650 1940 24960 39650 1940] }')
        builder.config_raw('forw mte Activate -1')

    builder.config_rf_card(0, bts, bts.phycellid_list[0], bts.frequency_list[0], builder.bandlist[0])
    if gv.case.curr_case.ca_type.strip() == '2CC':
        builder.config_rf_card(1, None, bts.phycellid_list[1], bts.frequency_list[1], builder.bandlist[1])
    if gv.case.curr_case.ca_type.strip() == '3CC':
        builder.config_rf_card(1, None, bts.phycellid_list[1], bts.frequency_list[1], builder.bandlist[1])
        builder.config_rf_card(2, None, bts.phycellid_list[2], bts.frequency_list[2], builder.bandlist[2])
    builder.config_raw('SETP RRC_TEST_DISABLE_CONNECTED_MEAS_PROCESSING 0')
    builder.config_raw('SETP DE_RDA_VERBOSITY 5')

    if not gv.env.use_ixia:
        if gv.case.curr_case.has_cap_volte:
            test_group = gv.tm500.shenick_volte_group_name
        else:
            test_group = gv.tm500.shenick_group_name
        print test_group
        builder.config_shenick_group(test_group)
    builder.clear_scenarios()
    builder.env_config_for_mts()

    builder.config_antennas()
    builder.config_phy_cap()
    builder.config_ul_power_offset(ul_offset, ul_offset, ul_offset)
    builder.config_nas_plmn()

    case = gv.case.curr_case
    ueid = 0
    cacap = 'C9BFF043A13A54C0C1F83F07E0FDF834626800A007E020140738082503CE02084D01081E70004067080074000040F400000D00007A00002680003CA0000728000007280004073800040F300000CC0003980002140FC1F83F07E0FC1F83F07E0FC0404FFC000000'
    ncacap = 'C9BFF044033E5CDA2204F84F84F84F84FBF068C4D0014008C0284F84F84F84F84F84F885800000'
    ulcacap = 'C9BFF041A32C10381DF834620000A006828303A0240900F4040103A0001000E50902403CA10040E5000400'
    imsis = {
        'S'         : gv.tm500.prbs_imsi,
        'MA'        :gv.tm500.prbma_imsi,
        'MB'        :gv.tm500.prbmb_imsi,
        'V'         :gv.tm500.volte_imsi,
        'MI'        :'262030020000590',}
    prb_list = []
    for uegroup in case.uegroup_list:
        bts.ue_cap = uegroup.ue_type
        uecapstr = cacap if uegroup.ue_type in ['CA','3CC'] else ncacap
        uecapstr = ulcacap if uegroup.ue_type == 'ULCA' else uecapstr
        groupid = builder.config_ue_group2(0, ueid, uegroup.ue_count, imsis[uegroup.prb], '')
        builder.config_ue_cap(uecapstr)
        builder.config_phy_cap()
        builder.config_cell_section2(bts.frequency_list[int(uegroup.cell_index)],bts.phycellid_list[int(uegroup.cell_index)])
        builder.config_execute_script()
        imsis[uegroup.prb] = _add_usim(imsis[uegroup.prb], uegroup.ue_count)
        ueid += int(uegroup.ue_count)
        #case.ue_count = case.ue_count + int(uegroup.ue_count)
        prb_list += [uegroup.prb]


    print "The case ue total count is %d" %(case.ue_count)
    gv.case.curr_case.real_ue_count = case.ue_count
    #print "The case real ue count is %d" %(gv.case.curr_case.real_ue_count)

    if not gv.case.curr_case.has_cap_volte:
        print "Add ue number kpi"
        gv.case.curr_case.kpi += ';kpi_ue_num:%s' %(case.ue_count)

    service_dict = {
    'ftp_get'       :'cftp_get',
    'ftp_put'       :'cftp_put',
    'voip'          :'cvoip',
    }


    ue_id = 0
    ue_group_type = 0
    ue_group_id = 0

    dst_bts = gv.master_bts
    cell_count = 2 if gv.case.curr_case.ca_type == '2CC' else 1
    cell_count = 3 if gv.case.curr_case.ca_type == '3CC' else cell_count

    position_def = 'forw mte MtsConfigEnb 1{0 0 0 ' + str(cell_count) + '{'
    for i in range(cell_count):
        if i in [1,2]:
            position_def += ','
        cell_id     = dst_bts.phycellid_list[i]
        frequency   = dst_bts.frequency_list[i]
        position_def += set_enb_position_entity2(cell_id = cell_id, dl_frequency = frequency, cell_range=1000, ref_signal_power=10)
    position_def += '}}'

    if gv.case.curr_case.tm == '4X2' and not gv.case.curr_case.has_cap_volte:
        builder.config_raw(position_def)
        builder.define_ue_group2(ue_group_id, 1, ue_id, int(case.ue_count)-1)
        builder.config_raw('forw mte MtsConfigPath 0 1{100 100}')
        builder.config_raw('forw mte MtsConfigMobility 0 0 0 0 0 50 0 -140 [4(1 [0] [0])]')
        ue_group_id += 1

    if gv.env.use_ixia and case.bbpooling == False:
        if case.ue_is_m678:
            builder.define_ue_group2(ue_group_id, ue_group_type, ue_id, int(case.ue_count)-1)
            builder.config_raw('forw mte MtsConfigBearerResources 0 1{[1{0 3 0 [10.68.170.206 255.255.255.255] [17] [1 65535] [1 65535] [] [] []}] [8 [5000 3000] [5000 3000]]}')
            builder.config_raw('forw mte MtsConfigBearerResources 1 1{[1{0 3 0 [10.68.170.205 255.255.255.255] [17] [1 65535] [1 65535] [] [] []}] [6 [5000 3000] [5000 3000]]}')
            # service_list = []
            # service_list1='"QCI8"|"QCI6"'
            # for service in service_list1.split('|'):
            #     app = service_dict[service.replace('"','')] if service.replace('"','') in service_dict.keys() else service
            #     if app.strip():
            #         service_list.append(builder.set_service(application=app, service_delay='60'))
            # apn1 = builder.build_a_apn('""', service_list)
            # profileid = builder.config_traffic_profile2(1, [apn1])
            # builder.config_uegroup_traffic_profile2(groupid = ue_group_id, traffic_profile_id = profileid,attach_duration=72000, deattach_duration=30, stagger_timer=50, time_distribution=-1)
            builder.config_raw('forw mte MtsConfigTrafficProfile 0 1{"" 2{0(QCI8 -1) 2(0) [],0(QCI6 -1) 2(1) []} [] [] []} []')
            builder.config_raw('forw mte MtsConfigTraffic 0 0 0 [0 72000 30 -1(200)]')
            print 'ixia mts config:%s' %case.service_group_list
        else:
            builder.define_ue_group2(ue_group_id, ue_group_type, ue_id, int(case.ue_count)-1)
            service_list = []
            apn1 = builder.build_a_apn('""', service_list)
            profileid = builder.config_traffic_profile2(1, [apn1])
            start_delay = 0
            builder.config_uegroup_traffic_profile2(groupid = ue_group_id, traffic_profile_id = profileid,attach_start_delay = start_delay, attach_duration=72000, deattach_duration=30, stagger_timer=200, time_distribution=-1)
            print 'ixia mts config:%s' %case.service_group_list

    else:
        start_delay = 0
        ue_num = 0
        for service_group in case.service_group_list:
            groupid = builder.define_ue_group2(ue_group_id, ue_group_type, ue_id, int(service_group.ue_count)-1)
            service_list = []
            for service in service_group.service_list1.split('|'):
                app = service_dict[service.replace('"','')] if service.replace('"','') in service_dict.keys() else service
                if app.strip():
                    service_list.append(builder.set_service(application=app, service_delay='200'))
            #apn1 = builder.build_a_apn('internet.nsn.com', service_list)
            apn1 = builder.build_a_apn('""', service_list)
            service_list = []
            if  service_group.service_list2.strip() <> '':
                print 'service_list2 is not null'
                print service_group.service_list2.split('|')
                for service in service_group.service_list2.split('|'):
                    if service.strip():
                        app = service_dict[service.replace('"','')] if service.replace('"','') in service_dict.keys() else service
                        if app.strip():
                            service_list.append(builder.set_service(application=app, service_delay='200'))
                apn2 = builder.build_a_apn('srvcc.nsn.com', service_list)
                print service_list
                profileid = builder.config_traffic_profile2(2, [apn1, apn2])
            else:
                profileid = builder.config_traffic_profile2(1, [apn1])
            if case.bbpooling == True:
                start_delay = 60*ue_group_id
            builder.config_uegroup_traffic_profile2(groupid = ue_group_id, traffic_profile_id = profileid, attach_start_delay = start_delay, attach_duration=72000, deattach_duration=30, stagger_timer=200, time_distribution=-1)
            ue_num = ue_num + int(service_group.ue_count)
            start_delay = start_delay + 200*ue_num/1000
            ue_id += int(service_group.ue_count)
            ue_group_id +=1

    if gv.case.curr_case.ue_is_m678:
        builder.config_mts_scenario2()
    else:
        builder.config_mts_scenario(0)
    builder.config_execute_script()
    return builder.script

