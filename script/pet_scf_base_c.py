from petbase import *

scf_parameters = {
    'a3Offset'                    :       'get_a3Offset',
    'a3TriggerQuantityHO'         :       'get_a3TriggerQuantityHO',
    'a3OffsetRsrpInterFreq'       :       'get_a3OffsetRsrpInterFreq',
    'actConvVoice'                :       'get_act_conv_voice',
    'actDLCAggr'                  :       'get_act_dlc_aggr',
    'actDlsVoicePacketAgg'        :       'get_act_dls_voice_packet_agg',
    'actDrx'                      :       'get_act_drx',
    'actDrxDuringMeasGap'         :       'get_actDrxDuringMeasGap',
    'actDl256QamChQualEst'        :       'get_actDl256QamChQualEst',
    'actEmerCallRedir'            :       'get_actEmerCallRedir',
    'actIMSEmerSessR9'            :       'get_actIMSEmerSessR9',
    'actFastMimoSwitch'           :       'get_act_fast_mimo_switch',
    'actFlexScellSelect'          :       'get_actFlexScellSelect',
    'actLbPucchReg'               :       'get_actLbPucchReg',
    'activatedMimoTM'             :       'get_activated_mimo_TM',
    'actModulationSchemeUL'       :       'get_ul_modulation_scheme',
    'actModulationSchemeDL'       :       'get_dl_modulation_scheme',
    'actNwReqUeCapa'              :       'get_actNwReqUeCapa',
    'actNbrForNonGbrBearers'      :       'get_act_nbr_for_nongbr_bearers',
    'actPdcpRohc'                 :       'get_act_actPdcpRohc',
    'actProactSchedBySrb'         :       'get_actProactSchedBySrb',
    'actRLFReportEval'            :       'get_actRLFReportEval',
    'actCellTrace'                :       'get_actCellTrace',
    'actAutoPucchAlloc'           :       'get_actAutoPucchAlloc',
    'actMroInterRatUtran'         :       'get_actMroInterRatUtran',
    'actServBasedMobThr'          :       'get_actServBasedMobThr',
    'actQci1eVTT'                 :       'get_act_qci1evtt',
    'actReduceWimaxInterference'  :       'get_actReduceWimaxInterference',
    'actServiceAccountSsh'        :       'get_act_service_account_ssh',
    'actServicePortState'         :       'get_act_service_port_state',
    'actSrb1Robustness'           :       'get_actSrb1Robustness',
    'actSmartDrx'                 :       'get_act_smart_drx',
    'actTmSwitch'                 :       'get_act_tm_switch',
    'actUpPtsBlanking'            :       'get_actUpPtsBlanking',
    'actUlSps'                    :       'get_act_ul_sps',
    'actUlpcMethod'               :       'get_actUlpcMethod',
    'actUlpcRachPwrCtrl'          :       'get_actUlpcRachPwrCtrl',
    'actULCAggr'                  :       'get_actULCAggr',
    'actUlMuMimo'                 :       'get_act_ul_mu_mimo',
    'actDlMuMimo'                 :       'get_act_dl_mu_mimo',
    'actUciOnlyGrants'            :       'get_act_uci_only_grants',
    'addAUeRrHo'                  :       'get_aue_rr_ho',
    'addAUeTcHo'                  :       'get_aue_tc_ho',
    'addNumDrbRadioReasHo'        :       'get_add_num_drb_radio_reasho',
    'addNumDrbTimeCriticalHo'     :       'get_add_num_drb_time_critical_ho',
    'addNumQci1DrbRadioReasHo'    :       'get_add_num_qci1_drb_radio_reasho',
    'addNumQci1DrbTimeCriticalHo' :       'get_add_num_qci1_drb_time_critical_ho',
    'aPucchAddAUeRrHo'            :       'get_apucch_add_aue_rrho',
    'aPucchAddAUeTcHo'            :       'get_apucch_add_aue_tcho',
    'aPucchMinNumEmergencySessions':      'get_apucch_minnum_eme_ses',
    'aPucchMinNumRrc'             :       'get_apucch_minnum_rrc',
    'aPucchMinNumRrcNoDrb'        :       'get_apucch_minnum_rrc_no_drb',
    'aPucchSrPeriodUpperLimit'    :       'get_apucch_sr_period_upper_limit',
    'cellSrPeriod'                :       'get_cell_srperiod',
    'chBw'                        :       'get_chbw',
    'cqiPerNp'                    :       'get_cqi_per_np',
    'countdownPucchCompr'         :       'get_countdownPucchCompr',
    'countdownPucchExp'           :       'get_countdownPucchExp',
    'deltaPucchShift'             :       'get_delta_pucch_shift',
    'dlChBw'                        :     'get_dlChBw',
    'dlInterferenceSpatialMode'   :       'get_dl_interference_spatial_mode',
    'dlMimoMode'                  :       'get_dl_mimo_mode',
    'dlSectorBeamformingMode'     :       'get_dl_sector_beamforming_mode',
    'dlSrbCqiOffset'              :       'get_dlSrbCqiOffset',
    'earfcn'                      :       'get_earfcn',
    'earfcndl'                    :       'get_earfcndl',
    'eutraCarrierInfo'            :       'get_eutraCarrierInfo',
    'ethernetPortSecurityEnabled' :       'get_ethernetPortSecurityEnabled',
    'freqEutra'                   :       'get_freqEutra',
    'fourLayerMimoAvSpectralEff'  :       'get_fourLayerMimoAvSpectralEff',
    'hsScenario'                  :       'get_hiscenario',
    'ilReacTimerUl'               :       'get_il_reac_timer_ul',
    'iniMcsUl'                    :       'get_iniMcsUl',
    'inactivityTimer'             :       'get_inactivity_timer',
    'ipAddrPrim'                  :       'get_ip_addr_prim',
    'maxNrSymPdcch'               :       'get_max_nr_sym_pdcch',
    'maxNumActDrb'                :       'get_max_num_act_drb',
    'maxNumActUE'                 :       'get_max_num_act_ue',
    'maxNumCaConfUeDc'            :       'get_max_num_ca_conf_ue_dc',
    'maxNumQci1Drb'               :       'get_max_num_qci1_drb',
    'maxNumRrc'                   :       'get_max_num_rrc',
    'maxNumRrcEmergency'          :       'get_max_num_rrc_emergency',
    'maxNumUeDl'                  :       'get_max_num_ue_dl',
    'maxNumUeDlDwPTS'             :       'get_max_num_ue_dldwpts',
    'maxNumUeUl'                  :       'get_max_num_ue_ul',
    'maxNumScells'                :       'get_max_num_scell',
    'maxNumCaConfUe'              :       'get_max_num_ca_conf_ue',
    'mbrSelector'                 :       'get_mbrSelector',
    'measQuantInterFreq'          :       'get_measQuantInterFreq',
    'n1PucchAn'                   :       'get_n1_pucch_an',
    'nCqiRb'                      :       'get_n_cqi_rb',
    'nCqiDtx'                     :       'get_n_cqi_dtx',
    'nSrsDtx'                     :       'get_n_srs_dtx',
    'nPucchF3Prbs'                :       'get_npucch_f3_prbs',
    'numOfCsiRsAntennaPorts'      :       'get_csi_ant_ports',
    'phyCellIdStart'              :       'get_phyCellIdStart',
    'prachCS'                     :       'get_prach_cs',
    'prachConfIndex'              :       'get_prach_conf_index',
    'prachFreqOff'                :       'get_prach_freq_off',
    'prachHsFlag'                 :       'get_prach_hs_flag',
    'pucchNAnCs'                  :       'get_pucch_Nan_cs',
    'reportingIntervalPm'         :       'get_reporting_interval_pm',
    'reqFreqBands'                :       'get_reqFreqBands',
    'redBwMaxRbDl'                :       'get_red_bw_max_rb_dl',
    'redBwMaxRbUl'                :       'get_red_bw_max_rb_ul',
    'riEnable'                    :       'get_ri_enable',
    'riPerM'                      :       'get_ri_perm',
    'riPerOffset'                 :       'get_ri_per_offset',
    'rrcConnectedUpperThresh'     :       'get_rrcConnectedUpperThresh',
    'rrcConnectedLowerThresh'     :       'get_rrcConnectedLowerThresh',
    'rootSeqIndex'                :       'get_rootseqindex',
    'rxCalibrationConfiguration'  :       'get_rxCalibrationConfiguration',
    'sCellActivationMethod'       :       'get_scell_activation_method',
    'srsActivation'               :       'get_srs_activation',
    'srsBwConf'                   :       'get_srs_bw_conf',
    'srsOnTwoSymUpPts'            :       'get_srs_on_two_symup_pts',
    'srsSubfrConf'                :       'get_srs_subfr_conf',
    'srsSimAckNack'               :       'get_srsSimAckNack',
    'subfrPShareRequired'         :       'get_subframe_share_required',
    'syncSigTxMode'               :       'get_sync_sig_txmode',
    'tac'                         :       'get_tac',
    'tddFrameConf'                :       'get_tdd_frame_conf',
    'tddSpecSubfConf'             :       'get_tdd_spec_subf_conf',
    'threshold1'                  :       'get_threshold1',
    'threshold2InterFreq'         :       'get_threshold2InterFreq',
    'threshold2a'                 :       'get_threshold2a',
    'ulCombinationMode'           :       'get_ul_combination_mode',
    'ulsMaxPacketAgg'             :       'get_uls_max_packet_agg',
    'ulChBw'                      :       'get_ulChBw',
}

