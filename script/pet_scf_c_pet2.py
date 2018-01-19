from petbase import *
from pet_scf_base_c import c_pet_scf_base, scf_parameters

mix_cap_scf_params = [
    'actAutoPucchAlloc',
    'actConvVoice',
    'actDLCAggr',
    'actDlsVoicePacketAgg',
    'actDrx',
    # 'actDrxDuringMeasGap',
    'actFastMimoSwitch',
    'actNbrForNonGbrBearers',
    'actSmartDrx',
    'actPdcpRohc',
    'actTmSwitch',
    'activatedMimoTM',
    # 'actUlSps',
    'actULCAggr',
    'actUlMuMimo',
    'actDlMuMimo',
    'actUlpcMethod',
    'actFlexScellSelect',
    'addAUeRrHo',
    'addAUeTcHo',
    'addNumDrbRadioReasHo',
    'addNumDrbTimeCriticalHo',
    'addNumQci1DrbRadioReasHo',
    'addNumQci1DrbTimeCriticalHo',
    'aPucchAddAUeRrHo',
    'aPucchAddAUeTcHo',
    'cellSrPeriod',
    'chBw',
    'cqiPerNp',
    'deltaPucchShift',
    'dlInterferenceSpatialMode',
    'dlMimoMode',
    'dlSectorBeamformingMode',
    'inactivityTimer',
    'ipAddrPrim',
    #'maxNrSymPdcch',
    'maxNumActDrb',
    'maxNumActUE',
    'maxNumCaConfUe',
    'maxNumCaConfUeDc',
    'maxNumQci1Drb',
    'maxNumRrc',
    'maxNumRrcEmergency',
    'maxNumUeDl',
    'maxNumUeDlDwPTS',
    'maxNumUeUl',
    'n1PucchAn',
    'nCqiRb',
    'nCqiDtx',
    'nSrsDtx',
    'pucchNAnCs',
    'prachFreqoff',
    # 'reportingIntervalPm',
    'riEnable',
    'riPerM',
    'riPerOffset',
    'srsActivation',
    'sCellActivationMethod',
    # 'srsBwConf',
    'srsOnTwoSymUpPts',
    'srsSubfrConf',
    'syncSigTxMode',
    'tac',
    'tddFrameConf',
    'tddSpecSubfConf',
    'ulsMaxPacketAgg',
]

pet2_scf_pms = {
    'actAutoPucchAlloc':             'get_auto_pucch_alloc',
    'actConvVoice':                  'get_act_conv_voice',
    'actNbrForNonGbrBearers':        'get_act_nbr_for_nongbr_bearers',
    'actUlMuMimo':                   'get_act_ul_mu_mimo',
    'actDlMuMimo':                   'get_act_dl_mu_mimo',
    'aPucchAddAUeRrHo' :             'get_apucch_add_aue_rrho',
    'aPucchAddAUeTcHo' :             'get_apucch_add_aue_tcho',
    'actFlexScellSelect':            'get_act_flex_scell_select',
    'actDrx':                        'get_act_drx',
    'actSmartDrx':                   'get_act_smart_drx',
    'addAUeRrHo':                    'get_aue_rr_ho',
    'addAUeTcHo':                    'get_aue_tc_ho',
    'aPucchMinNumEmergencySessions' :'get_apucch_minnum_eme_ses',
    'aPucchMinNumRrc' :              'get_apucch_minnum_rrc',
    'aPucchMinNumRrcNoDrb' :         'get_apucch_minnum_rrc_no_drb',
    'aPucchSrPeriodUpperLimit' :     'get_apucch_sr_period_upper_limit',
    'addNumDrbRadioReasHo':          'get_add_num_drb_radio_reasho',
    'addNumDrbTimeCriticalHo':       'get_add_num_drb_time_critical_ho',
    'addNumQci1DrbRadioReasHo':      'get_add_num_qci1_drb_radio_reasho',
    'addNumQci1DrbTimeCriticalHo':   'get_add_num_qci1_drb_time_critical_ho',
    'ipAddrPrim':                    'get_ip_addr_prim',
    'maxNumScells':                  'get_max_num_scell',
    'maxNumCaConfUe':                'get_max_num_ca_conf_ue',
    'maxNumQci1Drb' :                'get_max_num_qci1_drb',
    'nPucchF3Prbs':                  'get_npucch_f3_prbs',
    'prachFreqoff':                  'get_prach_freq_off',
    'nCqiRb':                        'get_n_cqi_rb',
    'nCqiDtx':                       'get_n_cqi_dtx',
    'nSrsDtx':                       'get_n_srs_dtx',
    'redBwMaxRbDl':                  'get_red_bw_max_rb_dl',
    'redBwMaxRbUl':                  'get_red_bw_max_rb_ul',
    'sCellActivationMethod':         'get_scell_activation_method',
    'tac':                           'get_tac',
}

