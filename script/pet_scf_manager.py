from petbase import *


class pet_scf_manager():

    def __init__(self, case, bts):
        self.pmchange_list = None
        self.changed_scf_file = None
        self.scf_version = None
        self.case = case
        self.bts  = bts
        prefix = '%s%s_' %(self.bts.role, self.bts.level)
        prefix = '' if prefix == 'MP_' else prefix.lower()
        if prefix:
            import copy
            self.case = copy.deepcopy(case)
            for attr in [x for x in dir(case) if x.startswith(prefix)]:
                setattr(self.case, attr.replace(prefix, ''), getattr(self.case, attr))

    def gene_change_list(self):
        from pet_scf_base_c import c_pet_scf_base as c_pet_scf
        c_scf = c_pet_scf(scf_param_map['%s_%s' %(self.bts.btstype, self.case.domain)])
        self.pmchange_list = c_scf.get_scf_params_change_list(self.bts, self.case)
        return self.pmchange_list

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


tput_scf_params = [
        'actDrx',
        'actRLFReportEval',
        'actFastMimoSwitch',
        'actModulationSchemeUL',
        'actTmSwitch',
        'cellSrPeriod',
        'actProactSchedBySrb',
        'actRLFReportEval',
        # 'actAutoPucchAlloc',
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
        'srsOnTwoSymUpPts',
        'srsSubfrConf',  #Follow the template, not changed
        'srsSimAckNack',
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


mr_sr_params = [
    'a3Offset',
    'a3TriggerQuantityHO',
    'a3OffsetRsrpInterFreq',
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
    'measQuantInterFreq',
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
    'threshold1',
    'threshold2InterFreq',
    'threshold2a',
    'ulCombinationMode',
    ]

traffic_model_sr_params = [
    'ipAddrPrim',
    'tac',
    ]

prfoa_sr_params = [
    ]

mix_cap_scf_params = [
    'actAutoPucchAlloc',
    'actConvVoice',
    'actDLCAggr',
    'actDlsVoicePacketAgg',
    'actDrx',
    'actDlMuMimo',
    # 'actDrxDuringMeasGap',
    'actEmerCallRedir',
    'actFastMimoSwitch',
    'actFlexScellSelect',
    'activatedMimoTM',
    'actIMSEmerSessR9',
    'actLbPucchReg',
    'actNbrForNonGbrBearers',
    'actSmartDrx',
    'actPdcpRohc',
    'actTmSwitch',
    # 'actUlSps',
    'actULCAggr',
    'actUlMuMimo',
    'actUlpcMethod',
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
    'countdownPucchCompr',
    'countdownPucchExp',
    'deltaPucchShift',
    'dlInterferenceSpatialMode',
    'dlMimoMode',
    'dlSectorBeamformingMode',
    'fourLayerMimoAvSpectralEff',
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
    'prachFreqOff',
    # 'reportingIntervalPm',
    'riEnable',
    'riPerM',
    'rrcConnectedUpperThresh',
    'rrcConnectedLowerThresh',
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


fdd_mix_cap_scf_params = [
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
    'actULCAggr',
    'actUlMuMimo',
    'actDlMuMimo',
    'actUlpcMethod',
    'actUciOnlyGrants',
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
    'dlChBw',
    'cqiPerNp',
    'deltaPucchShift',
    'dlMimoMode',
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
    'pucchNAnCs',
    'prachFreqOff',
    # 'reportingIntervalPm',
    'riEnable',
    'riPerM',
    'riPerOffset',
    'srsActivation',
    'sCellActivationMethod',
    'syncSigTxMode',
    'tac',
    'ulsMaxPacketAgg',
    'ulChBw',
]

fdd_tput_scf_params = [
        'actDrx',
        'actRLFReportEval',
        'actFastMimoSwitch',
        'actModulationSchemeUL',
        'cellSrPeriod',
        'actProactSchedBySrb',
        'actRLFReportEval',
        'actAutoPucchAlloc',
        'actULCAggr',
        'activatedMimoTM',
        'dlChBw',
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
        'prachCS',
        'prachConfIndex',
        'prachFreqOff',
        'reportingIntervalPm',
        'riEnable',
        'subfrPShareRequired',  #mbms parameter
        'syncSigTxMode',
        'riPerM',
        'riPerOffset',
        'maxNrSymPdcch',
        'n1PucchAn',
]


scf_param_map = {
    'TDD_CPK'       : tput_scf_params,
    'TDD_CAP'       : mix_cap_scf_params,
    'TDD_VOLTE'     : volte_scf_params,
    'TDD_MR'        : mr_sr_params,
    'TDD_TR'        : traffic_model_sr_params,
    'TDD_PRF'       : prfoa_sr_params,

    'FDD_CPK'       : fdd_tput_scf_params,
    'FDD_CAP'       : fdd_mix_cap_scf_params,
    'FDD_VOLTE'     : volte_scf_params,
    'FDD_MR'        : mr_sr_params,
    'FDD_TR'        : traffic_model_sr_params,
    'FDD_PRF'       : prfoa_sr_params,
}


def get_src_scf_version(case, bts, src_xml_file):
    directory_path = '/ffs/run' if bts.airscale else '/flash'
    from pet_bts import download_file_from_bts
    download_file_from_bts(bts.btsid, pathc(bts_file(bts.btsid, 'FileDirectory.xml')), 'FileDirectory.xml', directory_path)
    scf_version = 'SCFC' + etree.parse(bts_file(bts.btsid, 'FileDirectory.xml')).xpath('//fileElement[@name="SCFC"and@activeFlag="TRUE"]')[0].get('version')
    gv.logger.info('Myself found scf: ' + scf_version)
    return scf_version



def gene_changed_scf(case, bts):
    common_xml_operation(pathc(src_xml_file), pathc(bts_file(bts.btsid, scf_version)), self.get_accept_changes(case, bts))
    self.changed_scf_file = bts_file(bts.btsid, self.scf_version)


if __name__ == '__main__':

    gv.suite.log_directory = '/home/work/temp/cmp'
    gv.case.log_directory = '/home/work/temp/cmp'

    from pet_bts import read_bts_config
    bts = read_bts_config('1601')
    print bts
    # bts.btstype = "FDD"

    from pettool import get_case_config_new
    case = get_case_config_new('603309')
    gv.case.curr_case = case
    from petcasebase import re_organize_case
    re_organize_case()


    if bts.level == 'P': #Master 2 BTS
        src_xml_file = bts_file(bts.btsid, case.scf_file)
    else:
        src_xml_file = bts_file(bts.btsid, case.ms_scf_file)

    from pet_bts import pet_bts_read_scf_file
    pet_bts_read_scf_file(bts.btsid,  src_xml_file)


    # print "XXXXXXXXXX",case.tm
    scf_manager = pet_scf_manager(case, bts)
    scf_manager.gene_change_list()
    print "XXXXXXXX", scf_manager.pmchange_list
    # scf_manager.gene_changed_scf(case, bts)