tput_scf_params = [
        'actDrx',
        'actRLFReportEval',
        'actFastMimoSwitch',
        'actModulationSchemeUL',
        'actTmSwitch',
        'cellSrPeriod',
        'actProactSchedBySrb',
        'actRLFReportEval',
        'actAutoPucchAlloc',
        # 'actCellTrace',
        'actReduceWimaxInterference',
        'actUpPtsBlanking',
        'actULCAggr',
        'activatedMimoTM',
        'chBw',
        'cqiPerNp',
        'dlInterferenceSpatialMode',
        'dlMimoMode',
        'dlSectorBeamformingMode',
        'earfcn',
        'ethernetPortSecurityEnabled',
        'ilReacTimerUl',
        'inactivityTimer',
        'ipAddrPrim',
        'iniMcsUl',
        'maxNumUeDl',
        'maxNumUeUl',
        'maxNumUeDlDwPTS',
        'prachCS',
        'prachConfIndex',
        'prachFreqOff',
        'reportingIntervalPm',
        'riEnable',
        'rxCalibrationConfiguration',
        'sCellTmSettingWithBf',
        'srsOnTwoSymUpPts',
        'srsSubfrConf',  #Follow the template, not changed
        'subfrPShareRequired',  #mbms parameter
        'syncSigTxMode',
        'tddFrameConf',
        'tddSpecSubfConf',
        'riPerM',
        'riPerOffset',
        'maxNrSymPdcch',
        'n1PucchAn'
        # 'numOfCsiRsAntennaPorts',
]

volte_scf_params = [
        'actDlsVoicePacketAgg',
        'actDrx',
        'actDrxDuringMeasGap',
        'actSmartDrx',
        'actPdcpRohc',
        'actUlpcMethod',
        'cellSrPeriod',
        'riPerM',
        'riPerOffset',
        'tddFrameConf',
        'tddSpecSubfConf',
        'ulsMaxPacketAgg',
        ]

volte_scf_params1 = [
        'actDLCAggr',
        'actDlsVoicePacketAgg',
        'actDrx',
        'actDrxDuringMeasGap',
        'actFastMimoSwitch',
        # 'actQci1eVTT',
        'actSmartDrx',
        'actPdcpRohc',
        'actTmSwitch',
        'actUlSps',
        'actULCAggr',
        'actUlpcMethod',
        'cellSrPeriod',
        'chBw',
        'cqiPerNp',
        'deltaPucchShift',
        'dlInterferenceSpatialMode',
        'dlMimoMode',
#        'earfcn',
        'ethernetPortSecurityEnabled',
        'inactivityTimer',
        'maxNrSymPdcch',
        'maxNumActDrb',
        'maxNumActUE',
        'maxNumCaConfUeDc',
        'maxNumQci1Drb',
        'maxNumRrc',
        'maxNumRrcEmergency',
        'maxNumUeDl',
        'maxNumUeDlDwPTS',
        'maxNumUeUl',
        'n1PucchAn',
        # 'nCqiRb',
        'nCqiDtx',
        'pucchNAnCs',
        'reportingIntervalPm',
        'riEnable',
        'riPerM',
        'riPerOffset',
        'srsActivation',
        'srsBwConf',
        'srsOnTwoSymUpPts',
        'srsSubfrConf',
        'syncSigTxMode',
        'tac',
        'tddFrameConf',
        'tddSpecSubfConf',
        'ulsMaxPacketAgg',
        ]

mr_sr_params = [
    'activatedMimoTM',
    'actDLCAggr',
    'actLbPucchReg',
    'actFlexScellSelect',
    'actFastMimoSwitch',
    'actEmerCallRedir',
    'actIMSEmerSessR9',
    'actSrb1Robustness',
    'actNwReqUeCapa',
    'actUlpcRachPwrCtrl',
    'chBw',
    'countdownPucchCompr',
    'countdownPucchExp',
    'hsScenario',
    'dlMimoMode',
    'dlSrbCqiOffset',
    'dlSectorBeamformingMode',
    'earfcn',
    'eutraCarrierInfo',
    'ethernetPortSecurityEnabled',
    'freqEutra',
    'maxNumUeDl',
    'maxNumUeUl',
    'phyCellIdStart',
    'prachHsFlag',
    'prachCS',
    'reqFreqBands',
    'rootSeqIndex',
    'rrcConnectedUpperThresh',
    'rrcConnectedLowerThresh',
    'srsOnTwoSymUpPts',
    'tac',
    'tddFrameConf',
    'tddSpecSubfConf',
    'ulCombinationMode',
    ]

traffic_model_sr_params = [
    'ipAddrPrim',
    'tac',
    ]

prfoa_sr_params = [
    ]

from pet_xml import *


