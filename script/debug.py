def get_script_for_combined_ca_of_tput():
    case = gv.case.curr_case
    mp_bts = gv.master_bts
    ms_bts = gv.ms_bts

    script = ['SETP L2_MAC_ENABLE_CR379_R2_094167 1',
              'SETP L2_MAC_ENABLE_REL_9_CR409 1',
              'SETP RRC_ENABLE_RELEASE_11 1',
              'SETP NAS_ENABLE_R10 1',
              'SETP L2_MAC_DISABLE_SR_INIT_RACH_IF_SR_NOT_CFG 1', ]

    if str(bts.bandname) in ['41']:
        script += ['forw mte RrcAptOverrideBandSupport 2{41 [1 24960 39650 1940 24960 39650 1940] [],41 [1 24960 39650 1940 24960 39650 1940] []} [0]',
                   'forw mte Activate -1 [] [1]']

    if bts.btstype == 'TDD' and case.ca_type.strip() == '2CC':
        script += ['forw l1 MapFreqToRadioContext 0 1 %d %d' % (int(bts.dl_frequency_pcell)-100, int(bts.dl_frequency_pcell)+100),
                   'forw l1 MapFreqToRadioContext 1 1 %d %d' % (int(bts.dl_frequency_scell)-100, int(bts.dl_frequency_scell)+100), ]
    else:
        if bts.btstype == 'TDD':
            script += ['forw mte PhyConfigUlTiming 0', ]

    tm1 = 4 if case.tm in ['4X2'] else 2
    tm2 = 1 if case.tm in ['1'] else 2
    bandlist = case.band.upper().replace('M', '').split('-')
    ms_bandlist = case.ms_band.upper().replace('M', '').split('-')

    if bts.btstype == 'FDD' and case.ca_type in ['2CC']:
        script += ['forw mte SetMueRadioContextCell 0 %s %s %s [%s] [] [%s]' % (
            bts.phycellid_list[0], bts.dl_frequency_pcell, bandlist[1],
            tm1, tm2)]
        script += ['forw mte SetMueRadioContextCell 1 %s %s %s [%s] [] [%s]' % (
            bts.phycellid_list[1], bts.dl_frequency_scell, bandlist[0],
            tm1, tm2)]
    if gv.ms_bts:
        tm1 = 4 if case.ms_tm in ['4X2', '4X2-4X2'] else 2
        tm2 = 1 if case.ms_tm in ['1'] else 2

        if gv.ms_bts.btstype == 'TDD' and case.ca_type in ['2CC']:
            script += ['forw mte SetMueRadioContextCell 2 %s %s %s [%s] [%s %s] [%s]' % (
                gv.ms_bts.phycellid_list[0], gv.ms_bts.dl_frequency_pcell, ms_bandlist[0],
                tm1, case.ms_uldl, case.ms_ssf, tm2)]
            script += ['forw mte SetMueRadioContextCell 3 %s %s %s [%s] [%s %s] [%s]' % (
                gv.ms_bts.phycellid_list[1], gv.ms_bts.dl_frequency_scell, ms_bandlist[1],
                tm1, case.ms_uldl, case.ms_ssf, tm2)]

    if bts.btstype == 'FDD' and case.ca_type in ['2CC']:
        script += ['forw mte PhyConfigUlPowerOffset 1{-1 85 80 [80] []}']
        script += ['forw mte MtsConfigUeGroup 0 0 1{0}']
    if (case.ca_type == '2CC' and case.tm == '4X4-4X4') or (bts.btstype == 'FDD' and case.ca_type in ['2CC']):
        gv.tm500.shenick_volte_group_name = 'MUE_UDP'
        script += ['forw mte DeConfigRdaStartTestCase 0 %s [%s] [%s]' % (gv.tm500.shenick_hostname,
                                                                         gv.tm500.shenick_partition, gv.tm500.shenick_volte_group_name)]
        script += ['WAIT FOR "I: CMPI DTE RDA TEST GROUP STARTED IND:"']
    if bts.btstype == 'TDD':
        script += ['forw mte PhySetTDDCfg %s %s' % (case.uldl, case.ssf)]

    value = '4' if case.tm in ['4X2', '4X4', '94X4', '4X2-4X2', '4X4-4X4'] else '2'
    value = '1' if case.tm in ['1', '1-1'] else value
    value = '4' if bts.btstype == 'FDD' and case.ca_type in ['2CC'] else value
    script += ['SETP RRC_NUM_DL_ANTENNAS %s' % (value), ]

    value = '2 6 6' if case.ca_type.strip() else '2 4 4'
    value = '2 4 5' if case.cat5 else value
    value = '4 5 5' if case.tm in ['4X4', '94X4', '98X4'] else value
    value = '4 16 5' if case.tm in ['4X4-4X4'] else value
    value = '2 15 4' if bts.btstype == 'FDD' and case.ca_type in ['2CC'] else value
    if case.ca_type.strip() == '2CC':
        band = case.band.strip().replace('M', '')
        if band == '20-20':
            script += ['forw mte RrcAptConfigUeCap [[] [] [] [] [] [] [1{0 %s}]]' % (bts.uecap_20m_20m),
                       'forw mte Activate -1 [] [1]']
        if band == '20-10':
            script += ['forw mte RrcAptConfigUeCap [[] [] [] [] [] [] [1{0 %s}]]' % (bts.uecap_20m_10m),
                       'forw mte Activate -1 [] [1]']
        if band == '10-20':
            script += ['forw mte RrcAptConfigUeCap [[] [] [] [] [] [] [1{0 %s}]]' % (bts.uecap_10m_20m),
                       'forw mte Activate -1 [] [1]']

    if case.ue_cap:
        script += ['forw mte RrcAptConfigUeCap [[] [] [] [] [] [] [1{0 %s}]] [4]' % (gv.case.curr_case.ue_cap),
                   'forw mte Activate -1']

    if case.cat5:
        script += ['forw mte RrcAptConfigUeCap [[] [] [] [] [] [] [1{0 823FF400940003F068C41000}]]',
                   'forw mte Activate -1 [] [1]']
    if case.tm in ['4X4', '94X4', '98X4']:
        script += ['forw mte RrcAptConfigUeCap [[] [] [] [] [] [] [1{0 CA3E0441954010381FF8376260008017A31000072800209FF900000A2000}]]',
                   'forw mte Activate -1 [] [1]']

    script += ['forw mte PhyConfigSysCap %s' % (value), ]
    script += ['forw mte UsimConfig ' + _get_usim_str_single(bts.start_ue_imsi)]
    script += ['forw mte NasConfigEmmRegister 0(0 [0] [] [] [] [] [] [] [])',
               'forw mte NasAptConfigPlmnSelection 26203',
               'forw mte NasAptConfigCapability',
               'forw mte RrcAptConfigCapability', ]
    script += ['forw mte RrcAptConfigCellSelection %s' % (bts.dl_frequency_pcell),
               'forw mte Activate -1', ]
    return script


def newline():
    pass