from pet_xml import *

class c_pet_scf_c(c_pet_scf_base):
    def __init__(self, pmlist):
        self.pmlist = pmlist
        for pm in pet2_scf_pms:
            if not pm in scf_parameters.keys():
                scf_parameters[pm] = pet2_scf_pms[pm]

    def get_max_num_scell(self, bts, case):
        value = '2' if case.ca_type == '3CC' else '1'
        return modify_parameter(bts, 'maxNumScells', value)

    def get_npucch_f3_prbs(self, bts, case):
        value = '4' if case.ca_type == '3CC' else '0'
        return modify_parameter(bts, 'nPucchF3Prbs', value)

    def _get_red_bw_max_rb_dl(self, bts, case, band):
        value = '75' if band == '15' else '50'
        value = '100' if band == '20' else value
        return value

    def get_red_bw_max_rb_dl(self, bts, case):
        return self._get_cell_param_with_band(bts, case, '_get_red_bw_max_rb_dl', 'redBwMaxRbDl')

    def _get_red_bw_max_rb_ul(self, bts, case, band):
        value = '75' if band == '15' else '50'
        value = '100' if band == '20' else value
        return value

    def get_red_bw_max_rb_ul(self, bts, case):
        return self._get_cell_param_with_band(bts, case, '_get_red_bw_max_rb_ul', 'redBwMaxRbUl')

    def get_scell_activation_method(self, bts, case):
        value = 'nonGBRBufferBasedStepWise' if case.ca_type == '3CC' else 'nonGBRBufferBased'
        return modify_parameter(bts, 'sCellActivationMethod', value)

    def get_auto_pucch_alloc(self, bts, case):
        value = 'true' if case.f_1130 else 'false'
        return modify_parameter(bts, 'actAutoPucchAlloc', value)

    def get_act_conv_voice(self, bts, case):
        value = 'true'
        return modify_parameter(bts, 'actConvVoice', value)

    def get_apucch_add_aue_rrho(self, bts, case):
        if case.f_1130:
            return modify_parameter(bts, 'aPucchAddAUeRrHo', '0')
        else:
            return []

    def get_apucch_add_aue_tcho(self, bts, case):
        if case.f_1130:
            return modify_parameter(bts, 'aPucchAddAUeTcHo', '0')
        else:
            return []

    def get_apucch_minnum_eme_ses(self, bts, case):
        if case.f_1130:
            return modify_parameter(bts, 'aPucchMinNumEmergencySessions', '0')
        else:
            return []

    def get_apucch_minnum_rrc(self, bts, case):
        if case.f_1130:
            return modify_parameter(bts, 'aPucchMinNumRrc', '0')
        else:
            return []

    def get_apucch_minnum_rrc_no_drb(self, bts, case):
        if case.f_1130:
            return modify_parameter(bts, 'aPucchMinNumRrcNoDrb', '0')
        else:
            return []

    def get_apucch_sr_period_upper_limit(self, bts, case):
        if case.f_1130:
            return modify_parameter(bts, 'aPucchSrPeriodUpperLimit', '40')
        else:
            return []

    def _get_max_num_act_drb(self, bts, case, band):
        value = '400'
        if band in ['20'] and case.uldl == 1 and case.ssf == '7':
            value = '600' if case.ca_type in ['2CC', '3CC'] else '800'
        return str(int(value)*3)

    def get_max_num_act_drb(self, bts, case):
        return self._get_cell_param_with_band(bts, case, '_get_max_num_act_drb', 'maxNumActDrb')

    def _get_max_num_act_ue(self, bts, case, band):
        if (case.uldl == 1 and band in ['20','15'] and case.f_limit and not bts.airscale) or (
           case.uldl == 1 and band in ['20','15'] and case.fd_20ue and not bts.airscale):
            value = 800
        elif (case.uldl == 1 and band in ['20','15'] and not case.f_limit and not bts.airscale) or (
            case.uldl == 2 and band in ['20','15'] and case.f_limit and not bts.airscale) or (
            band in ['20'] and case.f_limit and bts.airscale) or (
            case.uldl == 2 and band in ['20','15'] and case.fd_20ue and not bts.airscale) or (
            case.uldl == 1 and band in ['20','15'] and not case.fd_20ue and not bts.airscale):
            value = 600
        elif band in ['10'] and case.f_limit and bts.airscale:
            value = 550
        else:
            value = 400
        return value

    def get_max_num_act_ue(self, bts, case):
        return self._get_cell_param_with_band(bts, case, '_get_max_num_act_ue', 'maxNumActUE')

    def _get_max_num_ue_dl(self, bts, case, band):
        value = '12' if band == '20' else '10'
        value = '20' if case.fd_20ue else value
        return value

    def get_max_num_ue_dl(self, bts, case):
        return self._get_cell_param_with_band(bts, case, '_get_max_num_ue_dl', 'maxNumUeDl')

    def get_max_num_ue_ul(self, bts, case):
        return self._get_cell_param_with_band(bts, case, '_get_max_num_ue_dl', 'maxNumUeUl')

    def _get_max_num_ue_dldwpts(self, bts, case, band):
        value = '8' if band == '20' else '7'
        value = '12' if case.fd_20ue else value
        return value

    def get_max_num_ue_dldwpts(self, bts, case):
        return self._get_cell_param_with_band(bts, case, '_get_max_num_ue_dldwpts', 'maxNumUeDlDwPTS')

    def get_cell_srperiod(self, bts, case):
        value = '40ms' if case.has_cap_volte else '80ms'
        return modify_parameter(bts, 'cellSrPeriod', value)

    def get_max_num_rrc(self, bts, case):
        return self._get_cell_param_with_band(bts, case, '_get_max_num_act_ue', 'maxNumRrc')

    def get_max_num_rrc_emergency(self, bts, case):
        return self._get_cell_param_with_band(bts, case, '_get_max_num_act_ue', 'maxNumRrcEmergency')

    def _get_max_num_qci1_drb(self, bts, case, band):
        if band == '10':
            value = '300' if case.uldl == 1 else '150'
        if band in ['15', '20']:
            value = '400' if case.uldl == 1 else '200'
        return value


    def get_max_num_qci1_drb(self, bts, case):
        return self._get_cell_param_with_band(bts, case, '_get_max_num_qci1_drb', 'maxNumQci1Drb')

    def get_srs_subfr_conf(self, bts, case):
        value = 'sc4' if case.has_cap_volte and case.uldl in [1] else 'sc0'
        return modify_parameter(bts, 'srsSubfrConf', value)

    def get_act_smart_drx(self, bts, case):
        value= 'true'if case.smartdrx else 'false'
        return modify_parameter(bts, 'actSmartDrx', value)

    def get_act_drx(self, bts, case):
        value= 'true'if case.smartdrx or case.drx else 'false'
        return modify_parameter(bts, 'actDrx', value)


    def get_act_nbr_for_nongbr_bearers(self, bts, case):
        if case.f_limit or case.fd_20ue:
            return modify_parameter(bts, 'actNbrForNonGbrBearers', 'false')
        else:
            return []

    def get_act_ul_mu_mimo(self, bts, case):
        if case.f_limit or case.fd_20ue:
            return modify_parameter(bts, 'actUlMuMimo', 'false')
        else:
            return []

    def get_act_dl_mu_mimo(self, bts, case):
        if case.f_limit or case.fd_20ue:
            return modify_parameter(bts, 'actDlMuMimo', 'false')
        else:
            return []

    def get_ri_perm(self, bts, case):
        value = '1' if case.drx or case.ca_type == '2CC' or case.tm.upper() == '4X2'else '2'
        return modify_parameter(bts, 'riPerM', value)

    def get_ri_per_offset(self, bts, case):
        value = '-1' if case.drx or case.ca_type == '2CC' or case.tm.upper() == '4X2' else '0'
        return modify_parameter(bts, 'riPerOffset', value)

    def get_act_flex_scell_select(self, bts, case):
        value = 'true' if case.ca_type.strip() else 'false'
        return modify_parameter(bts, 'actFlexScellSelect', value)

    def get_aue_rr_ho(self, bts, case):
        value = 0
        return modify_parameter(bts, 'addAUeRrHo', value)

    def get_aue_tc_ho(self, bts, case):
        value = 0
        return modify_parameter(bts, 'addAUeTcHo', value)

    def get_add_num_qci1_drb_radio_reasho(self, bts, case):
        value = 0
        return modify_parameter(bts, 'addNumQci1DrbRadioReasHo', value)

    def get_add_num_qci1_drb_time_critical_ho(self, bts, case):
        value = 0
        return modify_parameter(bts, 'addNumQci1DrbTimeCriticalHo', value)

    def get_add_num_drb_radio_reasho(self, bts, case):
        value = 0
        return modify_parameter(bts, 'addNumDrbRadioReasHo', value)

    def get_add_num_drb_time_critical_ho(self, bts, case):
        value = 0
        return modify_parameter(bts, 'addNumDrbTimeCriticalHo', value)

    def get_max_num_ca_conf_ue(self, bts, case):
        value = '100' if case.case_type in ['MIX_CAP'] else '50'
        return modify_parameter(bts, 'maxNumCaConfUe', value)

    def get_prach_freq_off(self, bts, case):
        if case.uldl == 1 and case.drx:
            value = 8
        elif case.uldl == 1 and case.drx:
            value = 7
        elif case.uldl == 2 and case.drx:
            value = 9
        elif case.uldl == 2 and not case.drx:
            value = 7
        else:
            return []
        return modify_parameter(bts, 'prachFreqoff', value)

    def get_n_cqi_rb(self, bts, case):
        if case.uldl == 1 and case.drx:
            value = 7
        elif case.uldl == 1 and not case.drx:
            value = 5
        elif case.uldl == 2 and case.drx:
            value = 9
        elif case.uldl == 2 and not case.drx:
            value = 5
        else:
            value = 7
        return modify_parameter(bts, 'nCqiRb', value)

    def get_n_cqi_dtx(self, bts, case):
        value = 0
        return modify_parameter(bts, 'nCqiDtx', value)

    def get_n_srs_dtx(self, bts, case):
        value = 0
        return modify_parameter(bts, 'nSrsDtx', value)

    def get_tac(self,bts,case):
        if case.has_cap_volte:
            value = 5888
            return modify_parameter(bts, 'tac', value)
        else:
            return []

    def get_ip_addr_prim(self,bts,case):
        if gv.env.use_catapult and case.ue_is_m678:
            value = '10.68.152.170'
            return modify_parameter(bts, 'ipAddrPrim', value)
        else:
            return []