class c_pet_scf_base(IpaMmlItem):
    def __init__(self, pmlist):
        self.pmlist = pmlist

    def _modifi_cap_for_ho(self, bts, case, param):
        result = modify_parameter(bts, param, '0') if case.domain in ['CAP'] else []
        return result

    def get_aue_rr_ho(self, bts, case):
        return self._modifi_cap_for_ho(bts, case, 'addAUeRrHo')

    def get_aue_tc_ho(self, bts, case):
        return self._modifi_cap_for_ho(bts, case, 'addAUeTcHo')

    def _get_cell_param_with_band(self, bts, case, kwname, pmname):
        bandlist = case.band.upper().replace('M','').split('-')
        bandlist = bandlist * int(bts.cell_count/len(bandlist))
        return modify_parameter(bts, pmname, [getattr(self, kwname)(bts, case, band) for band in bandlist])

    def get_a3Offset(self, bts, case):
        result = []
        if case.domain in ['MR'] and case.is_handover and case.is_sf:
            result = modify_parameter(bts, 'a3Offset', '2')
        return result

    def get_a3TriggerQuantityHO(self, bts, case):
        result = []
        if case.domain in ['MR'] and case.is_handover and case.is_sf:
            result = modify_parameter(bts, 'a3TriggerQuantityHO', 'RSRP')
        return result

    def get_a3OffsetRsrpInterFreq(self, bts, case):
        result = []
        if case.domain in ['MR'] and case.is_handover and case.is_df:
            result = modify_parameter(bts, 'a3OffsetRsrpInterFreq', '2')
        return result

    def get_act_conv_voice(self, bts, case):
        if case.domain in ['CAP']:
            value = 'true'
            return modify_parameter(bts, 'actConvVoice', value)
        else:
            return []

    def get_act_dlc_aggr(self, bts, case):
        if case.ca_type.upper() in ['2CC', '3CC', '4CC'] or case.f_2324:
            return modify_parameter(bts, 'actDLCAggr', 'true')
        elif case.domain in ['CAP'] and case.ca_type in ['2CC', '3CC']:
            return modify_parameter(bts, 'actDLCAggr', 'true')
        else:
            return []

        # value = 'true' if case.ca_type.strip() else 'false'
        # value = 'true' if case.f_2324 else value
        # return modify_parameter(bts, 'actDLCAggr', value)

    def get_act_dls_voice_packet_agg(self, bts, case):
        value = 'false' if case.volte_one_way_delay else 'true'
        return modify_parameter(bts, 'actDlsVoicePacketAgg', value)

    def get_act_drx(self, bts, case):
        if case.domain in ['CAP']:
            value= 'true'if case.smartdrx or case.drx else 'false'
            return modify_parameter(bts, 'actDrx', value)
        value = 'true' if case.drx else 'false'
        return modify_parameter(bts, 'actDrx', value)

    def get_actDrxDuringMeasGap(self, bts, case):
        if case.drx:
            return []
        else:
            return modify_parameter(bts, 'actDrxDuringMeasGap', 'false')

    def get_actDl256QamChQualEst(self, bts, case):
        if not case.qam_256:
            return []
        else:
            return modify_parameter(bts, 'actDl256QamChQualEst', 'false')

    def get_actEmerCallRedir(self, bts, case):
        if case.f_2664:
            return modify_parameter(bts, 'actEmerCallRedir', 'Enabled')
        else:
            return modify_parameter(bts, 'actEmerCallRedir', 'Disabled')

    def get_actIMSEmerSessR9(self, bts, case):
        if case.f_2664:
            return modify_parameter(bts, 'actIMSEmerSessR9', 'true')
        else:
            return modify_parameter(bts, 'actIMSEmerSessR9', 'false')

    def get_act_fast_mimo_switch(self, bts, case):
        result = []
        tmlist = case.tm.upper().replace('TM','').split('-')
        tmlist = tmlist * int(bts.cell_count/len(tmlist))
        values = []
        print "XXXXXXXXX", tmlist, bts.cell_count
        for cellid in range(bts.cell_count):
            value = 'true' if tmlist[cellid] in ['4', '9', '4X2', '98X4', '94X4', '4X4'] else 'false'
            values.append(value)
        return modify_parameter(bts, 'actFastMimoSwitch', values)

    def get_actFlexScellSelect(self, bts, case):
        if case.domain in ['CAP']:
            value = 'true' if case.ca_type.strip() else 'false'
            return modify_parameter(bts, 'actFlexScellSelect', value)
        if case.f_2664:
            return modify_parameter(bts, 'actFlexScellSelect', 'true')
        else:
            return modify_parameter(bts, 'actFlexScellSelect', 'false')


    def get_actLbPucchReg(self, bts, case):
        if case.f_2664:
            return modify_parameter(bts, 'actLbPucchReg', 'true')
        else:
            return modify_parameter(bts, 'actLbPucchReg', 'false')


    def get_activated_mimo_TM(self, bts, case):  #TODO
        result = []
        astr = '\n<p name="activatedMimoTM">TM4</p>\n'
        astr2 = '\n<p name="activatedMimoTM">TM9</p>\n'
        if case.releaseno in ['TL16','TL16A']:
            if case.tm in ['4X2', '4X2-TM4X2', '4X2-TM4X2-TM4X2', '4X4', '4']:
                for cellid in range(bts.cell_count):
                    result.append('add|%s|distName=%s' %(astr, bts.lncels[cellid]))
            if case.tm == '94X4':
                for cellid in range(bts.cell_count):
                    result.append('add|%s|distName=%s' %(astr2, bts.lncels[cellid]))
        if case.releaseno in ['TL17', 'TRUNK', 'TL17SP', 'TL17A']:
            from pet_xml import get_parameters, get_mos
            items = get_parameters(bts, 'activatedMimoTM')
            newvalue = 'TM4' if case.tm.upper().replace('TM', '') in ['4X2', '4X2-4X2', '4X2-4X2-4X2', '4X4'] else ''
            newvalue = 'TM9' if case.tm in ['94X4'] else newvalue
            if items:
                if newvalue:
                    return modify_parameter(bts, 'activatedMimoTM', newvalue)
            else:
                if newvalue:
                    for tddcell in get_mos(bts, 'LNCEL_TDD'):
                        result.append('add|\n<p name="activatedMimoTM">%s</p>\n|distName=%s' %(newvalue, tddcell.get('distName')))
        return result

    def get_ul_modulation_scheme(self, bts, case):
        value = '64QAMand16QAMHighMCS' if case.cat5 else '16QAMHighMCS'
        return modify_parameter(bts, 'actModulationSchemeUL', value)

    def get_dl_modulation_scheme(self, bts, case):
        if case.qam_256:
            return modify_parameter(bts, 'actModulationSchemeDl', '256QAM')
        else:
            return []

    def get_actNwReqUeCapa(self, bts, case):
        value = 'true' if case.f_2324 else 'false'
        return modify_parameter(bts, 'actNwReqUeCapa', value)

    def get_actProactSchedBySrb(self, bts, case):
        if case.up_schedule:
            return modify_parameter(bts, 'actProactSchedBySrb', 'false')
        else:
            return []

    def _cap_limit_fd20(self, bts, case):
        return case.domain in ['CAP'] and (case.f_limit or case.fd_20ue)

    def _modify_for_cap_limit_fd20(self, bts, case, param):
        result = []
        if case.domain in ['CAP']:
            result = modify_parameter(bts, param, 'false') if self._cap_limit_fd20(bts, case) else result
        return result

    def get_act_nbr_for_nongbr_bearers(self, bts, case):
        return self._modify_for_cap_limit_fd20(bts, case, 'actNbrForNonGbrBearers')

    def get_act_ul_mu_mimo(self, bts, case):
        return self._modify_for_cap_limit_fd20(bts, case, 'actUlMuMimo')

    def get_act_dl_mu_mimo(self, bts, case):
        return self._modify_for_cap_limit_fd20(bts, case, 'actDlMuMimo')

    def get_act_uci_only_grants(self, bts, case):
        if bts.btstype == 'FDD' and case.domain in ['CAP']:
            value = 'true' if case.ca_type.upper() == '4CC' else 'false'
            return modify_parameter(bts, 'actUciOnlyGrants ', value)
        else:
            return []

    def get_actRLFReportEval(self, bts, case):
        if case.f_678:
            return modify_parameter(bts, 'actRLFReportEval', 'true')
        else:
            return []

    def get_actCellTrace(self, bts, case):
        value = 'true' if case.f_678 else 'false'
        return modify_parameter(bts, 'actCellTrace', value)

    def get_actAutoPucchAlloc(self, bts, case):
        if case.domain in ['CAP']:
            value = 'true' if case.f_1130 or case.f_2664 else 'false'
            return modify_parameter(bts, 'actAutoPucchAlloc', value)
        if bts.airscale and case.case_type.strip().upper() in ['PING_DELAY_32','PING_DELAY_1500','PING_DELAY_1400'] or case.f_2664 :
            return modify_parameter(bts, 'actAutoPucchAlloc', 'false')
        elif not case.f_2664:
            return modify_parameter(bts, 'actAutoPucchAlloc', 'false')
        else:
            return []

    def get_actMroInterRatUtran(self, bts, case):
        value = 'true' if case.f_1749 else 'false'
        return modify_parameter(bts, 'actMroInterRatUtran', value)

    def get_actServBasedMobThr(self, bts, case):
        value = 'true' if case.f_1749 else 'false'
        return modify_parameter(bts, 'actServBasedMobThr', value)

    def get_act_qci1evtt(self, bts, case):
        value = 'true' if case.lte1406 else 'false'
        return modify_parameter(bts, 'actQci1eVTT', value)

    def get_actReduceWimaxInterference(self, bts, case):
        value = 'true' if case.wimax else 'false'
        return modify_parameter(bts, 'actReduceWimaxInterference', value)

    def get_act_service_account_ssh(self, bts, case):
        return modify_parameter(bts, 'actServiceAccountSsh', 'true')

    def get_act_service_port_state(self, bts, case):
        return modify_parameter(bts, 'actServicePortState', 'true')

    def get_act_smart_drx(self, bts, case):
        if case.domain in ['CAP']:
            value= 'true'if case.smartdrx else 'false'
            return modify_parameter(bts, 'actSmartDrx', value)
        if case.drx:
            return []
        else:
            return modify_parameter(bts, 'actSmartDrx', 'false')

    def get_actSrb1Robustness(self, bts, case):
        value = 'true' if case.f_2026 else 'false'
        return modify_parameter(bts, 'actSrb1Robustness', value)

    def get_act_tm_switch(self, bts, case):
        value = 'true' if case.tm38 or case.tm39 else 'false'
        value = 'true' if case.case_type in ['MIX_MR'] else value
        return modify_parameter(bts, 'actTmSwitch', value)

    def get_actUpPtsBlanking(self, bts, case):
        value = 'true' if case.wimax else 'false'
        return modify_parameter(bts, 'actUpPtsBlanking', value)

    def get_act_ul_sps(self, bts, case):
        value = 'true' if case.ul_sps else 'false'
        return modify_parameter(bts, 'actUlSps', value)

    def get_act_actPdcpRohc(self, bts, case):
        value = 'true' if case.ul_sps else 'false'
        value = 'true' if case.case_type == 'MIX_CAP' else value
        value = 'false' if case.volte_one_way_delay else value
        return modify_parameter(bts, 'actPdcpRohc', value)

    def get_apucch_add_aue_rrho(self, bts, case):
        if case.domain in ['CAP'] and case.f_1130:
            return modify_parameter(bts, 'aPucchAddAUeRrHo', '0')
        else:
            return []

    def _modify_cap_apucch(self, bts, case, param):
        return modify_parameter(bts, param, '0') if case.domain in ['CAP'] and case.f_1130 else []

    def get_apucch_add_aue_tcho(self, bts, case):
        return self._modify_cap_apucch(bts, case, 'aPucchAddAUeTcHo') if case.domain in ['CAP'] else []

    def get_apucch_minnum_eme_ses(self, bts, case):
        return self._modify_cap_apucch(bts, case, 'aPucchMinNumEmergencySessions') if case.domain in ['CAP'] else []

    def get_apucch_minnum_rrc(self, bts, case):
        return self._modify_cap_apucch(bts, case, 'aPucchMinNumRrc') if case.domain in ['CAP'] else []

    def get_apucch_minnum_rrc_no_drb(self, bts, case):
        return self._modify_cap_apucch(bts, case, 'aPucchMinNumRrcNoDrb') if case.domain in ['CAP'] else []

    def get_apucch_sr_period_upper_limit(self, bts, case):
        if case.f_1130 and case.domain in ['CAP']:
            return modify_parameter(bts, 'aPucchSrPeriodUpperLimit', '40')
        else:
            return []

    def get_add_num_drb_radio_reasho(self, bts, case):
        return self._modifi_cap_for_ho(bts, case, 'addNumDrbRadioReasHo')

    def get_add_num_drb_time_critical_ho(self, bts, case):
        return self._modifi_cap_for_ho(bts, case, 'addNumDrbTimeCriticalHo')

    def get_add_num_qci1_drb_radio_reasho(self, bts, case):
        return self._modifi_cap_for_ho(bts, case, 'addNumQci1DrbRadioReasHo')

    def get_add_num_qci1_drb_time_critical_ho(self, bts, case):
        return self._modifi_cap_for_ho(bts, case, 'addNumQci1DrbTimeCriticalHo')

    def get_cell_srperiod(self, bts, case):
        value = '5ms' if case.case_type.strip().upper() in ['PING_DELAY_32','PING_DELAY_1500','PING_DELAY_1400'] else '40ms'
        value = '40ms' if case.case_type.strip().upper() in ['PING_DELAY_32','PING_DELAY_1500','PING_DELAY_1400'] and 'SR=40ms' in case.case_name else value
        value = '20ms' if case.case_type.strip().upper() in ['PING_DELAY_32','PING_DELAY_1500','PING_DELAY_1400'] and 'SR=20ms' in case.case_name else value
        value = '20ms' if case.domain.strip().upper() == 'VOLTE' else value
        if case.domain == 'MR':
            value = '5ms' if case.uldl == 1 else '10ms'
        value = '10ms' if case.up_schedule else value
        if case.domain in ['CAP']:
            value = '40ms' if case.has_cap_volte else '80ms'
        if bts.btstype == 'FDD' and case.domain in ['CAP']:
            value = '10ms' if band in ['1.4','3'] else '40ms'
        return modify_parameter(bts, 'cellSrPeriod', value)

    def get_dlChBw(self, bts, case):
        result = []
        bandlist = case.band.upper().replace('M','').split('-')
        bandlist = bandlist * int(bts.cell_count/len(bandlist))
        values = [bandlist[cellid]+' MHz' for cellid in range(bts.cell_count)]
        return modify_parameter(bts, 'dlChBw', values)

    def get_ulChBw(self, bts, case):
        if bts.btstype == 'FDD' and case.domain in ['CAP']:
            bandlist = case.band.upper().replace('M','').split('-')
            bandlist = bandlist * int(bts.cell_count/len(bandlist))
            values = [bandlist[cellid]+' MHz' for cellid in range(bts.cell_count)]
            return modify_parameter(bts, 'ulChBw', values)
        else:
            return []

    def get_chbw(self, bts, case):
        result = []
        bandlist = case.band.upper().replace('M','').split('-')
        bandlist = bandlist * int(bts.cell_count/len(bandlist))
        values = [bandlist[cellid]+' MHz' for cellid in range(bts.cell_count)]
        return modify_parameter(bts, 'chBw', values)

    def _get_cqi_per_np(self, bts, case, band):
        value = '20ms' if band in ['1.4'] else '40ms'
        return value
    def get_cqi_per_np(self, bts, case):
        # if bts.airscale:
        #     return []
        # else:
        value = '20ms' if case.case_type.strip().upper() in ['PING_DELAY_32','PING_DELAY_1500','PING_DELAY_1400'] else '40ms'
        value = '20ms' if case.domain == 'MR' else value
        value = '80ms' if case.domain in ['VOLTE', 'CAP'] else value
        if bts.btstype == 'FDD' and case.domain in ['CAP']:
            return self._get_cell_param_with_band(bts, case, '_get_cqi_per_np', 'cqiPerNp')
        return modify_parameter(bts, 'cqiPerNp', value)

    def get_countdownPucchCompr(self, bts, case):
        if case.f_2664:
            return modify_parameter(bts, 'countdownPucchCompr', '60min')
        else:
            return []

    def get_countdownPucchExp(self, bts, case):
        if case.f_2664:
            return modify_parameter(bts, 'countdownPucchExp', '1min')
        else:
            return []

    def get_delta_pucch_shift(self, bts, case):
        return modify_parameter(bts, 'deltaPucchShift', '1')

    def get_dl_interference_spatial_mode(self, bts, case):
        if case.tm in ['1', '1-TM1', 'TM1-TM1','1-TM1-TM1']:
            return modify_parameter(bts, 'dlInterferenceSpatialMode', 'SingleTX')
        else:
            return []

    def get_dl_mimo_mode(self, bts, case):
        data ={
            '1'     :       'SingleTX',
            '2'     :       'TXDiv',
            '3'     :       'Dynamic Open Loop MIMO',
            '4'     :       'Closed Loop Mimo',
            '7'     :       'Single Stream Beamforming',
            '8'     :       'Dual Stream Beamforming',
            '9'     :       'Closed Loop MIMO (8x2)',
            '4X2'   :       'Closed Loop MIMO (4x2)',
            '98X4'  :       'Closed Loop MIMO (8x4)',
            '94X4'  :       'Closed Loop MIMO (4x4)',
            '4X4'   :       'Closed Loop MIMO (4x4)',
            '44X4'  :       'Closed Loop MIMO (4x4)',
        }
        values = []
        tmlist = case.tm.upper().replace('TM','').split('-')
        tmlist = tmlist * int(bts.cell_count/len(tmlist))
        print 'XXXXXXXXXXX',bts.cell_count, tmlist
        for cellid in range(bts.cell_count):
            # value = 'Closed Loop MIMO (4x2)' if tmlist[cellid] == '4X2' else data[tmlist[cellid]]
            # values.append(value)
            values.append(data[tmlist[cellid]])
        return modify_parameter(bts, 'dlMimoMode', values)

    def get_dl_sector_beamforming_mode(self, bts, case):
        result = []
        if case.releaseno in ['TL16','TL16A', 'TL17', 'TRUNK','TL17SP']:
            if case.pipe == 2 or case.tm.replace('TM', '').upper() in ['1', '1-1', '1-1-1', '4X2', '4X2-4X2', '4X2-4X2-4X2','94X4', '4X4']:
                return delete_parameter(bts, 'dlSectorBeamformingMode')
        return result

    def get_dlSrbCqiOffset(self, bts, case):
        result = []
        if case.f_2026:
            if scf_has_parameter(bts, 'dlSrbCqiOffset'):
                pass
            else:
                astr = '<p name="dlSrbCqiOffset">-20</p>\n'
                if case.releaseno in ['TL17', 'TRUNK', 'TL17SP', 'TL17A']:
                    for tddcell in bts.allcells:
                        result.append('add|%s|distName=%s' %(astr, bts.tddcell.get('distName')))
                else:
                    for cellid in range(bts.cell_count):
                        result.append('add|%s|distName=%s' %(astr, bts.lncels[cellid]))
        return result

    def get_earfcn(self, bts, case):
        result = []
        values = []
        if case.domain == 'CPK' and bts.rru_type == 'FZHJ':
            band = case.band.upper().replace('M','')
            if band == '10-20':
                values = ['38050', '37900']
            if band == '20-10':
                values = ['37900', '38050']
            if band == '20-20-10':
                values = ['40540', '49723', '40861']
            if band == '20-20-20':
                values = ['40540', '40740', '40938']
            if values:
                result = modify_parameter(bts, 'earfcn', values)

        if case.domain == 'CPK' and case.ulca and bts.rru_type == 'FZHJ':
            band = case.band.upper().replace('M','')
            if band == '20-10':
                values = ['37900', '38050']
            if band == '20-20':
                values = ['37900', '38100']
            if values:
                result = modify_parameter(bts, 'earfcn', values)

        if bts.new_earfcn_list:
             result += modify_parameter(bts, 'earfcn', bts.new_earfcn_list)
        return result

    def get_earfcndl(self, bts, case):
        result = []
        values = []
        # if case.domain == 'CPK' and bts.rru_type == 'FZHJ':
        #     band = case.band.upper().replace('M','')
        #     if band == '10-20':
        #         values = ['38050', '37900']
        #     if band == '20-10':
        #         values = ['37900', '38050']
        #     if band == '20-20-10':
        #         values = ['40540', '49723', '40861']
        #     if band == '20-20-20':
        #         values = ['40540', '40740', '40938']
        #     if values:
        #         result = modify_parameter(bts, 'earfcndl', values)

        # if case.domain == 'CPK' and case.ulca:
        #     band = case.band.upper().replace('M','')
        #     if band == '20-10':
        #         values = ['37900', '38050']
        #     if band == '20-20':
        #         values = ['37900', '38100']
        #     if values:
        #         result = modify_parameter(bts, 'earfcndl', values)

        # result += modify_parameter(bts, 'earfcnul', values+18000)

        # if bts.new_earfcn_list:
        #      result += modify_parameter(bts, 'earfcndl', bts.new_earfcn_list)
        return result

    def get_eutraCarrierInfo(self, bts, case):
        result = []
        if hasattr(bts, 'new_eutraCarrierInfo_list') and bts.new_eutraCarrierInfo_list:
            print 'XXXXXXXXXXXXXX', bts.new_eutraCarrierInfo_list
            return modify_parameter(bts, 'eutraCarrierInfo', bts.new_eutraCarrierInfo_list)
        return result

    def get_ethernetPortSecurityEnabled(self, bts, case):
        return modify_parameter(bts, 'ethernetPortSecurityEnabled', 'false')

    def get_freqEutra(self, bts, case):
        black_str = '''
        <list name="blacklistHoL">
            <item>
                <p name="blacklistTopo">onlyX2</p>
                <p name="freqEutra">PH0</p>
                <p name="phyCellIdStart">0</p>
                <p name="phyCellIdRange">n504</p>
            </item>
        </list>
        '''
        result = []
        if case.ho_type == 'INTER' and case.ho_path == 'S1':
            tstr = black_str.replace('PH0', bts.freqEutra_tstr)
            from pet_xml import get_mos
            lncels = get_mos(bts)
            for cell in lncels:
                result.append('delete||distName=%s iterchild name=blacklistHoL' %(cell.get('distName')))
                result.append('add|%s|distName=%s' %(tstr, cell.get('distName')))
        return result

    def get_fourLayerMimoAvSpectralEff(self, bts, case):
        if case.domain in ['CAP']:
            value = '' if case.tm == '4X2' else '0.5'
            return modify_parameter(bts, 'fourLayerMimoAvSpectralEff', value)
        elif case.domain in ['CPK']:
            value = '0.5' if case.tm in ['4X4', '98X4']  else ''
            return modify_parameter(bts, 'fourLayerMimoAvSpectralEff', value)
        else:
            return []

    def get_hiscenario(self, bts, case):
        result = []
        if case.high_speed:
            if scf_has_parameter(bts, 'hsScenario'):
                return modify_parameter(bts, 'hsScenario', 'scenario1')
            else:
                astr = '<p name="hsScenario">scenario1</p>\n'
                for cellid in range(bts.cell_count):
                    result.append('add|%s|distName=%s' %(astr, bts.lncels[cellid]))
        return result

    def get_il_reac_timer_ul(self, bts, case):
        value = '1500' if case.scheduled else '0'
        return modify_parameter(bts, 'ilReacTimerUl', value)

    def get_iniMcsUl(self, bts, case):
        if not case.scheduled and case.case_type.strip().upper() in ['PING_DELAY_32','PING_DELAY_1500','PING_DELAY_1400']:
            return modify_parameter(bts, 'iniMcsUl', '4')
        else:
            return []

    def get_inactivity_timer(self, bts, case):
        timer = '300' if case.domain.strip().upper() == 'VOLTE' else '20'
        timer = '3000' if case.case_type.strip().upper() in ['THROUGHPUT_MUE_DL',
                                    'THROUGHPUT_MUE_UL',
                                    'PING_DELAY_32',
                                    'FTP_UPLOAD',
                                    'FTP_DOWNLOAD'] else timer
        timer = '10000' if case.case_type in ['MIX_CAP'] else timer
        return modify_parameter(bts, 'inactivityTimer', timer)

    def get_ip_addr_prim(self, bts, case):
        value = bts.mme_ip
        value = bts.work_mme if case.domain == 'MR' else value
        value = case.cap_fix_mme_ip if case.domain in ['CAP'] and case.cap_fix_mme_ip.strip() else value
        return modify_parameter(bts, 'ipAddrPrim', value)

    def get_max_nr_sym_pdcch(self, bts, case):
        return modify_parameter(bts, 'maxNrSymPdcch', '1')

    def _get_max_num_act_drb(self, bts, case, band):
        if case.domain in ['CAP']:
            value = '1200'
            if band in ['20'] and case.uldl == 1 and case.ssf == 7:
                value = '1800' if case.ca_type in ['2CC', '3CC'] else '2400'
            if bts.btstype == 'FDD':
                value = '108'  if band in ['1.4'] else value
                value = '300'  if band in ['3'] else value
                value = '1260' if band in ['5','10'] else value
                value = '2520' if band in ['15','20'] else value
            return value
        return '1800' if band in ['15', '20'] and case.uldl == 1 else '1200'

    def get_max_num_act_drb(self, bts, case):
        return self._get_cell_param_with_band(bts, case, '_get_max_num_act_drb', 'maxNumActDrb')

    def _get_max_num_act_ue(self, bts, case, band):
        value = '400'
        value = '800' if case.uldl == 1 and band in ['20','15'] and case.f_limit and not bts.airscale else value
        value = '800' if case.uldl == 1 and band in ['20','15'] and case.fd_20ue and not bts.airscale else value
        value = '600' if case.uldl == 1 and band in ['20','15'] and not case.f_limit and not bts.airscale else value
        value = '600' if case.uldl == 2 and band in ['20','15'] and case.f_limit and not bts.airscale else value
        value = '600' if band in ['20'] and case.f_limit and bts.airscale else value
        value = '600' if case.uldl == 2 and band in ['20','15'] and case.fd_20ue and not bts.airscale else value
        value = '600' if case.uldl == 1 and band in ['20','15'] and not case.fd_20ue and not bts.airscale else value
        value = '550' if band in ['10'] and case.f_limit and bts.airscale else value
        value = '40'  if bts.btstype == 'FDD' and band in ['1.4'] else value
        value = '116'  if bts.btstype == 'FDD' and band in ['3'] else value
        value = '420' if bts.btstype == 'FDD' and band in ['5','10'] else value
        value = '840' if bts.btstype == 'FDD' and band in ['15','20'] else value
        return value

    def get_max_num_act_ue(self, bts, case):
        if case.domain in ['CAP']:
            return self._get_cell_param_with_band(bts, case, '_get_max_num_act_ue', 'maxNumActUE')
        if case.domain == 'VOLTE':
            value = '480' if case.uldl == 1 else '240'
        if case.domain == 'MR':
            value = '200'
        return modify_parameter(bts, 'maxNumActUE', value)


    def get_max_num_ca_conf_ue_dc(self, bts, case):
        value = '100' if case.case_type in ['MIX_CAP'] else '50'
        return modify_parameter(bts, 'maxNumCaConfUeDc', value)

    def _get_max_num_qci1_drb(self, bts, case, band):
        if band == '10':
            value = '300' if case.uldl == 1 else '150'
        if band in ['15', '20']:
            value = '400' if case.uldl == 1 else '200'
        if bts.btstype == 'FDD' and case.domain in ['CAP']:
            value = '200'   if band in ['5','10'] else value
            value = '300'   if band in ['15','20'] else value
            value = '1'     if band in ['1.4'] else value
            value = '4'     if band in ['3'] else value
        return value

    def get_max_num_qci1_drb(self, bts, case):
        if case.domain in ['CAP']:
            return self._get_cell_param_with_band(bts, case, '_get_max_num_qci1_drb', 'maxNumQci1Drb')
        else:
            return []

    def get_max_num_rrc(self, bts, case):
        if case.domain in ['CAP']:
            return self._get_cell_param_with_band(bts, case, '_get_max_num_act_ue', 'maxNumRrc')
        value = '480' if case.uldl == 1 else '240'
        return modify_parameter(bts, 'maxNumRrc', value)

    def get_max_num_rrc_emergency(self, bts, case):
        if case.domain in ['CAP']:
            return self._get_cell_param_with_band(bts, case, '_get_max_num_act_ue', 'maxNumRrcEmergency')
        value = '480' if case.uldl == 1 else '240'
        return modify_parameter(bts, 'maxNumRrcEmergency', value)

    def _get_max_num_ue_dl(self, bts, case, band):
        value = '12' if band in ['15', '20'] else '10'
        value = '20' if case.max_tti_user else value
        value = '20' if case.domain in ['CAP'] and case.fd_20ue else value
        value = '8'  if band in ['10'] and case.domain in ['MR'] else value
        value = '14' if band in ['10'] and bts.btstype == 'FDD' and case.domain in ['CAP'] else value
        value = '17' if band in ['15'] and bts.btstype == 'FDD' and case.domain in ['CAP'] else value
        value = '20' if band in ['20'] and bts.btstype == 'FDD' and case.domain in ['CAP'] else value
        value = '7'  if band in ['1.4','3','5'] and bts.btstype == 'FDD' and case.domain in ['CAP'] else value
        return value

    def get_max_num_ue_dl(self, bts, case):
        return self._get_cell_param_with_band(bts, case, '_get_max_num_ue_dl', 'maxNumUeDl')

    def _get_max_num_ue_dldwpts(self, bts, case, band):
        if case.domain in ['CAP']:
            value = '8' if band == '20' else '7'
            value = '12' if case.fd_20ue else value
            return value
        if case.ssf == 5:
            value = '0'
        else:
            value = '8' if band in ['15', '20'] else '7'
        value = '12' if case.max_tti_user else value
        return value

    def get_max_num_ue_dldwpts(self, bts, case):
        return self._get_cell_param_with_band(bts, case, '_get_max_num_ue_dldwpts', 'maxNumUeDlDwPTS')

    def _get_max_num_ue_ul(self, bts, case, band):
        if case.domain in ['CAP']:
            value = '12' if band == '20' else '10'
            value = '20' if case.fd_20ue else value
            return value
        value = '12' if band in ['15', '20'] else '10'
        value = '20' if case.max_tti_user or case.fd_20ue else value
        if case.ul_sps:
            value = str(int(value)+4)
        value = '8'  if band in ['10'] and case.domain.upper() in ['MR'] else value
        value = '14' if band in ['10'] and bts.btstype == 'FDD' and case.domain in ['CAP'] else value
        value = '17' if band in ['15'] and bts.btstype == 'FDD' and case.domain in ['CAP'] else value
        value = '20' if band in ['20'] and bts.btstype == 'FDD' and case.domain in ['CAP'] else value
        value = '7'  if band in ['1.4','3','5'] and bts.btstype == 'FDD' and case.domain in ['CAP'] else value
        return value

    def get_max_num_ue_ul(self, bts, case):
        return self._get_cell_param_with_band(bts, case, '_get_max_num_ue_ul', 'maxNumUeUl')

    def get_max_num_scell(self, bts, case):
        if case.domain in ['CAP']:
            value = '2' if case.ca_type == '3CC' else '1'
            return modify_parameter(bts, 'maxNumScells', value)
        else:
            return []

    def get_mbrSelector(self, bts, case):
        if case.qam_256:
            return modify_parameter(bts, 'mbrSelector', 'ueCapability')
        else:
            return []

    def get_measQuantInterFreq(self, bts, case):
        result = []
        if case.domain in ['MR'] and case.is_handover and case.is_df:
            result = modify_parameter(bts, 'measQuantInterFreq', 'rsrp')
        return result

    def get_max_num_ca_conf_ue(self, bts, case):
        value = '100' if case.domain in ['CAP'] else '50'
        return modify_parameter(bts, 'maxNumCaConfUe', value)

    def _get_n1_pucch_an(self, bts, case, band):
        value = '30' if band in ['1.4'] else value
        value = '24' if band in ['3'] else value
        value = '18' if band in ['5','10'] else value
        value = '36' if band in ['15','20'] else value
        value = '72' if band in ['5','10'] and case.ca_type.upper()  in ['2CC','3CC','4CC'] else value
        value = '90' if band in ['15','20'] and case.ca_type.upper()  in ['2CC','3CC','4CC'] else value
        return value

    def get_n1_pucch_an(self, bts, case):
        if bts.btstype == 'FDD' and case.domain in ['CAP']:
            return self._get_cell_param_with_band(bts, case, '_get_n1_pucch_an', 'n1PucchAn')
        value = '108' if case.domain in ['VOLTE', 'CAP'] else '10'
        value = '72' if case.domain == 'MR' else value
        value = '72' if case.case_type == 'FTP_DOWNLOAD' else value
        value = '10' if case.case_type == 'FTP_UPLOAD' else value
        return modify_parameter(bts, 'n1PucchAn', value)

    def _get_n_cqi_rb(self, bts, case, band):
        if case.domain == 'CPK':
            value = '2' if case.uldl == 2 and case.case_type == 'THROUGHPUT_MUE_DL' else '1'
        else:
            value = '6' if band in ['20', '15'] else '5'
        value = '20' if case.domain == 'MR' else value
        if case.domain in ['CAP']:
            if bts.btstype == 'FDD':
                value = '1' if band in ['1.4','3'] else value
                value = '4' if band in ['5','10'] else value
                value = '7' if band in ['15','20'] else value
            else:
                value = '7' if case.uldl == 1 and case.drx else value
                value = '5' if case.uldl == 1 and not case.drx else '7'
                value = '9' if case.uldl == 2 and case.drx else '7'
                value = '5' if case.uldl == 2 and not case.drx else '7'
        return value

    def get_n_cqi_rb(self, bts, case):
        return self._get_cell_param_with_band(bts, case, '_get_n_cqi_rb', 'nCqiRb')

    def get_n_cqi_dtx(self, bts, case):
        if case.domain =='VOLTE':
            if case.releaseno == 'TL16':
                value = '0' if case.case_type == 'VOLTE_CAP' else '100'
                return modify_parameter(bts, 'nCqiDtx', value)
        if case.domain in ['CAP']:
             return modify_parameter(bts, 'nCqiDtx', '0')
        return []

    def get_n_srs_dtx(self, bts, case):
        if case.domain in ['CAP']:
            return modify_parameter(bts, 'nSrsDtx', '0')
        else:
            return []

    def get_npucch_f3_prbs(self, bts, case):
        if case.domain in ['CAP']:
            value = '4' if case.ca_type == '3CC' else '0'
            return modify_parameter(bts, 'nPucchF3Prbs', value)
        else:
            return []

    def get_csi_ant_ports(self, bts, case):
        value = '4' if case.tm.strip() in ['94X4', '4X4'] else '8'
        return modify_parameter(bts, 'numOfCsiRsAntennaPorts', value)

    def get_phyCellIdStart(self, bts, case):
        if case.ho_type.upper().strip() == 'INTER' and case.ho_path.strip() == 'S1':
            return modify_parameter(bts, 'phyCellIdStart', '0')
        return []


    def get_prach_cs(self, bts, case):
        value = '6' if case.format == '4' else '12'
        if case.domain == 'MR':
            value = '11' if case.high_speed else '12'
        return modify_parameter(bts, 'prachCS', value)

    def get_prach_conf_index(self, bts, case):
        pdef = {
            '0':    '3',
            '1':    '23',
            '2':    '33',
            '4':    '51',
            }
        return modify_parameter(bts, 'prachConfIndex', pdef[str(case.format)])

    def _get_prach_frea_off(self, bts, case, band):
        value = '0' if band in ['1.4'] else value
        value = '2' if band in ['3','5'] else value
        value = '4' if band in ['10'] else value
        value = '5' if band in ['20'] else value
        value = '5' if band in ['5','10'] and case.ca_type.upper in ['2CC','3CC','4CC'] else value
        value = '7' if band in ['15'] and case.ca_type.upper in ['2CC','3CC','4CC'] else value
        value = '8' if band in ['20'] and case.ca_type.upper in ['2CC','3CC','4CC'] else value
        return value

    def get_prach_freq_off(self, bts, case):
        if bts.btstype == 'FDD' and case.domain in ['CAP']:
            return self._get_cell_param_with_band(bts, case, '_get_prach_frea_off', 'prachFreqOff')
        value = '0' if case.format == '4' else '2'
        value = '3' if case.uldl == 2 and case.case_type == 'THROUGHPUT_MUE_DL' else value
        value = '3' if case.case_type == 'FTP_DOWNLOAD' else value
        value = '4' if case.ca_type == '3CC' else value
        value = '8' if case.uldl == 1 and case.drx and case.domain in ['CAP'] else value
        value = '7' if case.uldl == 1 and not case.drx and case.domain in ['CAP'] else value
        value = '9' if case.uldl == 2 and case.drx and case.domain in ['CAP'] else value
        value = '7' if case.uldl == 2 and not case.drx and case.domain in ['CAP'] else value
        return modify_parameter(bts, 'prachFreqOff', value)

    def get_prach_hs_flag(self, bts, case):
        value = 'true' if case.high_speed else 'false'
        return modify_parameter(bts, 'prachHsFlag', value)

    def get_pucch_Nan_cs(self, bts, case):
        return modify_parameter(bts, 'pucchNAnCs', '0')

    def get_reporting_interval_pm(self, bts, case):
        return modify_parameter(bts, 'reportingIntervalPm', '15min')

    def get_reqFreqBands(self, bts, case):
        astr = '''
        <list name="reqFreqBands">
            <item>
            <p name="bandNumber">40</p>
            <p name="bandPrio">3</p>
            </item>
        </list>\n
        '''
        result = []
        if case.f_2324:
            if case.releaseno in ['TL17', 'TRUNK', 'TL17SP', 'TL17A']:
                pass
            else:
                if scf_has_parameter(bts, 'bandNumber'):
                    result.append('add|%s|distName=%s' %(astr, bts.btsdistName))
        return result

    def get_ri_enable(self, bts, case):
        #result = []
        # if bts.airscale:
        #     return []
        # else:
        value = 'false' if case.tm in ['1', '1-TM1', '1-TM1-TM1', '2', '7'] else 'true'
        return modify_parameter(bts, 'riEnable', value)

    def get_ri_perm(self, bts, case):
        if case.domain in ['CAP']:
            value = '1' if case.drx or case.ca_type == '2CC' or case.tm == '4X2' else '2'
            return modify_parameter(bts, 'riPerM', value)
        value = '1' if case.drx or case.ca_type == '2CC' or case.ca_type == '3CC' else '2'
        return modify_parameter(bts, 'riPerM', value)

    def get_ri_per_offset(self, bts, case):
        if case.domain in ['CAP']:
            value = '-1' if case.drx or case.ca_type == '2CC' or case.tm.upper() == '4X2' else '0'
            return modify_parameter(bts, 'riPerOffset', value)
        value = '-1' if case.drx or case.ca_type == '2CC' or case.ca_type == '3CC' else '0'
        return modify_parameter(bts, 'riPerOffset', value)

    def get_rrcConnectedUpperThresh(self, bts, case):
        if case.f_2664:
            return modify_parameter(bts, 'rrcConnectedUpperThresh', '80')
        else:
            return []

    def get_rrcConnectedLowerThresh(self, bts, case):
        if case.f_2664:
            return modify_parameter(bts, 'rrcConnectedLowerThresh', '10')
        else:
            return []

    def get_rootseqindex(self, bts, case):
        value = '300' if case.high_speed else '12'
        return modify_parameter(bts, 'rootSeqIndex', value)

    def get_rxCalibrationConfiguration(self, bts, case):
        value = 'noRxCalibration' if case.wimax else 'GuardPeriod'
        return modify_parameter(bts, 'rxCalibrationConfiguration', value)

    def _get_red_bw_max_rb_dl(self, bts, case, band):
        value = '75'  if band == '15' else '50'
        value = '100' if band == '20' else value
        value = '6' if band in ['1.4'] and bts.btstype == 'FDD' and case.domain in ['CAP'] else value
        value = str(int(band)*5) if band in ['3','5','10','15','20'] and bts.btstype == 'FDD' and case.domain in ['CAP'] else value
        return value

    def get_red_bw_max_rb_dl(self, bts, case):
        if case.domain in ['CAP']:
            return self._get_cell_param_with_band(bts, case, '_get_red_bw_max_rb_dl', 'redBwMaxRbDl')
        else:
            return []

    def _get_red_bw_max_rb_ul(self, bts, case, band):
        value = '75' if band == '15' else '50'
        value = '100' if band == '20' else value
        value = '6' if cqiPerNp in ['1.4'] and bts.btstype == 'FDD' and case.domain in ['CAP'] else value
        value = str(int(band)*5) if band in ['3','5','10','15','20'] and bts.btstype == 'FDD' and case.domain in ['CAP'] else value
        return value

    def get_red_bw_max_rb_ul(self, bts, case):
        return self._get_cell_param_with_band(bts, case, '_get_red_bw_max_rb_ul', 'redBwMaxRbUl') if case.domain in ['CAP'] else []


    def get_scell_activation_method(self, bts, case):
        if case.domain in ['CAP']:
            value = 'nonGBRBufferBasedStepWise' if case.ca_type == '3CC' else 'nonGBRBufferBased'
            return modify_parameter(bts, 'sCellActivationMethod', value)
        else:
            return []

    def get_srs_activation(self, bts, case):
        if case.domain in ['CAP']:
            value = 'true' if bts.btstype == 'TDD' else 'false'
            return modify_parameter(bts, 'srsActivation', value)
        else:
            return []

    def get_srs_bw_conf(self, bts, case):
        return modify_parameter(bts, 'srsBwConf', '2bw')

    def get_srs_on_two_symup_pts(self, bts, case):
        value = 'false' if case.ssf in [3, 4] else 'true'
        return modify_parameter(bts, 'srsOnTwoSymUpPts', value)

    def get_srs_subfr_conf(self, bts, case):
        if case.domain == 'CPK':
            value = 'sc0'
        if case.wimax:
            value = 'sc4'
        if case.domain == 'VOLTE' or case.domain == 'MR':
            value = 'sc4' if case.uldl in [1] else 'sc1'
        if case.domain in ['CAP']:
            value = 'sc4' if case.has_cap_volte and case.uldl in [1] else 'sc0'
        return modify_parameter(bts, 'srsSubfrConf', value)

    def get_srsSimAckNack(self, bts, case):
        if case.wimax:
            return modify_parameter(bts, 'srsSimAckNack', 'true')
        else:
            return []

    def get_tac(self, bts, case):
        if case.case_type == 'MIX_MR':
            return modify_parameter(bts, 'tac', bts.work_tac)
        elif case.has_cap_volte and case.domain in ['CAP']:
            return modify_parameter(bts, 'tac', '1800')
        else:
            return []

    def get_tdd_frame_conf(self, bts, case):
        return modify_parameter(bts, 'tddFrameConf', case.uldl)

    def get_tdd_spec_subf_conf(self, bts, case):
        return modify_parameter(bts, 'tddSpecSubfConf', case.ssf)

    def get_threshold1(self, bts, case):
        result = []
        if case.domain in ['MR']:
            if case.is_handover:
                result = modify_parameter(bts, 'threshold1', '90')
        return result

    def get_threshold2InterFreq(self, bts, case):
        result = []
        if case.domain in ['MR'] and case.is_handover and case.is_df:
            result = modify_parameter(bts, 'threshold2InterFreq', '56')
        return result

    def get_threshold2a(self, bts, case):
        result = []
        if case.domain in ['MR'] and case.is_handover and case.is_df:
            result = modify_parameter(bts, 'threshold2a', '60')
        return result

    def get_ul_combination_mode(self, bts, case):
        value = 'MRC' if case.high_speed else 'IRC'
        return modify_parameter(bts, 'ulCombinationMode', value)

    def get_actUlpcMethod(self, bts, case):
        if case.domain in ['VOLTE']:
            if case.releaseno == 'TL16':
                return modify_parameter(bts, 'actUlpcMethod', 'PuschOLPucchOL')
        return []

    def get_actUlpcRachPwrCtrl(self, bts, case):
        if case.f_1235:
            return modify_parameter(bts, 'actUlpcRachPwrCtrl', 'true')
        return []

    def get_actULCAggr(self, bts, case):
        result = []
        if case.domain == 'VOLTE':
            if not case.ca_type:
                return modify_parameter(bts, 'actULCAggr', 'false')
        if case.ulca:
            return modify_parameter(bts, 'actULCAggr', 'UL_CA_without_smartSched')
        return result

    def get_uls_max_packet_agg(self, bts, case):
        value  = '1' if case.volte_one_way_delay else '3'
        return modify_parameter(bts, 'ulsMaxPacketAgg', value)

    def _remove_unneeded_channels(self, bts, case):
        from pet_xml import scfns
        tmstr = case.tm.upper().replace('TM', '')
        channels_list=get_mos(bts, 'CHANNEL')
        left_range = 4
        if tmstr in ['4X2', '4X2-4X2', '4X2-4X2-4X2']:
            left_range = 4
        elif tmstr in ['1', '1-1', '1-1-1']:
            left_range = 1
        elif case.tm in ['94X4', '4X4', 'TM4X2']:
            left_range = 4
        elif case.pipe == 2:
            left_range = 2
        removed_channels = []
        for channel in channels_list:
            antl_name = channel.xpath('.//scfns:p[@name="antlDN"]', namespaces=scfns)[0].text
            if not antl_name.split('/')[-1] in ['ANTL-'+str(x+1) for x in range(left_range)]:
                print 'Remove channel by antl: ', antl_name, channel.get('distName')
                print antl_name.split('/')[-1]
                removed_channels.append(channel.get('distName'))
        return ["delete||distName=%s" %(x) for x in removed_channels]

    def get_changes_for_pipe(self, bts, case):
        result = []
        tmstr = case.tm.upper().replace('TM', '')
        if case.pipe == 2 or tmstr in ['1', '1-1', '1-1-1',
                        '4X2', '4X2-4X2', '4X2-4X2-4X2', '94X4', '4X4']:
            if tmstr in ['4X2', '4X2-4X2', '4X2-4X2-4X2']:
                del_antl = bts.antls[4:]
            elif case.tm == '94X4':
                del_antl = []
                for k in [1,3,5,7]:
                    del_antl.append(bts.antls[k])
            elif tmstr in ['1', '1-M1', '1-1-1']:
                del_antl = bts.antls[1:]
            else:
                del_antl = bts.antls[2:]

            for antl in del_antl:
                if scf_has_node(bts, antl, 'additionalRxGain'):
                    result.append("delete||distName=%s children name=additionalRxGain" %(antl))
                if scf_has_node(bts, antl, 'ulDelay'):
                    # print antl, antl.split('/')[-1], antl.split('/')[-1].split('-')
                    if int (antl.split('/')[-1].split('-')[1]) > 4:
                        result.append("delete||distName=%s children name=ulDelay" %(antl))

            channels_list=get_mos(bts, 'CHANNEL')
            rxchanles = [x for x in channels_list if get_all_parameter_under_node(x, 'direction')[0].text == 'RX']
            txchanles = [x for x in channels_list if get_all_parameter_under_node(x, 'direction')[0].text == 'TX']
            rxchanles = sort_mos_by_distnames(rxchanles)
            txchanles = sort_mos_by_distnames(txchanles)
            indexrange = range(len(rxchanles)/len(bts.lcells))
            if tmstr in ['4X2', '4X2-4X2', '4X2-4X2-4X2']:
                indexrange = indexrange[4:]
            elif tmstr in ['1', '1-1', '1-1-1']:
                indexrange = indexrange[1:]
            elif case.tm in ['94X4', '4X4', 'TM4X2']:
                indexrange = range(8)[4:]
            elif case.pipe == 2:
                indexrange = indexrange[2:]

            result += self._remove_unneeded_channels(bts, case)
            # for cell in bts.lcells:
            #     cellname = cell.get('distName').split('/')[-1]
            #     rxchanles_cell = [x for x in rxchanles if cellname in x.get('distName')]
            #     txchanles_cell = [x for x in txchanles if cellname in x.get('distName')]
            #     print [x.get('distName') for x in rxchanles_cell]
            #     for i in range(len(rxchanles)):
            #         if i in indexrange:
            #             result.append("delete||distName=%s" %(rxchanles_cell[i].get('distName')))
            #             result.append("delete||distName=%s" %(txchanles_cell[i].get('distName')))

            for cell in bts.lcells:
                antlid_list = [int(x.text.strip()) for x in get_all_parameter_under_node(cell, 'antlId')]
                antlid_list.sort()
                if antlid_list:
                    if tmstr in ['4X2', '4X2-4X2', '4X2-4X2-4X2']:
                        for antiid in antlid_list[4:]:
                            result.append("delete||name=antlId && text=%s parent tag=item" %(antiid))
                    elif tmstr in ['1', '1-1', '1-1-1']:
                        for antiid in antlid_list[1:]:
                            result.append("delete||name=antlId && text=%s parent tag=item" %(antiid))
                    elif case.tm in ['94X4', '4X4', 'TM4X2']:
                        for i in [5,6,7,8]:
                            result.append("delete||name=antlId && text=%s parent tag=item" %(antlid_list[i-1]))
                    else:
                        for antiid in antlid_list[2:]:
                            result.append("delete||name=antlId && text=%s parent tag=item" %(antiid))
        return result

    def get_changes_for_beforming(self, bts, case):
        result = []
        if bts.rru_type == 'FZND':
            return result

        tmlist = case.tm.upper().replace('TM','').split('-')
        tmlist = tmlist * int(bts.cell_count/len(tmlist))
        print 'xxxxxxxxxxxxxxxxxxxxxx',tmlist,tmlist[0],case.case_type
        if len(tmlist) == 1:
            if tmlist[0] in ['1','2', '3','4', '4X2']:
                if case.case_type not in ['MIX_MR', 'VOLTE_CAP', 'VOLTE_PERM', 'VOLTE_MIX']:
                    # if scf_has_node(bts, bts.allcells[0].get('distName'), 'beamformingType', 'beamforming'):
                    if scf_has_node(bts, bts.allcells[0].get('distName'), 'beamformingType', ''):
                        result.append("delete||distName=%s iterchild name=beamformingType && text=beamforming parent tag=item" %(bts.allcells[0].get('distName')))
        else:
            need_delete = True
            cell_index = 0
            for tmmode in tmlist:
                if tmmode in ['1','2', '3','4', '4X2']:
                    cell = bts.allcells[cell_index]
                    if not case.case_type in ['MIX_MR', 'VOLTE_CAP', 'VOLTE_PERM']:
                        if scf_has_node(bts, cell.get('distName'), 'beamformingType', ''):
                            result.append("delete||distName=%s iterchild name=beamformingType && text=beamforming parent tag=item" %(cell.get('distName')))
                cell_index += 1
        return result

    def get_changes_for_csi_config_info(self, bts, case):
        result = []
        added_str = '''
        <list name="csiRsConfigInfo">
        <item>
        <p name="numOfCsiRsAntennaPorts">8</p>
        <p name="csiRsPwrOffset">0</p>
        <p name="csiRsResourceConf">rsc20</p>
        <p name="csiRsSubfrConf">14</p>
        </item>
        </list>
        '''
        tmstr = case.tm
        tmlist = tmstr.replace('TM', '').split('-')
        if bts.cell_count > len(tmlist):
            tmlist = tmlist * int(bts.cell_count/len(tmlist))
        for i in range(bts.cell_count):
            if tmlist[i] in ['9','98X4','94X4', '4X4']:
                if tmlist[i] in ['94X4', '4X4']:
                    added_str = added_str.replace('<p name="numOfCsiRsAntennaPorts">8</p>',
                                                  '<p name="numOfCsiRsAntennaPorts">4</p>')
                    added_str = added_str.replace('<p name="csiRsResourceConf">rsc20</p>',
                                                  '<p name="csiRsResourceConf">rsc9</p>')

                if case.releaseno in ['TL17', 'TRUNK', 'TL17SP', 'TL17A']:
                    result.append('add|%s|distName=%s' %(added_str, bts.allcells[i].get('distName')))
                else:
                    result.append('add|%s|distName=%s' %(added_str, bts.lncels[i]))
        if case.ca_type.upper() in ['2CC','3CC']:
            return []
        else:
            return result


    def get_subframe_share_required(self, bts, case):
        result = []
        if case.mbms and case.subfrpshare:
             return modify_parameter(bts, 'subfrPShareRequired', case.subfrpshare)
        return result

    def get_sync_sig_txmode(self, bts, case):
        if case.tm in ['1', '1-TM1', 'TM1-TM1']:
            return modify_parameter(bts, 'syncSigTxMode', 'SingleTx')
        else:
            return []


    def get_scf_params_change_list(self, bts, case):
        result = []
        palist = {}
        for param in self.pmlist:
            values = getattr(self, scf_parameters[param])(bts, case)
            result += values

        if bts.btstype == 'TDD':
            result += self.get_changes_for_pipe(bts, case)
        result += self.get_changes_for_beforming(bts, case)
        result += self.get_changes_for_csi_config_info(bts, case)
        result.sort()

        self.show_scf_change_list(result)
        print result
        return result

    def show_scf_change_list(self, result):
        result.sort()
        palist = []
        for value in result:
            if value.split('|')[0] <> 'delete':
                if 'LNCEL' in value:
                    cell = value.split('|distName=')[1].split()[0].split('/')[-1]
                    param = value.split('|distName=')[1].split()[-1].split('=')[-1]
                    pv = value.split('|distName=')[0].split('text=')[-1]
                else:
                    cell = 'eNB'
                    param = value.split()[-1].split('=')[-1]
                    if 'text=' in value:
                        pv = value.split('text=')[1].split('|')[0]
                    else:
                        pv = ''
                palist.append('%-20s' %(cell)+ '%-40s' %(param) + '%-20s' %(pv))
        for line in result:
            print line
        palist.sort()
        for line in palist:
            print line


    def generate_swconfig_file(self, bts, case):
        lines = [x.replace('\n', '') for x in open(bts_source_file(bts.bts_id, 'swconfig.txt')).readlines()]
        lines += [
                    '0x310001=0',
                    '0x310002=0',
                ]  #disable SW Fallback

        if case.case_type.upper() == 'LATENCY':
            lines = [
                    '0x3A0001=1',
                    '0x10041=5',
                    '0x310001=0',
                    '0x310002=0',
                    ]

        with open(bts_file(bts.bts_id, 'swconfig_new.txt'), 'w') as f:
            for line in lines:
                f.write(line + '\n')
