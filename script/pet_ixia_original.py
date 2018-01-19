# IxNetwork version: 8.01.1029.6
# time of scriptgen: 2016/11/17, 16:46
import sys, os
import time, re

sys.path.append('/home/work/tacase/ixialib')

from ixiatcl import IxiaTcl
from ixiahlt import IxiaHlt
from ixiangpf import IxiaNgpf
from ixiaerror import IxiaError

def load_config(filename):
    print 'os.path.basename(filename)=%s' %(os.path.basename(filename))
    print 'import module=%s' %(os.path.basename(filename).split('.')[0])
    import importlib
    sys.path.append(os.path.dirname(filename))
    return importlib.import_module(os.path.basename(filename).split('.')[0])

#print 'sys.argv[1]=%s' %(sys.argv[1])
ixiavar = load_config(sys.argv[1])

if os.name == 'nt':
	ixiatcl = IxiaTcl()
else:
	# unix dependencies
	tcl_dependencies = [
		'/home/user/ixia/ixos/lib',
		'/home/user/ixia/ixnet/IxTclProtocol',
		'/home/user/ixia/ixnet/IxTclNetwork'
	]
	ixiatcl = IxiaTcl(tcl_autopath=tcl_dependencies)

ixiahlt = IxiaHlt(ixiatcl)
ixiangpf = IxiaNgpf(ixiahlt)

def ixnHLT_endpointMatch(ixnHLT, ixnpattern_list, handle_type='HANDLE'):
	traffic_ep_ignore_list = [
		'^::ixNet::OBJ-/vport:\d+/protocols/mld/host:\d+$',
		'^::ixNet::OBJ-/vport:\d+/protocolStack/ethernet:[^/]+/ipEndpoint:[^/]+/range:[^/]+/ptpRangeOverIp:1$'
	]

	rval = []
	for pat in ixnpattern_list:
		if pat[ 0] != '^': pat = '^' + pat
		if pat[-1] != '$': pat = pat + '$'

		for path in set(x for x in ixnHLT if x.startswith(handle_type)):
			ixn_path = path.split(',')[1]
			parent_ixn_path = '/'.join(ixn_path.split('/')[:-1])
			parent_path = '%s,%s' % (handle_type, parent_ixn_path)

			parent_found = False
			if len(rval) > 0 and parent_path in ixnHLT and parent_path in rval:
				parent_found = True

			if not parent_found and re.match(pat, ixn_path) and len(ixnHLT[path]) > 0:
				if not any(re.match(x, ixnHLT[path]) for x in traffic_ep_ignore_list):
					rval.append(ixnHLT[path])

	return rval

# ----------------------------------------------------------------
# Configuration procedure

try:
	ixnHLT_logger('')
except (NameError,):
	def ixnHLT_logger(msg):
		print(msg)

try:
	ixnHLT_errorHandler('', {})
except (NameError,):
	def ixnHLT_errorHandler(cmd, retval):
		global ixiatcl
		err = ixiatcl.tcl_error_info()
		log = retval['log']
		additional_info = '> command: %s\n> tcl errorInfo: %s\n> log: %s' % (cmd, err, log)
		raise IxiaError(IxiaError.COMMAND_FAIL, additional_info)

def ixnHLT_Scriptgen_Configure(ixiahlt, ixnHLT):
	ixiatcl = ixiahlt.ixiatcl
	# //vport
	ixnHLT_logger('interface_config://vport:<1>...')
	_result_ = ixiahlt.interface_config(
		mode='config',
		port_handle=ixnHLT['PORT-HANDLE,//vport:<1>'],
		transmit_clock_source='external',
		tx_gap_control_mode='average',
		transmit_mode='advanced',
		port_rx_mode='capture_and_measure',
		flow_control_directed_addr='0180.c200.0001',
		enable_flow_control='1',
		internal_ppm_adjust='0',
		additional_fcoe_stat_1='fcoe_invalid_delimiter',
		ignore_link='0',
		enable_data_center_shared_stats='0',
		additional_fcoe_stat_2='fcoe_invalid_frames',
		data_integrity='1',
		intf_mode='ethernet',
		speed='ether100',
		duplex='full',
		autonegotiation=1,
		auto_detect_instrumentation_type='floating',
		phy_mode='copper',
		master_slave_mode='auto',
		arp_refresh_interval='60'
	)
	# Check status
	if _result_['status'] != IxiaHlt.SUCCESS:
		ixnHLT_errorHandler('interface_config', _result_)
	# The last configure command did not scriptgen the following attributes:
	# [//vport:<1>]
	# n kBool -isConnected 'True'
	# n kString -ixnClientVersion '8.01.1029.6'
	# n kString -connectionInfo 'chassis="10.106.210.87" card="2" port="2" portip="10.0.2.2"'
	# n kEnumValue -stateDetail 'idle'
	# n kInteger -actualSpeed '1000'
	# n kBool -isDirectConfigModeEnabled 'False'
	# n kInteger -internalId '1'
	# n kString -licenses 'obsolete, do not use'
	# n kString -connectionStatus '10.106.210.87:02:02 '
	# n kEnumValue -state 'up'
	# n kBool -isVMPort 'False'
	# n kString -assignedTo '10.106.210.87:2:2'
	# n kObjref -connectedTo '$ixNetSG_ref(19)'
	# n kBool -isPullOnly 'False'
	# n kBool -isAvailable 'True'
	# n kString -ixosChassisVersion 'ixos 8.01.1213.10 ea-patch1'
	# n kString -ixnChassisVersion '8.01.1029.6'
	# n kBool -isMapped 'True'
	# n kString -name '1/2/1 #1'

	try:
		ixnHLT['HANDLE,//vport:<1>'] = _result_['interface_handle']
		config_handles = ixnHLT.setdefault('VPORT-CONFIG-HANDLES,//vport:<1>,interface_config', [])
		config_handles.append(_result_['interface_handle'])
	except:
		pass
	ixnHLT_logger('COMPLETED: interface_config')

	# //vport
	ixnHLT_logger('interface_config://vport:<2>...')
	_result_ = ixiahlt.interface_config(
		mode='config',
		port_handle=ixnHLT['PORT-HANDLE,//vport:<2>'],
		transmit_clock_source='external',
		tx_gap_control_mode='average',
		transmit_mode='advanced',
		port_rx_mode='capture_and_measure',
		flow_control_directed_addr='0180.c200.0001',
		enable_flow_control='1',
		internal_ppm_adjust='0',
		additional_fcoe_stat_1='fcoe_invalid_delimiter',
		ignore_link='0',
		enable_data_center_shared_stats='0',
		additional_fcoe_stat_2='fcoe_invalid_frames',
		data_integrity='1',
		intf_mode='ethernet',
		speed='ether100',
		duplex='full',
		autonegotiation=1,
		auto_detect_instrumentation_type='floating',
		phy_mode='copper',
		master_slave_mode='auto',
		arp_refresh_interval='60'
	)
	# Check status
	if _result_['status'] != IxiaHlt.SUCCESS:
		ixnHLT_errorHandler('interface_config', _result_)
	# The last configure command did not scriptgen the following attributes:
	# [//vport:<2>]
	# n kBool -isConnected 'True'
	# n kString -ixnClientVersion '8.01.1029.6'
	# n kString -connectionInfo 'chassis="10.106.210.87" card="2" port="1" portip="10.0.2.1"'
	# n kEnumValue -stateDetail 'idle'
	# n kInteger -actualSpeed '1000'
	# n kBool -isDirectConfigModeEnabled 'False'
	# n kInteger -internalId '2'
	# n kString -licenses 'obsolete, do not use'
	# n kString -connectionStatus '10.106.210.87:02:01 '
	# n kEnumValue -state 'up'
	# n kBool -isVMPort 'False'
	# n kString -assignedTo '10.106.210.87:2:1'
	# n kObjref -connectedTo '$ixNetSG_ref(18)'
	# n kBool -isPullOnly 'False'
	# n kBool -isAvailable 'True'
	# n kString -ixosChassisVersion 'ixos 8.01.1213.10 ea-patch1'
	# n kString -ixnChassisVersion '8.01.1029.6'
	# n kBool -isMapped 'True'
	# n kString -name '1/2/2'

	try:
		ixnHLT['HANDLE,//vport:<2>'] = _result_['interface_handle']
		config_handles = ixnHLT.setdefault('VPORT-CONFIG-HANDLES,//vport:<2>,interface_config', [])
		config_handles.append(_result_['interface_handle'])
	except:
		pass
	ixnHLT_logger('COMPLETED: interface_config')

	# //vport/l1Config/rxFilters/filterPalette
	ixnHLT_logger('uds_config://vport:<1>/l1Config/rxFilters/filterPalette...')
	_result_ = ixiahlt.uds_config(
		port_handle=ixnHLT['PORT-HANDLE,//vport:<1>'],
		uds1='1',
		uds1_SA='any',
		uds1_DA='any',
		uds1_error='errAnyFrame',
		uds1_framesize='any',
		uds1_framesize_from='0',
		uds1_framesize_to='0',
		uds1_pattern='any',
		uds2='1',
		uds2_SA='any',
		uds2_DA='any',
		uds2_error='errAnyFrame',
		uds2_framesize='any',
		uds2_framesize_from='0',
		uds2_framesize_to='0',
		uds2_pattern='any',
		uds3='1',
		uds3_SA='any',
		uds3_DA='any',
		uds3_error='errAnyFrame',
		uds3_framesize='any',
		uds3_framesize_from='0',
		uds3_framesize_to='0',
		uds3_pattern='any',
		uds4='1',
		uds4_SA='any',
		uds4_DA='any',
		uds4_error='errAnyFrame',
		uds4_framesize='any',
		uds4_framesize_from='0',
		uds4_framesize_to='0',
		uds4_pattern='any',
		uds5='1',
		uds5_SA='any',
		uds5_DA='any',
		uds5_error='errAnyFrame',
		uds5_framesize='any',
		uds5_framesize_from='0',
		uds5_framesize_to='0',
		uds5_pattern='any',
		uds6='1',
		uds6_SA='any',
		uds6_DA='any',
		uds6_error='errAnyFrame',
		uds6_framesize='any',
		uds6_framesize_from='0',
		uds6_framesize_to='0',
		uds6_pattern='any'
	)
	# Check status
	if _result_['status'] != IxiaHlt.SUCCESS:
		ixnHLT_errorHandler('uds_config', _result_)
	# The last configure command did not scriptgen the following attributes:
	# [//vport:<1>/l1Config/rxFilters/filterPalette]
	# n kString -sourceAddress1Mask '00:00:00:00:00:00'
	# n kString -destinationAddress1Mask '00:00:00:00:00:00'
	# n kString -sourceAddress2 '00:00:00:00:00:00'
	# n kEnumValue -pattern2OffsetType 'fromStartOfFrame'
	# n kInteger -pattern2Offset '20'
	# n kString -sourceAddress2Mask '00:00:00:00:00:00'
	# n kString -destinationAddress2 '00:00:00:00:00:00'
	# n kString -destinationAddress1 '00:00:00:00:00:00'
	# n kString -sourceAddress1 '00:00:00:00:00:00'
	# n kString -pattern1 '0'
	# n kString -destinationAddress2Mask '00:00:00:00:00:00'
	# n kInteger -pattern1Offset '20'
	# n kString -pattern2 '0'
	# n kString -pattern2Mask '0'
	# n kEnumValue -pattern1OffsetType 'fromStartOfFrame'
	# n kString -pattern1Mask '0'

	ixnHLT_logger('COMPLETED: uds_config')

	# //vport/l1Config/rxFilters/filterPalette
	ixnHLT_logger('uds_config://vport:<2>/l1Config/rxFilters/filterPalette...')
	_result_ = ixiahlt.uds_config(
		port_handle=ixnHLT['PORT-HANDLE,//vport:<2>'],
		uds1='1',
		uds1_SA='any',
		uds1_DA='any',
		uds1_error='errAnyFrame',
		uds1_framesize='any',
		uds1_framesize_from='0',
		uds1_framesize_to='0',
		uds1_pattern='any',
		uds2='1',
		uds2_SA='any',
		uds2_DA='any',
		uds2_error='errAnyFrame',
		uds2_framesize='any',
		uds2_framesize_from='0',
		uds2_framesize_to='0',
		uds2_pattern='any',
		uds3='1',
		uds3_SA='any',
		uds3_DA='any',
		uds3_error='errAnyFrame',
		uds3_framesize='any',
		uds3_framesize_from='0',
		uds3_framesize_to='0',
		uds3_pattern='any',
		uds4='1',
		uds4_SA='any',
		uds4_DA='any',
		uds4_error='errAnyFrame',
		uds4_framesize='any',
		uds4_framesize_from='0',
		uds4_framesize_to='0',
		uds4_pattern='any',
		uds5='1',
		uds5_SA='any',
		uds5_DA='any',
		uds5_error='errAnyFrame',
		uds5_framesize='any',
		uds5_framesize_from='0',
		uds5_framesize_to='0',
		uds5_pattern='any',
		uds6='1',
		uds6_SA='any',
		uds6_DA='any',
		uds6_error='errAnyFrame',
		uds6_framesize='any',
		uds6_framesize_from='0',
		uds6_framesize_to='0',
		uds6_pattern='any'
	)
	# Check status
	if _result_['status'] != IxiaHlt.SUCCESS:
		ixnHLT_errorHandler('uds_config', _result_)
	# The last configure command did not scriptgen the following attributes:
	# [//vport:<2>/l1Config/rxFilters/filterPalette]
	# n kString -sourceAddress1Mask '00:00:00:00:00:00'
	# n kString -destinationAddress1Mask '00:00:00:00:00:00'
	# n kString -sourceAddress2 '00:00:00:00:00:00'
	# n kEnumValue -pattern2OffsetType 'fromStartOfFrame'
	# n kInteger -pattern2Offset '20'
	# n kString -sourceAddress2Mask '00:00:00:00:00:00'
	# n kString -destinationAddress2 '00:00:00:00:00:00'
	# n kString -destinationAddress1 '00:00:00:00:00:00'
	# n kString -sourceAddress1 '00:00:00:00:00:00'
	# n kString -pattern1 '0'
	# n kString -destinationAddress2Mask '00:00:00:00:00:00'
	# n kInteger -pattern1Offset '20'
	# n kString -pattern2 '0'
	# n kString -pattern2Mask '0'
	# n kEnumValue -pattern1OffsetType 'fromStartOfFrame'
	# n kString -pattern1Mask '0'

	ixnHLT_logger('COMPLETED: uds_config')

	# //vport/l1Config/rxFilters/filterPalette
	ixnHLT_logger('uds_filter_pallette_config://vport:<1>/l1Config/rxFilters/filterPalette...')
	_result_ = ixiahlt.uds_filter_pallette_config(
		port_handle=ixnHLT['PORT-HANDLE,//vport:<1>'],
		DA1='00:00:00:00:00:00',
		DA2='00:00:00:00:00:00',
		DA_mask1='00:00:00:00:00:00',
		DA_mask2='00:00:00:00:00:00',
		pattern1='0',
		pattern2='0',
		pattern_mask1='0',
		pattern_mask2='0',
		pattern_offset1='20',
		pattern_offset2='20',
		SA1='00:00:00:00:00:00',
		SA2='00:00:00:00:00:00',
		SA_mask1='00:00:00:00:00:00',
		SA_mask2='00:00:00:00:00:00',
		pattern_offset_type1='startOfFrame',
		pattern_offset_type2='startOfFrame'
	)
	# Check status
	if _result_['status'] != IxiaHlt.SUCCESS:
		ixnHLT_errorHandler('uds_filter_pallette_config', _result_)

	ixnHLT_logger('COMPLETED: uds_filter_pallette_config')

	# //vport/capture/filterPallette
	ixnHLT_logger('packet_config_filter://vport:<1>/capture/filterPallette...')
	_result_ = ixiahlt.packet_config_filter(
		port_handle=ixnHLT['PORT-HANDLE,//vport:<1>'],
		pattern_offset_type1='startOfFrame',
		pattern_offset_type2='startOfFrame',
		DA1='00 00 00 00 00 00',
		DA2='00 00 00 00 00 00',
		DA_mask1='00 00 00 00 00 00',
		DA_mask2='00 00 00 00 00 00',
		pattern1='00',
		pattern2='00',
		pattern_mask1='00',
		pattern_mask2='00',
		pattern_offset1='0',
		pattern_offset2='0',
		SA1='00 00 00 00 00 00',
		SA2='00 00 00 00 00 00',
		SA_mask1='00 00 00 00 00 00',
		SA_mask2='00 00 00 00 00 00'
	)
	# Check status
	if _result_['status'] != IxiaHlt.SUCCESS:
		ixnHLT_errorHandler('packet_config_filter', _result_)

	ixnHLT_logger('COMPLETED: packet_config_filter')

	# //vport/l1Config/rxFilters/filterPalette
	ixnHLT_logger('uds_filter_pallette_config://vport:<2>/l1Config/rxFilters/filterPalette...')
	_result_ = ixiahlt.uds_filter_pallette_config(
		port_handle=ixnHLT['PORT-HANDLE,//vport:<2>'],
		DA1='00:00:00:00:00:00',
		DA2='00:00:00:00:00:00',
		DA_mask1='00:00:00:00:00:00',
		DA_mask2='00:00:00:00:00:00',
		pattern1='0',
		pattern2='0',
		pattern_mask1='0',
		pattern_mask2='0',
		pattern_offset1='20',
		pattern_offset2='20',
		SA1='00:00:00:00:00:00',
		SA2='00:00:00:00:00:00',
		SA_mask1='00:00:00:00:00:00',
		SA_mask2='00:00:00:00:00:00',
		pattern_offset_type1='startOfFrame',
		pattern_offset_type2='startOfFrame'
	)
	# Check status
	if _result_['status'] != IxiaHlt.SUCCESS:
		ixnHLT_errorHandler('uds_filter_pallette_config', _result_)

	ixnHLT_logger('COMPLETED: uds_filter_pallette_config')

	# //vport/capture
	ixnHLT_logger('packet_config_buffers://vport:<1>/capture...')
	_result_ = ixiahlt.packet_config_buffers(
		port_handle=ixnHLT['PORT-HANDLE,//vport:<1>'],
		data_plane_capture_enable='0',
		control_plane_capture_enable='1',
		control_plane_filter_pcap='',
		control_plane_trigger_pcap=''
	)
	# Check status
	if _result_['status'] != IxiaHlt.SUCCESS:
		ixnHLT_errorHandler('packet_config_buffers', _result_)
	# The last configure command did not scriptgen the following attributes:
	# [//vport:<1>/capture]
	# n kEnumValue -controlBufferBehaviour 'bufferLiveNonCircular'
	# n kBool -isDataCaptureRunning 'False'
	# n kArray -decodeAsNetworkProtocols ''
	# n kEnumValue -dataReceiveTimestamp 'chassisUtcTime'
	# n kBool -isCaptureRunning 'False'
	# n kInteger -controlSliceSize '0'
	# n kEnumValue -beforeTriggerFilter 'captureBeforeTriggerNone'
	# n kDouble -triggerPosition '1'
	# n kString -displayFiltersDataCapture ''
	# n kArray -decodeAsTransportProtocols ''
	# n kString -controlActiveCapture ''
	# n kEnumValue -continuousFilters 'captureContinuousFilter'
	# n kString -controlDecodeAsCurrentFilter ''
	# n kString -dataDecodeAsCurrentFilter ''
	# n kString -dataCaptures ''
	# n kInteger -sliceSize '0'
	# n kEnumValue -afterTriggerFilter 'captureAfterTriggerFilter'
	# n kArray -decodeAsLinkProtocols ''
	# n kString -controlCaptures ''
	# n kString -displayFiltersControlCapture ''
	# n kEnumValue -controlInterfaceType 'anyInterface'
	# n kBool -isControlCaptureRunning 'False'
	# n kEnumValue -captureMode 'captureTriggerMode'
	# n kString -dataActiveCapture ''
	# n kInteger -controlBufferSize '60'

	for handle in ixiatcl.convert_tcl_list(_result_['port_handle']):
		ixnHLT['HANDLE,//vport:<1>/capture'] = handle
		config_handles = ixnHLT.setdefault('VPORT-CONFIG-HANDLES,//vport:<1>,packet_config_buffers', [])
		config_handles.append(handle)
	ixnHLT_logger('COMPLETED: packet_config_buffers')

	# //vport/capture/trigger
	ixnHLT_logger('packet_config_triggers://vport:<1>/capture/trigger...')
	_result_ = ixiahlt.packet_config_triggers(
		port_handle=ixnHLT['PORT-HANDLE,//vport:<1>']
	)
	# Check status
	if _result_['status'] != IxiaHlt.SUCCESS:
		ixnHLT_errorHandler('packet_config_triggers', _result_)
	# The last configure command did not scriptgen the following attributes:
	# [//vport:<1>/capture/trigger]
	# n kEnumValue -captureTriggerError 'errAnyFrame'
	# n kBool -captureTriggerFrameSizeEnable 'False'
	# n kInteger -captureTriggerFrameSizeFrom '12'
	# n kEnumValue -captureTriggerDA 'anyAddr'
	# n kString -captureTriggerExpressionString ''
	# n kEnumValue -captureTriggerPattern 'anyPattern'
	# n kEnumValue -captureTriggerSA 'anyAddr'
	# n kInteger -captureTriggerFrameSizeTo '12'

	ixnHLT_logger('COMPLETED: packet_config_triggers')

	# The following objects had no attributes that were scriptgenned:
	# n //globals/interfaces
	# n //statistics/measurementMode
	# n //vport:<1>/l1Config/ethernet/fcoe
	# n //vport:<2>/l1Config/ethernet/fcoe
	# n //vport:<2>/capture/trigger
	# n //vport:<2>/capture/filter
	# n //vport:<2>/capture/filterPallette
	# n //globals/testInspector
	# n //globals/preferences
	# n //reporter
	# n //reporter/testParameters
	# n //reporter/generate
	# n //reporter/saveResults
	# n //statistics/rawData
	# n //statistics/autoRefresh
	# n //impairment
	# n //impairment/defaultProfile
	# n //impairment/defaultProfile/checksums
	# n //impairment/defaultProfile/rxRateLimit
	# n //impairment/defaultProfile/drop
	# n //impairment/defaultProfile/reorder
	# n //impairment/defaultProfile/duplicate
	# n //impairment/defaultProfile/bitError
	# n //impairment/defaultProfile/delay
	# n //impairment/defaultProfile/delayVariation
	# n //impairment/defaultProfile/customDelayVariation
	# n //quickTest
	# n //quickTest/globals
	# n //vport:<1>/l1Config/ethernet/oam
	# n //vport:<1>/l1Config/OAM
	# n //vport:<1>/protocols
	# n //vport:<1>/protocols/openFlow
	# n //vport:<1>/protocols/openFlow/hostTopologyLearnedInformation/switchHostRangeLearnedInfoTriggerAttributes
	# n //vport:<1>/protocolStack/options
	# n //vport:<2>/l1Config/ethernet/oam
	# n //vport:<2>/l1Config/OAM
	# n //vport:<2>/protocols
	# n //vport:<2>/protocols/openFlow
	# n //vport:<2>/protocols/openFlow/hostTopologyLearnedInformation/switchHostRangeLearnedInfoTriggerAttributes
	# n //vport:<2>/protocolStack/options
	# n //globals/testInspector/statistic:<1>
	# n //globals/testInspector/statistic:<2>
	# n //globals/testInspector/statistic:<3>
	# n //globals/testInspector/statistic:<4>
	# n //globals/testInspector/statistic:<5>
	# n //globals/testInspector/statistic:<6>
	# n //globals/testInspector/statistic:<7>
	# n //globals/testInspector/statistic:<8>
	# n {//statistics/rawData/statistic:"Tx Frames"}
	# n {//statistics/rawData/statistic:"Rx Frames"}
	# n {//statistics/rawData/statistic:"Frames Delta"}
	# n {//statistics/rawData/statistic:"Tx Frame Rate"}
	# n {//statistics/rawData/statistic:"Rx Frames Rate"}
	# n {//statistics/rawData/statistic:"Avg Latency (us)"}
	# n {//statistics/rawData/statistic:"Min Latency (us)"}
	# n {//statistics/rawData/statistic:"Max Latency (us)"}
	# n {//statistics/rawData/statistic:"Minimum Delay Variation"}
	# n {//statistics/rawData/statistic:"Maximum Delay Variation"}
	# n {//statistics/rawData/statistic:"Avg Delay Variation"}
	# n {//statistics/rawData/statistic:"Reordered Packets"}
	# n {//statistics/rawData/statistic:"Lost Packets"}
	# end of list

def ixnCPF_Scriptgen_Configure(ixiangpf, ixnHLT):
	ixiatcl = ixiangpf.ixiahlt.ixiatcl

	_result_ = ixiangpf.topology_config(
		topology_name      = """T 1/2/1""",
		port_handle        = [ixnHLT['PORT-HANDLE,//vport:<1>']],
	)
	if _result_['status'] != IxiaHlt.SUCCESS:
		ixnHLT_errorHandler('topology_config', _result_)

	topology_1_handle = _result_['topology_handle']
	ixnHLT['HANDLE,//topology:<1>'] = topology_1_handle

	_result_ = ixiangpf.topology_config(
		topology_handle              = topology_1_handle,
		device_group_name            = """Range 1/2/1 2 False""",
		device_group_multiplier      = ixiavar.pppoe_client_ue_number,
		device_group_enabled         = "1",
	)
	if _result_['status'] != IxiaHlt.SUCCESS:
		ixnHLT_errorHandler('topology_config', _result_)

	deviceGroup_1_handle = _result_['device_group_handle']
	ixnHLT['HANDLE,//topology:<1>/deviceGroup:<1>'] = deviceGroup_1_handle

	_result_ = ixiangpf.multivalue_config(
		pattern                = "counter",
		counter_start          = ixiavar.ethernet_mac,
		counter_step           = "00.00.00.00.00.01",
		counter_direction      = "increment",
		nest_step              = '%s' % ("00.00.01.00.00.00"),
		nest_owner             = '%s' % (topology_1_handle),
		nest_enabled           = '%s' % ("1"),
	)
	if _result_['status'] != IxiaHlt.SUCCESS:
		ixnHLT_errorHandler('multivalue_config', _result_)

	multivalue_1_handle = _result_['multivalue_handle']

	_result_ = ixiangpf.interface_config(
		protocol_name           = """Ethernet 1""",
		protocol_handle         = deviceGroup_1_handle,
		mtu                     = "1500",
		src_mac_addr            = multivalue_1_handle,
		vlan                    = "0",
		vlan_id_count           = '%s' % ("0"),
		use_vpn_parameters      = "0",
		site_id                 = "0",
	)
	if _result_['status'] != IxiaHlt.SUCCESS:
		ixnHLT_errorHandler('interface_config', _result_)

	# n The attribute: useVlans with the value: False is not supported by scriptgen.
	# n The attribute: stackedLayers with the value: {} is not supported by scriptgen.
	# n The attribute: connectedVia with the value: {} is not supported by scriptgen.
	# n Node: pbbEVpnParameter is not supported for scriptgen.
	ethernet_1_handle = _result_['ethernet_handle']
	ixnHLT['HANDLE,//topology:<1>/deviceGroup:<1>/ethernet:<1>'] = ethernet_1_handle

	_result_ = ixiangpf.multivalue_config(
		pattern                 = "single_value",
		single_value            = "10",
		nest_step               = '%s' % ("1"),
		nest_owner              = '%s' % (topology_1_handle),
		nest_enabled            = '%s' % ("0"),
		overlay_value           = '%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s' % ("5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5"),
		overlay_value_step      = '%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s' % ("5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5"),
		overlay_index           = '%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s' % ("1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "22", "23", "24", "25", "26", "27", "28", "29", "30", "31", "32", "33", "34", "35", "36", "37", "38", "39", "40", "41", "42", "43", "44", "45", "46", "47", "48", "49", "50", "51", "52", "53", "54", "55", "56", "57", "58", "59", "60", "61", "62", "63", "64", "65", "66", "67", "68", "69", "70", "71", "72", "73", "74", "75", "76", "77", "78", "79", "80", "81", "82", "83", "84", "85", "86", "87", "88", "89", "90", "91", "92", "93", "94", "95", "96", "97", "98", "99", "100"),
		overlay_index_step      = '%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s' % ("0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"),
		overlay_count           = '%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s' % ("1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1"),
	)
	if _result_['status'] != IxiaHlt.SUCCESS:
		ixnHLT_errorHandler('multivalue_config', _result_)

	multivalue_2_handle = _result_['multivalue_handle']

	_result_ = ixiangpf.multivalue_config(
		pattern                 = "single_value",
		single_value            = "10",
		nest_step               = '%s' % ("1"),
		nest_owner              = '%s' % (topology_1_handle),
		nest_enabled            = '%s' % ("0"),
		overlay_value           = '%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s' % ("5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5"),
		overlay_value_step      = '%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s' % ("5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5"),
		overlay_index           = '%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s' % ("1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "22", "23", "24", "25", "26", "27", "28", "29", "30", "31", "32", "33", "34", "35", "36", "37", "38", "39", "40", "41", "42", "43", "44", "45", "46", "47", "48", "49", "50", "51", "52", "53", "54", "55", "56", "57", "58", "59", "60", "61", "62", "63", "64", "65", "66", "67", "68", "69", "70", "71", "72", "73", "74", "75", "76", "77", "78", "79", "80", "81", "82", "83", "84", "85", "86", "87", "88", "89", "90", "91", "92", "93", "94", "95", "96", "97", "98", "99", "100"),
		overlay_index_step      = '%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s' % ("0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"),
		overlay_count           = '%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s' % ("1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1"),
	)
	if _result_['status'] != IxiaHlt.SUCCESS:
		ixnHLT_errorHandler('multivalue_config', _result_)

	multivalue_3_handle = _result_['multivalue_handle']

	_result_ = ixiangpf.multivalue_config(
		pattern                 = "single_value",
		single_value            = "10",
		nest_step               = '%s' % ("1"),
		nest_owner              = '%s' % (topology_1_handle),
		nest_enabled            = '%s' % ("0"),
		overlay_value           = '%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s' % ("5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5"),
		overlay_value_step      = '%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s' % ("5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5"),
		overlay_index           = '%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s' % ("1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "22", "23", "24", "25", "26", "27", "28", "29", "30", "31", "32", "33", "34", "35", "36", "37", "38", "39", "40", "41", "42", "43", "44", "45", "46", "47", "48", "49", "50", "51", "52", "53", "54", "55", "56", "57", "58", "59", "60", "61", "62", "63", "64", "65", "66", "67", "68", "69", "70", "71", "72", "73", "74", "75", "76", "77", "78", "79", "80", "81", "82", "83", "84", "85", "86", "87", "88", "89", "90", "91", "92", "93", "94", "95", "96", "97", "98", "99", "100"),
		overlay_index_step      = '%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s' % ("0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"),
		overlay_count           = '%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s' % ("1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1"),
	)
	if _result_['status'] != IxiaHlt.SUCCESS:
		ixnHLT_errorHandler('multivalue_config', _result_)

	multivalue_4_handle = _result_['multivalue_handle']

	_result_ = ixiangpf.multivalue_config(
		pattern                 = "single_value",
		single_value            = "20",
		nest_step               = '%s' % ("1"),
		nest_owner              = '%s' % (topology_1_handle),
		nest_enabled            = '%s' % ("0"),
		overlay_value           = '%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s' % ("10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10"),
		overlay_value_step      = '%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s' % ("10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10"),
		overlay_index           = '%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s' % ("1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "22", "23", "24", "25", "26", "27", "28", "29", "30", "31", "32", "33", "34", "35", "36", "37", "38", "39", "40", "41", "42", "43", "44", "45", "46", "47", "48", "49", "50", "51", "52", "53", "54", "55", "56", "57", "58", "59", "60", "61", "62", "63", "64", "65", "66", "67", "68", "69", "70", "71", "72", "73", "74", "75", "76", "77", "78", "79", "80", "81", "82", "83", "84", "85", "86", "87", "88", "89", "90", "91", "92", "93", "94", "95", "96", "97", "98", "99", "100"),
		overlay_index_step      = '%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s' % ("0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"),
		overlay_count           = '%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s' % ("1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1"),
	)
	if _result_['status'] != IxiaHlt.SUCCESS:
		ixnHLT_errorHandler('multivalue_config', _result_)

	multivalue_5_handle = _result_['multivalue_handle']

	_result_ = ixiangpf.multivalue_config(
		pattern                 = "single_value",
		single_value            = "3",
		nest_step               = '%s' % ("1"),
		nest_owner              = '%s' % (topology_1_handle),
		nest_enabled            = '%s' % ("0"),
		overlay_value           = '%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s' % ("10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10"),
		overlay_value_step      = '%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s' % ("10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10"),
		overlay_index           = '%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s' % ("1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "22", "23", "24", "25", "26", "27", "28", "29", "30", "31", "32", "33", "34", "35", "36", "37", "38", "39", "40", "41", "42", "43", "44", "45", "46", "47", "48", "49", "50", "51", "52", "53", "54", "55", "56", "57", "58", "59", "60", "61", "62", "63", "64", "65", "66", "67", "68", "69", "70", "71", "72", "73", "74", "75", "76", "77", "78", "79", "80", "81", "82", "83", "84", "85", "86", "87", "88", "89", "90", "91", "92", "93", "94", "95", "96", "97", "98", "99", "100"),
		overlay_index_step      = '%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s' % ("0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"),
		overlay_count           = '%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s' % ("1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1"),
	)
	if _result_['status'] != IxiaHlt.SUCCESS:
		ixnHLT_errorHandler('multivalue_config', _result_)

	multivalue_6_handle = _result_['multivalue_handle']

	_result_ = ixiangpf.multivalue_config(
		pattern                 = "single_value",
		single_value            = "user",
		overlay_value           = '%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s' % ("tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500"),
		overlay_value_step      = '%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s' % ("tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500"),
		overlay_index           = '%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s' % ("1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "22", "23", "24", "25", "26", "27", "28", "29", "30", "31", "32", "33", "34", "35", "36", "37", "38", "39", "40", "41", "42", "43", "44", "45", "46", "47", "48", "49", "50", "51", "52", "53", "54", "55", "56", "57", "58", "59", "60", "61", "62", "63", "64", "65", "66", "67", "68", "69", "70", "71", "72", "73", "74", "75", "76", "77", "78", "79", "80", "81", "82", "83", "84", "85", "86", "87", "88", "89", "90", "91", "92", "93", "94", "95", "96", "97", "98", "99", "100"),
		overlay_index_step      = '%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s' % ("0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"),
		overlay_count           = '%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s' % ("1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1"),
	)
	if _result_['status'] != IxiaHlt.SUCCESS:
		ixnHLT_errorHandler('multivalue_config', _result_)

	multivalue_7_handle = _result_['multivalue_handle']

	_result_ = ixiangpf.multivalue_config(
		pattern                 = "single_value",
		single_value            = "secret",
		overlay_value           = '%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s' % ("tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500"),
		overlay_value_step      = '%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s' % ("tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500", "tm500"),
		overlay_index           = '%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s' % ("1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "22", "23", "24", "25", "26", "27", "28", "29", "30", "31", "32", "33", "34", "35", "36", "37", "38", "39", "40", "41", "42", "43", "44", "45", "46", "47", "48", "49", "50", "51", "52", "53", "54", "55", "56", "57", "58", "59", "60", "61", "62", "63", "64", "65", "66", "67", "68", "69", "70", "71", "72", "73", "74", "75", "76", "77", "78", "79", "80", "81", "82", "83", "84", "85", "86", "87", "88", "89", "90", "91", "92", "93", "94", "95", "96", "97", "98", "99", "100"),
		overlay_index_step      = '%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s' % ("0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"),
		overlay_count           = '%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s' % ("1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1"),
	)
	if _result_['status'] != IxiaHlt.SUCCESS:
		ixnHLT_errorHandler('multivalue_config', _result_)

	multivalue_8_handle = _result_['multivalue_handle']

	_result_ = ixiangpf.multivalue_config(
		pattern                 = "single_value",
		single_value            = "5",
		nest_step               = '%s' % ("1"),
		nest_owner              = '%s' % (topology_1_handle),
		nest_enabled            = '%s' % ("0"),
		overlay_value           = '%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s' % ("10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10"),
		overlay_value_step      = '%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s' % ("10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10"),
		overlay_index           = '%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s' % ("1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "22", "23", "24", "25", "26", "27", "28", "29", "30", "31", "32", "33", "34", "35", "36", "37", "38", "39", "40", "41", "42", "43", "44", "45", "46", "47", "48", "49", "50", "51", "52", "53", "54", "55", "56", "57", "58", "59", "60", "61", "62", "63", "64", "65", "66", "67", "68", "69", "70", "71", "72", "73", "74", "75", "76", "77", "78", "79", "80", "81", "82", "83", "84", "85", "86", "87", "88", "89", "90", "91", "92", "93", "94", "95", "96", "97", "98", "99", "100"),
		overlay_index_step      = '%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s' % ("0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"),
		overlay_count           = '%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s' % ("1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1"),
	)
	if _result_['status'] != IxiaHlt.SUCCESS:
		ixnHLT_errorHandler('multivalue_config', _result_)

	multivalue_9_handle = _result_['multivalue_handle']

	_result_ = ixiangpf.multivalue_config(
		pattern                 = "single_value",
		single_value            = "5",
		nest_step               = '%s' % ("1"),
		nest_owner              = '%s' % (topology_1_handle),
		nest_enabled            = '%s' % ("0"),
		overlay_value           = '%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s' % ("10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10"),
		overlay_value_step      = '%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s' % ("10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10", "10"),
		overlay_index           = '%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s' % ("1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "22", "23", "24", "25", "26", "27", "28", "29", "30", "31", "32", "33", "34", "35", "36", "37", "38", "39", "40", "41", "42", "43", "44", "45", "46", "47", "48", "49", "50", "51", "52", "53", "54", "55", "56", "57", "58", "59", "60", "61", "62", "63", "64", "65", "66", "67", "68", "69", "70", "71", "72", "73", "74", "75", "76", "77", "78", "79", "80", "81", "82", "83", "84", "85", "86", "87", "88", "89", "90", "91", "92", "93", "94", "95", "96", "97", "98", "99", "100"),
		overlay_index_step      = '%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s' % ("0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"),
		overlay_count           = '%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s' % ("1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1"),
	)
	if _result_['status'] != IxiaHlt.SUCCESS:
		ixnHLT_errorHandler('multivalue_config', _result_)

	multivalue_10_handle = _result_['multivalue_handle']

	_result_ = ixiangpf.multivalue_config(
		pattern                 = "single_value",
		single_value            = "10",
		nest_step               = '%s' % ("1"),
		nest_owner              = '%s' % (topology_1_handle),
		nest_enabled            = '%s' % ("0"),
		overlay_value           = '%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s' % ("5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5"),
		overlay_value_step      = '%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s' % ("5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5"),
		overlay_index           = '%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s' % ("1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "22", "23", "24", "25", "26", "27", "28", "29", "30", "31", "32", "33", "34", "35", "36", "37", "38", "39", "40", "41", "42", "43", "44", "45", "46", "47", "48", "49", "50", "51", "52", "53", "54", "55", "56", "57", "58", "59", "60", "61", "62", "63", "64", "65", "66", "67", "68", "69", "70", "71", "72", "73", "74", "75", "76", "77", "78", "79", "80", "81", "82", "83", "84", "85", "86", "87", "88", "89", "90", "91", "92", "93", "94", "95", "96", "97", "98", "99", "100"),
		overlay_index_step      = '%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s' % ("0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"),
		overlay_count           = '%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s' % ("1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1"),
	)
	if _result_['status'] != IxiaHlt.SUCCESS:
		ixnHLT_errorHandler('multivalue_config', _result_)

	multivalue_11_handle = _result_['multivalue_handle']

	_result_ = ixiangpf.multivalue_config(
		pattern                 = "single_value",
		single_value            = "10",
		nest_step               = '%s' % ("1"),
		nest_owner              = '%s' % (topology_1_handle),
		nest_enabled            = '%s' % ("0"),
		overlay_value           = '%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s' % ("5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5"),
		overlay_value_step      = '%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s' % ("5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5", "5"),
		overlay_index           = '%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s' % ("1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "22", "23", "24", "25", "26", "27", "28", "29", "30", "31", "32", "33", "34", "35", "36", "37", "38", "39", "40", "41", "42", "43", "44", "45", "46", "47", "48", "49", "50", "51", "52", "53", "54", "55", "56", "57", "58", "59", "60", "61", "62", "63", "64", "65", "66", "67", "68", "69", "70", "71", "72", "73", "74", "75", "76", "77", "78", "79", "80", "81", "82", "83", "84", "85", "86", "87", "88", "89", "90", "91", "92", "93", "94", "95", "96", "97", "98", "99", "100"),
		overlay_index_step      = '%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s' % ("0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"),
		overlay_count           = '%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s' % ("1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1"),
	)
	if _result_['status'] != IxiaHlt.SUCCESS:
		ixnHLT_errorHandler('multivalue_config', _result_)

	multivalue_12_handle = _result_['multivalue_handle']

	_result_ = ixiangpf.multivalue_config(
		pattern                 = "counter",
		counter_start           = "0:11:11:11:0:0:0:1",
		counter_step            = "0:0:0:1:0:0:0:0",
		counter_direction       = "increment",
		nest_step               = '%s' % ("00:01:00:00:00:00:00:00"),
		nest_owner              = '%s' % (topology_1_handle),
		nest_enabled            = '%s' % ("1"),
		overlay_value           = '%s' % ("00:00:00:00:00:00:00:00"),
		overlay_value_step      = '%s' % ("00:00:00:00:00:00:00:00"),
		overlay_index           = '%s' % ("1"),
		overlay_index_step      = '%s' % ("1"),
		overlay_count           = '%s' % ("100"),
	)
	if _result_['status'] != IxiaHlt.SUCCESS:
		ixnHLT_errorHandler('multivalue_config', _result_)

	multivalue_13_handle = _result_['multivalue_handle']

	_result_ = ixiangpf.multivalue_config(
		pattern                 = "counter",
		counter_start           = "1.1.1.1",
		counter_step            = "0.0.0.1",
		counter_direction       = "increment",
		nest_step               = '%s' % ("0.1.0.0"),
		nest_owner              = '%s' % (topology_1_handle),
		nest_enabled            = '%s' % ("1"),
		overlay_value           = '%s' % ("2.2.2.2"),
		overlay_value_step      = '%s' % ("0.0.0.0"),
		overlay_index           = '%s' % ("1"),
		overlay_index_step      = '%s' % ("1"),
		overlay_count           = '%s' % ("100"),
	)
	if _result_['status'] != IxiaHlt.SUCCESS:
		ixnHLT_errorHandler('multivalue_config', _result_)

	multivalue_14_handle = _result_['multivalue_handle']

	_result_ = ixiangpf.multivalue_config(
		pattern             = "string",
		string_pattern      = ixiavar.pppoe_client_service_name,
	)
	if _result_['status'] != IxiaHlt.SUCCESS:
		ixnHLT_errorHandler('multivalue_config', _result_)

	multivalue_15_handle = _result_['multivalue_handle']

	_result_ = ixiangpf.multivalue_config(
		pattern                = "counter",
		counter_start          = "1",
		counter_step           = "1",
		counter_direction      = "increment",
		nest_step              = '%s' % ("10000"),
		nest_owner             = '%s' % (topology_1_handle),
		nest_enabled           = '%s' % ("1"),
	)
	if _result_['status'] != IxiaHlt.SUCCESS:
		ixnHLT_errorHandler('multivalue_config', _result_)

	multivalue_16_handle = _result_['multivalue_handle']

	_result_ = ixiangpf.pppox_config(
		port_role                            = "access",
		handle                               = ethernet_1_handle,
		protocol_name                        = """PPPoX Client 1""",
		unlimited_redial_attempts            = "0",
		enable_mru_negotiation               = "1",
		desired_mru_rate                     = "1492",
		max_payload                          = "1700",
		enable_max_payload                   = "0",
		client_ipv6_ncp_configuration        = "learned",
		client_ipv4_ncp_configuration        = "learned",
		lcp_enable_accm                      = "0",
		lcp_accm                             = "ffffffff",
		ac_select_mode                       = "first_responding",
		auth_req_timeout                     = multivalue_2_handle,
		config_req_timeout                   = multivalue_3_handle,
		echo_req                             = "0",
		echo_rsp                             = "1",
		ip_cp                                = "ipv4_cp",
		ipcp_req_timeout                     = multivalue_4_handle,
		max_auth_req                         = multivalue_5_handle,
		max_padi_req                         = multivalue_9_handle,
		max_padr_req                         = multivalue_10_handle,
		max_terminate_req                    = multivalue_6_handle,
		padi_req_timeout                     = multivalue_11_handle,
		padr_req_timeout                     = multivalue_12_handle,
		password                             = "password",
		chap_secret                          = multivalue_8_handle,
		username                             = "user",
		chap_name                            = multivalue_7_handle,
		mode                                 = "add",
		auth_mode                            = "chap",
		echo_req_interval                    = "10",
		max_configure_req                    = "3",
		max_ipcp_req                         = "3",
		actual_rate_downstream               = "10",
		actual_rate_upstream                 = "10",
		data_link                            = "ethernet",
		enable_domain_group_map              = "0",
		enable_client_signal_iwf             = "0",
		enable_client_signal_loop_char       = "0",
		enable_client_signal_loop_encap      = "0",
		enable_client_signal_loop_id         = "0",
		intermediate_agent_encap1            = "untagged_eth",
		intermediate_agent_encap2            = "na",
		ppp_local_iid                        = multivalue_13_handle,
		ppp_local_ip                         = multivalue_14_handle,
		redial                               = "1",
		redial_max                           = "20",
		redial_timeout                       = "10",
		service_name                         = multivalue_15_handle,
		service_type                         = "name",
		client_dns_options                   = "disable_extension",
		client_dns_primary_address           = "8.8.8.8",
		client_dns_secondary_address         = "9.9.9.9",
		client_netmask_options               = "disable_extension",
		client_netmask                       = "255.0.0.0",
		client_wins_options                  = "disable_extension",
		client_wins_primary_address          = "8.8.8.8",
		client_wins_secondary_address        = "9.9.9.9",
		lcp_max_failure                      = "5",
		lcp_start_delay                      = "0",
		enable_host_uniq                     = "false",
		host_uniq                            = multivalue_16_handle,
		multiplier                           = "1",
	)
	if _result_['status'] != IxiaHlt.SUCCESS:
		ixnHLT_errorHandler('pppox_config', _result_)

	# n The attribute: stackedLayers with the value: {} is not supported by scriptgen.
	# n The attribute: connectedVia with the value: {} is not supported by scriptgen.
	pppoxclient_1_handle = _result_['pppox_client_handle']
	ixnHLT['HANDLE,//topology:<1>/deviceGroup:<1>/ethernet:<1>/pppoxclient:<1>'] = pppoxclient_1_handle

	_result_ = ixiangpf.topology_config(
		topology_name      = """Topology 2""",
		port_handle        = [ixnHLT['PORT-HANDLE,//vport:<2>']],
	)
	if _result_['status'] != IxiaHlt.SUCCESS:
		ixnHLT_errorHandler('topology_config', _result_)

	topology_2_handle = _result_['topology_handle']
	ixnHLT['HANDLE,//topology:<2>'] = topology_2_handle

	_result_ = ixiangpf.topology_config(
		topology_handle              = topology_2_handle,
		device_group_name            = """Device Group 2""",
		device_group_multiplier      = "5",
		device_group_enabled         = "1",
	)
	if _result_['status'] != IxiaHlt.SUCCESS:
		ixnHLT_errorHandler('topology_config', _result_)

	deviceGroup_2_handle = _result_['device_group_handle']
	ixnHLT['HANDLE,//topology:<2>/deviceGroup:<1>'] = deviceGroup_2_handle

	_result_ = ixiangpf.multivalue_config(
		pattern                = "counter",
		counter_start          = "00.12.01.00.00.01",
		counter_step           = "00.00.00.00.00.01",
		counter_direction      = "increment",
		nest_step              = '%s' % ("00.00.01.00.00.00"),
		nest_owner             = '%s' % (topology_2_handle),
		nest_enabled           = '%s' % ("1"),
	)
	if _result_['status'] != IxiaHlt.SUCCESS:
		ixnHLT_errorHandler('multivalue_config', _result_)

	multivalue_17_handle = _result_['multivalue_handle']

	_result_ = ixiangpf.interface_config(
		protocol_name                = """Ethernet 2""",
		protocol_handle              = deviceGroup_2_handle,
		mtu                          = "1500",
		src_mac_addr                 = multivalue_17_handle,
		vlan                         = "0",
		vlan_id                      = '%s' % ("1"),
		vlan_id_step                 = '%s' % ("0"),
		vlan_id_count                = '%s' % ("1"),
		vlan_tpid                    = '%s' % ("0x8100"),
		vlan_user_priority           = '%s' % ("0"),
		vlan_user_priority_step      = '%s' % ("0"),
		use_vpn_parameters           = "0",
		site_id                      = "0",
	)
	if _result_['status'] != IxiaHlt.SUCCESS:
		ixnHLT_errorHandler('interface_config', _result_)

	# n The attribute: useVlans with the value: False is not supported by scriptgen.
	# n The attribute: stackedLayers with the value: {} is not supported by scriptgen.
	# n The attribute: connectedVia with the value: {} is not supported by scriptgen.
	# n Node: pbbEVpnParameter is not supported for scriptgen.
	ethernet_2_handle = _result_['ethernet_handle']
	ixnHLT['HANDLE,//topology:<2>/deviceGroup:<1>/ethernet:<1>'] = ethernet_2_handle

	_result_ = ixiangpf.multivalue_config(
		pattern                = "counter",
		counter_start          = ixiavar.ipv4_address,
		counter_step           = "0.0.0.1",
		counter_direction      = "increment",
		nest_step              = '%s' % ("0.1.0.0"),
		nest_owner             = '%s' % (topology_2_handle),
		nest_enabled           = '%s' % ("1"),
	)
	if _result_['status'] != IxiaHlt.SUCCESS:
		ixnHLT_errorHandler('multivalue_config', _result_)

	multivalue_18_handle = _result_['multivalue_handle']

	_result_ = ixiangpf.interface_config(
		protocol_name                     = """IPv4 1""",
		protocol_handle                   = ethernet_2_handle,
		ipv4_resolve_gateway              = "1",
		ipv4_manual_gateway_mac           = "00.00.00.00.00.01",
		ipv4_manual_gateway_mac_step      = "00.00.00.00.00.00",
		gateway                           =  ixiavar.ipv4_gateway_ip,
		gateway_step                      = "0.0.0.0",
		intf_ip_addr                      = multivalue_18_handle,
		netmask                           = "255.255.255.0",
	)
	if _result_['status'] != IxiaHlt.SUCCESS:
		ixnHLT_errorHandler('interface_config', _result_)

	# n The attribute: stackedLayers with the value: {} is not supported by scriptgen.
	# n The attribute: connectedVia with the value: {} is not supported by scriptgen.
	ipv4_1_handle = _result_['ipv4_handle']
	ixnHLT['HANDLE,//topology:<2>/deviceGroup:<1>/ethernet:<1>/ipv4:<1>'] = ipv4_1_handle

	# n Node: /globals/topology/ipv6Autoconfiguration does not have global settings.
	# n Node: /globals/topology/ipv6 does not have global settings.
	# n Node: /globals/topology/bfdRouter does not have global settings.
	# n Node: /globals/topology/ospfv2Router does not have global settings.
	# n Node: /globals/topology/ospfv3Router does not have global settings.
	# n Node: /globals/topology/pimRouter does not have global settings.
	# n Node: /globals/topology/rsvpteIf does not have global settings.
	# n Node: /globals/topology/rsvpteLsps does not have global settings.
	# n Node: /globals/topology/isisFabricPathRouter does not have global settings.
	# n Node: /globals/topology/isisL3Router does not have global settings.
	# n Node: /globals/topology/isisSpbRouter does not have global settings.
	# n Node: /globals/topology/isisTrillRouter does not have global settings.
	# n Node: /globals/topology/igmpHost does not have global settings.
	# n Node: /globals/topology/mldHost does not have global settings.
	# n Node: /globals/topology/ldpBasicRouterV6 does not have global settings.
	# n Node: /globals/topology/ldpBasicRouter does not have global settings.
	# n Node: /globals/topology/ldpTargetedRouter does not have global settings.
	# n Node: /globals/topology/ldpTargetedRouterV6 does not have global settings.
	# n Node: /globals/topology/msrpListener does not have global settings.
	# n Node: /globals/topology/msrpTalker does not have global settings.
	# n Node: /globals/topology/bgpIpv4Peer does not have global settings.
	# n Node: /globals/topology/bgpIpv6Peer does not have global settings.
	# n Node: /globals/topology/igmpQuerier does not have global settings.
	# n Node: /globals/topology/mldQuerier does not have global settings.
	# n Node: /globals/topology/dhcpv4client does not have global settings.
	# n Node: /globals/topology/dhcpv6client does not have global settings.
	# n Node: /globals/topology/dhcpv4server does not have global settings.
	# n Node: /globals/topology/dhcpv6server does not have global settings.
	# n Node: /globals/topology/dhcpv4relayAgent does not have global settings.
	# n Node: /globals/topology/lightweightDhcpv6relayAgent does not have global settings.
	# n Node: /globals/topology/dhcpv6relayAgent does not have global settings.
	# n Node: /globals/topology/pppoxserver does not have global settings.
	# n Node: /globals/topology/lac does not have global settings.
	# n Node: /globals/topology/lns does not have global settings.
	# n Node: /globals/topology/vxlan does not have global settings.
	# n Node: /globals/topology/greoipv4 does not have global settings.
	# n Node: /globals/topology/greoipv6 does not have global settings.
	# n Node: /globals/topology/ptp does not have global settings.
	# n Node: /globals/topology/ancp does not have global settings.
	# n Node: /globals/topology/lacp does not have global settings.
	# n Node: /globals/topology/staticLag does not have global settings.

	_result_ = ixiangpf.interface_config(
		protocol_handle                    = "/globals",
		arp_on_linkup                      = "0",
		single_arp_per_gateway             = "1",
		ipv4_send_arp_rate                 = "200",
		ipv4_send_arp_interval             = "1000",
		ipv4_send_arp_max_outstanding      = "400",
		ipv4_send_arp_scale_mode           = "port",
		ipv4_attempt_enabled               = "0",
		ipv4_attempt_rate                  = "200",
		ipv4_attempt_interval              = "1000",
		ipv4_attempt_scale_mode            = "port",
		ipv4_diconnect_enabled             = "0",
		ipv4_disconnect_rate               = "200",
		ipv4_disconnect_interval           = "1000",
		ipv4_disconnect_scale_mode         = "port",
		ipv4_re_send_arp_on_link_up        = "true",
	)
	if _result_['status'] != IxiaHlt.SUCCESS:
		ixnHLT_errorHandler('interface_config', _result_)


	_result_ = ixiangpf.interface_config(
		protocol_handle                     = "/globals",
		ethernet_attempt_enabled            = "0",
		ethernet_attempt_rate               = "200",
		ethernet_attempt_interval           = "1000",
		ethernet_attempt_scale_mode         = "port",
		ethernet_diconnect_enabled          = "0",
		ethernet_disconnect_rate            = "200",
		ethernet_disconnect_interval        = "1000",
		ethernet_disconnect_scale_mode      = "port",
	)
	if _result_['status'] != IxiaHlt.SUCCESS:
		ixnHLT_errorHandler('interface_config', _result_)


	_result_ = ixiangpf.multivalue_config(
		pattern                = "distributed",
		distributed_value      = "1",
	)
	if _result_['status'] != IxiaHlt.SUCCESS:
		ixnHLT_errorHandler('multivalue_config', _result_)

	multivalue_19_handle = _result_['multivalue_handle']

	_result_ = ixiangpf.multivalue_config(
		pattern                = "distributed",
		distributed_value      = "10",
	)
	if _result_['status'] != IxiaHlt.SUCCESS:
		ixnHLT_errorHandler('multivalue_config', _result_)

	multivalue_20_handle = _result_['multivalue_handle']

	_result_ = ixiangpf.multivalue_config(
		pattern                = "distributed",
		distributed_value      = "10",
	)
	if _result_['status'] != IxiaHlt.SUCCESS:
		ixnHLT_errorHandler('multivalue_config', _result_)

	multivalue_21_handle = _result_['multivalue_handle']

	_result_ = ixiangpf.pppox_config(
		port_role                                = "access",
		handle                                   = "/globals",
		mode                                     = "add",
		ipv6_global_address_mode                 = "icmpv6",
		ra_timeout                               = "30",
		create_interfaces                        = "0",
		attempt_rate                             = "100",
		attempt_max_outstanding                  = "1000",
		attempt_interval                         = "1000",
		attempt_enabled                          = "1",
		attempt_scale_mode                       = "port",
		disconnect_rate                          = "100",
		disconnect_max_outstanding               = "1000",
		disconnect_interval                      = "1000",
		disconnect_enabled                       = "1",
		disconnect_scale_mode                    = "port",
		enable_session_lifetime                  = "0",
		min_lifetime                             = multivalue_19_handle,
		max_lifetime                             = multivalue_20_handle,
		enable_session_lifetime_restart          = "0",
		max_session_lifetime_restarts            = multivalue_21_handle,
		unlimited_session_lifetime_restarts      = "0",
	)
	if _result_['status'] != IxiaHlt.SUCCESS:
		ixnHLT_errorHandler('pppox_config', _result_)


	# n Node: /globals/topology/ipv6Autoconfiguration does not have global settings.
	# n Node: /globals/topology/ipv6 does not have global settings.
	# n Node: /globals/topology/bfdRouter does not have global settings.
	# n Node: /globals/topology/ospfv2Router does not have global settings.
	# n Node: /globals/topology/ospfv3Router does not have global settings.
	# n Node: /globals/topology/pimRouter does not have global settings.
	# n Node: /globals/topology/rsvpteIf does not have global settings.
	# n Node: /globals/topology/rsvpteLsps does not have global settings.
	# n Node: /globals/topology/isisFabricPathRouter does not have global settings.
	# n Node: /globals/topology/isisL3Router does not have global settings.
	# n Node: /globals/topology/isisSpbRouter does not have global settings.
	# n Node: /globals/topology/isisTrillRouter does not have global settings.
	# n Node: /globals/topology/igmpHost does not have global settings.
	# n Node: /globals/topology/mldHost does not have global settings.
	# n Node: /globals/topology/ldpBasicRouterV6 does not have global settings.
	# n Node: /globals/topology/ldpBasicRouter does not have global settings.
	# n Node: /globals/topology/ldpTargetedRouter does not have global settings.
	# n Node: /globals/topology/ldpTargetedRouterV6 does not have global settings.
	# n Node: /globals/topology/msrpListener does not have global settings.
	# n Node: /globals/topology/msrpTalker does not have global settings.
	# n Node: /globals/topology/bgpIpv4Peer does not have global settings.
	# n Node: /globals/topology/bgpIpv6Peer does not have global settings.
	# n Node: /globals/topology/igmpQuerier does not have global settings.
	# n Node: /globals/topology/mldQuerier does not have global settings.
	# n Node: /globals/topology/dhcpv4client does not have global settings.
	# n Node: /globals/topology/dhcpv6client does not have global settings.
	# n Node: /globals/topology/dhcpv4server does not have global settings.
	# n Node: /globals/topology/dhcpv6server does not have global settings.
	# n Node: /globals/topology/dhcpv4relayAgent does not have global settings.
	# n Node: /globals/topology/lightweightDhcpv6relayAgent does not have global settings.
	# n Node: /globals/topology/dhcpv6relayAgent does not have global settings.
	# n Node: /globals/topology/pppoxserver does not have global settings.
	# n Node: /globals/topology/lac does not have global settings.
	# n Node: /globals/topology/lns does not have global settings.
	# n Node: /globals/topology/vxlan does not have global settings.
	# n Node: /globals/topology/greoipv4 does not have global settings.
	# n Node: /globals/topology/greoipv6 does not have global settings.
	# n Node: /globals/topology/ptp does not have global settings.
	# n Node: /globals/topology/ancp does not have global settings.
	# n Node: /globals/topology/lacp does not have global settings.
	# n Node: /globals/topology/staticLag does not have global settings.


def ixnHLT_Scriptgen_RunTest(ixiahlt, ixnHLT):
	ixiatcl = ixiahlt.ixiatcl
	# #######################
	# start phase of the test
	# #######################
	ixnHLT_logger('Waiting 60 seconds before starting protocol(s) ...')
	time.sleep(60)

	ixnHLT_logger('Starting all protocol(s) ...')

	_result_ = ixiahlt.test_control(action='start_all_protocols')
	# Check status
	if _result_['status'] != IxiaHlt.SUCCESS:
		ixnHLT_errorHandler('ixiahlt::traffic_control', _result_)

	time.sleep(30)



	#
	#  Reset traffic
	#
	ixnHLT_logger('Resetting traffic...')
	_result_ = ixiahlt.traffic_control(
		action='reset',
		traffic_generator='ixnetwork_540',
		cpdp_convergence_enable='0',
		l1_rate_stats_enable ='1',
		misdirected_per_flow ='0',
		delay_variation_enable='0',
		packet_loss_duration_enable='0',
		latency_bins='enabled',
		latency_control='store_and_forward',
		instantaneous_stats_enable='0'
	)
	# Check status
	if _result_['status'] != IxiaHlt.SUCCESS:
		ixnHLT_errorHandler('traffic_control', _result_)
	#
	# Collect port_handles for traffic_stats
	#
	traffic_stats_ph = set()
	for (k, v) in ixnHLT.iteritems():
		if k.startswith('PORT-HANDLE,'):
			traffic_stats_ph.add(v)

	#
	#  Configure traffic for all configuration elements
	#
	#  -- Traffic item//traffic/trafficItem:<1>
	ixnHLT_logger('Configuring traffic for traffic item: //traffic/trafficItem:<1>')

	ti_srcs, ti_dsts = {}, {}
	ti_mcast_rcvr_handle, ti_mcast_rcvr_port_index, ti_mcast_rcvr_host_index, ti_mcast_rcvr_mcast_index = {}, {}, {}, {}

	ti_srcs['EndpointSet-1'] = ixnHLT_endpointMatch(ixnHLT, ['//topology:<1>'], 'HANDLE')
	if len(ti_srcs) == 0:
		match_err = {'log': 'Cannot find any src endpoints for EndpointSet-1'}
		ixnHLT_errorHandler('ixnHLT_endpointMatch', match_err)

	ti_dsts['EndpointSet-1'] = ''
	ixiatcl.set_py('ti_scalable_dsts(EndpointSet-1)', [ixnHLT['HANDLE,//topology:<2>/deviceGroup:<1>/ethernet:<1>/ipv4:<1>']])
	ixiatcl.set_py('ti_scalable_dsts_port_start(EndpointSet-1)', [1])
	ixiatcl.set_py('ti_scalable_dsts_port_count(EndpointSet-1)', [1])
	ixiatcl.set_py('ti_scalable_dsts_intf_start(EndpointSet-1)', [1])
	ixiatcl.set_py('ti_scalable_dsts_intf_count(EndpointSet-1)', [1])

	_result_ = ixiahlt.traffic_config(
		mode='create',
		traffic_generator='ixnetwork_540',
		endpointset_count=1,
		emulation_src_handle=[[ti_srcs['EndpointSet-1']]],
		emulation_dst_handle=[[ti_dsts['EndpointSet-1']]],
		emulation_multicast_dst_handle=[[]],
		emulation_multicast_dst_handle_type=[[]],
		emulation_scalable_dst_handle='ti_scalable_dsts',
		emulation_scalable_dst_port_start='ti_scalable_dsts_port_start',
		emulation_scalable_dst_port_count='ti_scalable_dsts_port_count',
		emulation_scalable_dst_intf_start='ti_scalable_dsts_intf_start',
		emulation_scalable_dst_intf_count='ti_scalable_dsts_intf_count',
		global_dest_mac_retry_count='1',
		global_dest_mac_retry_delay='5',
		enable_data_integrity='1',
		global_enable_dest_mac_retry='1',
		global_enable_min_frame_size='0',
		global_enable_staggered_transmit='0',
		global_enable_stream_ordering='0',
		global_stream_control='continuous',
		global_stream_control_iterations='1',
		global_large_error_threshhold='2',
		global_enable_mac_change_on_fly='0',
		global_max_traffic_generation_queries='500',
		global_mpls_label_learning_timeout='30',
		global_refresh_learned_info_before_apply='0',
		global_use_tx_rx_sync='1',
		global_wait_time='1',
		global_display_mpls_current_label_value='0',
		global_frame_ordering='none',
		frame_sequencing='disable',
		frame_sequencing_mode='rx_threshold',
		src_dest_mesh='one_to_one',
		route_mesh='one_to_one',
		bidirectional='0',
		allow_self_destined='0',
		use_cp_rate='1',
		use_cp_size='1',
		enable_dynamic_mpls_labels='0',
		hosts_per_net='1',
		name='TI0-QCI7_UL',
		source_filter='all',
		destination_filter='all',
		tag_filter=[[]],
		merge_destinations='1',
		circuit_endpoint_type='ipv4',
		pending_operations_timeout='30'
	)
	# Check status
	if _result_['status'] != IxiaHlt.SUCCESS:
		ixnHLT_errorHandler('traffic_config', _result_)

	#  -- All current config elements
	config_elements = ixiatcl.convert_tcl_list(_result_['traffic_item'])

	#  -- Config Element //traffic/trafficItem:<1>/configElement:<1>
	ixnHLT_logger('Configuring options for config elem: //traffic/trafficItem:<1>/configElement:<1>')
	_result_ = ixiahlt.traffic_config(
		mode='modify',
		traffic_generator='ixnetwork_540',
		stream_id=config_elements[0],
		preamble_size_mode='auto',
		preamble_custom_size='8',
		data_pattern='',
		data_pattern_mode='incr_byte',
		enforce_min_gap='0',
		rate_mbps=ixiavar.traffic_ul_rate_mbps,
		frame_rate_distribution_port='apply_to_all',
		frame_rate_distribution_stream='split_evenly',
		frame_size=ixiavar.traffic_ul_frame_size,
		length_mode='fixed',
		tx_mode='advanced',
		transmit_mode='continuous',
		pkts_per_burst='1',
		tx_delay='0',
		tx_delay_unit='bytes',
		number_of_packets_per_stream='1',
		loop_count='1',
		min_gap_bytes='12'
	)
	# Check status
	if _result_['status'] != IxiaHlt.SUCCESS:
		ixnHLT_errorHandler('traffic_config', _result_)

	#  -- Endpoint set EndpointSet-1
	ixnHLT_logger('Configuring traffic for config elem: //traffic/trafficItem:<1>/configElement:<1>')
	ixnHLT_logger('Configuring traffic for endpoint set: EndpointSet-1')
	#  -- Stack //traffic/trafficItem:<1>/configElement:<1>/stack:"ethernet-1"
	_result_ = ixiahlt.traffic_config(
		mode='modify_or_insert',
		traffic_generator='ixnetwork_540',
		stream_id=config_elements[0],
		stack_index='1',
		l2_encap='ethernet_ii',
		mac_src_mode='fixed',
		mac_src_tracking='0',
		mac_src='00:00:00:00:00:00'
	)
	# Check status
	if _result_['status'] != IxiaHlt.SUCCESS:
		ixnHLT_errorHandler('traffic_config', _result_)

	#  -- Stack //traffic/trafficItem:<1>/configElement:<1>/stack:"pppoESession-2"
	_result_ = ixiahlt.traffic_config(
		mode='modify_or_insert',
		traffic_generator='ixnetwork_540',
		stream_id=config_elements[0],
		stack_index='2',
		pt_handle='pppoESession'
	)
	# Check status
	if _result_['status'] != IxiaHlt.SUCCESS:
		ixnHLT_errorHandler('traffic_config', _result_)

	# The stack handle used to configure the custom fields
	last_stack = _result_['last_stack']

	ixnHLT_logger('Configuring field "pppoESession.header.header.version-1" for stack pppoESession')
	_result_ = ixiahlt.traffic_config(
		mode='set_field_values',
		traffic_generator='ixnetwork_540',
		header_handle=last_stack,
		pt_handle='pppoESession',
		field_handle="pppoESession.header.header.version-1",
		field_activeFieldChoice='0',
		field_auto='0',
		field_optionalEnabled='1',
		field_fullMesh='0',
		field_trackingEnabled='0',
		field_valueType='singleValue',
		field_singleValue='1'
	)
	# Check status
	if _result_['status'] != IxiaHlt.SUCCESS:
		ixnHLT_errorHandler('traffic_config', _result_)

	ixnHLT_logger('Configuring field "pppoESession.header.header.type-2" for stack pppoESession')
	_result_ = ixiahlt.traffic_config(
		mode='set_field_values',
		traffic_generator='ixnetwork_540',
		header_handle=last_stack,
		pt_handle='pppoESession',
		field_handle="pppoESession.header.header.type-2",
		field_activeFieldChoice='0',
		field_auto='0',
		field_optionalEnabled='1',
		field_fullMesh='0',
		field_trackingEnabled='0',
		field_valueType='singleValue',
		field_singleValue='1'
	)
	# Check status
	if _result_['status'] != IxiaHlt.SUCCESS:
		ixnHLT_errorHandler('traffic_config', _result_)

	ixnHLT_logger('Configuring field "pppoESession.header.header.code-3" for stack pppoESession')
	_result_ = ixiahlt.traffic_config(
		mode='set_field_values',
		traffic_generator='ixnetwork_540',
		header_handle=last_stack,
		pt_handle='pppoESession',
		field_handle="pppoESession.header.header.code-3",
		field_activeFieldChoice='0',
		field_auto='0',
		field_optionalEnabled='1',
		field_fullMesh='0',
		field_trackingEnabled='0',
		field_valueType='singleValue',
		field_singleValue='0'
	)
	# Check status
	if _result_['status'] != IxiaHlt.SUCCESS:
		ixnHLT_errorHandler('traffic_config', _result_)

	ixnHLT_logger('Configuring field "pppoESession.header.header.sessionID-4" for stack pppoESession')
	_result_ = ixiahlt.traffic_config(
		mode='set_field_values',
		traffic_generator='ixnetwork_540',
		header_handle=last_stack,
		pt_handle='pppoESession',
		field_handle="pppoESession.header.header.sessionID-4",
		field_activeFieldChoice='0',
		field_auto='0',
		field_optionalEnabled='1',
		field_fullMesh='0',
		field_trackingEnabled='0',
		field_valueType='singleValue',
		field_singleValue='0'
	)
	# Check status
	if _result_['status'] != IxiaHlt.SUCCESS:
		ixnHLT_errorHandler('traffic_config', _result_)

	ixnHLT_logger('Configuring field "pppoESession.header.header.payloadLength-5" for stack pppoESession')
	_result_ = ixiahlt.traffic_config(
		mode='set_field_values',
		traffic_generator='ixnetwork_540',
		header_handle=last_stack,
		pt_handle='pppoESession',
		field_handle="pppoESession.header.header.payloadLength-5",
		field_activeFieldChoice='0',
		field_auto='1',
		field_optionalEnabled='1',
		field_fullMesh='0',
		field_trackingEnabled='0',
		field_valueType='singleValue',
		field_singleValue='40'
	)
	# Check status
	if _result_['status'] != IxiaHlt.SUCCESS:
		ixnHLT_errorHandler('traffic_config', _result_)

	ixnHLT_logger('Configuring field "pppoESession.header.protocolID-6" for stack pppoESession')
	_result_ = ixiahlt.traffic_config(
		mode='set_field_values',
		traffic_generator='ixnetwork_540',
		header_handle=last_stack,
		pt_handle='pppoESession',
		field_handle="pppoESession.header.protocolID-6",
		field_activeFieldChoice='0',
		field_auto='1',
		field_optionalEnabled='1',
		field_fullMesh='0',
		field_trackingEnabled='0',
		field_valueType='singleValue',
		field_singleValue='21'
	)
	# Check status
	if _result_['status'] != IxiaHlt.SUCCESS:
		ixnHLT_errorHandler('traffic_config', _result_)

	#  -- Stack //traffic/trafficItem:<1>/configElement:<1>/stack:"ipv4-3"
	_result_ = ixiahlt.traffic_config(
		mode='modify_or_insert',
		traffic_generator='ixnetwork_540',
		stream_id=config_elements[0],
		stack_index='3',
		l3_protocol='ipv4',
		qos_type_ixn='tos',
		ip_precedence_mode='fixed',
		ip_precedence='0',
		ip_precedence_tracking='0',
		ip_delay_mode='fixed',
		ip_delay='0',
		ip_delay_tracking='0',
		ip_throughput_mode='fixed',
		ip_throughput='0',
		ip_throughput_tracking='0',
		ip_reliability_mode='fixed',
		ip_reliability='0',
		ip_reliability_tracking='0',
		ip_cost_mode='fixed',
		ip_cost='0',
		ip_cost_tracking='0',
		ip_cu_mode='fixed',
		ip_cu='0',
		ip_cu_tracking='0',
		ip_id_mode='fixed',
		ip_id='0',
		ip_id_tracking='0',
		ip_reserved_mode='fixed',
		ip_reserved='0',
		ip_reserved_tracking='0',
		ip_fragment_mode='fixed',
		ip_fragment='1',
		ip_fragment_tracking='0',
		ip_fragment_last_mode='fixed',
		ip_fragment_last='1',
		ip_fragment_last_tracking='0',
		ip_fragment_offset_mode='fixed',
		ip_fragment_offset='0',
		ip_fragment_offset_tracking='0',
		ip_ttl_mode='fixed',
		ip_ttl='64',
		ip_ttl_tracking='0',
		ip_src_mode='fixed',
		ip_src_addr='0.0.0.0',
		ip_src_tracking='0',
		ip_dst_mode='fixed',
		ip_dst_addr='0.0.0.0',
		ip_dst_tracking='0',
		track_by='none',
		egress_tracking='none'
	)
	# Check status
	if _result_['status'] != IxiaHlt.SUCCESS:
		ixnHLT_errorHandler('traffic_config', _result_)

	#  -- Post Options
	ixnHLT_logger('Configuring post options for config elem: //traffic/trafficItem:<1>/configElement:<1>')
	_result_ = ixiahlt.traffic_config(
		mode='modify',
		traffic_generator='ixnetwork_540',
		stream_id=config_elements[0],
		transmit_distribution='ipv4SourceIp0 ipv4DestIp0'
	)
	# Check status
	if _result_['status'] != IxiaHlt.SUCCESS:
		ixnHLT_errorHandler('traffic_config', _result_)

	#  -- Traffic item//traffic/trafficItem:<2>
	ixnHLT_logger('Configuring traffic for traffic item: //traffic/trafficItem:<2>')

	ti_srcs, ti_dsts = {}, {}
	ti_mcast_rcvr_handle, ti_mcast_rcvr_port_index, ti_mcast_rcvr_host_index, ti_mcast_rcvr_mcast_index = {}, {}, {}, {}

	ti_srcs['EndpointSet-1'] = ''
	ti_dsts['EndpointSet-1'] = ixnHLT_endpointMatch(ixnHLT, ['//topology:<1>'], 'HANDLE')
	if len(ti_dsts) == 0:
		match_err = {'log': 'Cannot find any dst endpoints for elem EndpointSet-1'}
		ixnHLT_errorHandler('ixnHLT_endpointMatch', match_err)

	ixiatcl.set_py('ti_scalable_srcs(EndpointSet-1)', [ixnHLT['HANDLE,//topology:<2>/deviceGroup:<1>/ethernet:<1>/ipv4:<1>']])
	ixiatcl.set_py('ti_scalable_srcs_port_start(EndpointSet-1)', [1])
	ixiatcl.set_py('ti_scalable_srcs_port_count(EndpointSet-1)', [1])
	ixiatcl.set_py('ti_scalable_srcs_intf_start(EndpointSet-1)', [1])
	ixiatcl.set_py('ti_scalable_srcs_intf_count(EndpointSet-1)', [1])

	_result_ = ixiahlt.traffic_config(
		mode='create',
		traffic_generator='ixnetwork_540',
		endpointset_count=1,
		emulation_src_handle=[[ti_srcs['EndpointSet-1']]],
		emulation_dst_handle=[[ti_dsts['EndpointSet-1']]],
		emulation_multicast_dst_handle=[[]],
		emulation_multicast_dst_handle_type=[[]],
		emulation_scalable_src_handle='ti_scalable_srcs',
		emulation_scalable_src_port_start='ti_scalable_srcs_port_start',
		emulation_scalable_src_port_count='ti_scalable_srcs_port_count',
		emulation_scalable_src_intf_start='ti_scalable_srcs_intf_start',
		emulation_scalable_src_intf_count='ti_scalable_srcs_intf_count',
		global_dest_mac_retry_count='1',
		global_dest_mac_retry_delay='5',
		enable_data_integrity='1',
		global_enable_dest_mac_retry='1',
		global_enable_min_frame_size='0',
		global_enable_staggered_transmit='0',
		global_enable_stream_ordering='0',
		global_stream_control='continuous',
		global_stream_control_iterations='1',
		global_large_error_threshhold='2',
		global_enable_mac_change_on_fly='0',
		global_max_traffic_generation_queries='500',
		global_mpls_label_learning_timeout='30',
		global_refresh_learned_info_before_apply='0',
		global_use_tx_rx_sync='1',
		global_wait_time='1',
		global_display_mpls_current_label_value='0',
		global_frame_ordering='none',
		frame_sequencing='disable',
		frame_sequencing_mode='rx_threshold',
		src_dest_mesh='one_to_one',
		route_mesh='one_to_one',
		bidirectional='0',
		allow_self_destined='0',
		use_cp_rate='1',
		use_cp_size='1',
		enable_dynamic_mpls_labels='0',
		hosts_per_net='1',
		name='TI1-QCI7_DL',
		source_filter='all',
		destination_filter='all',
		tag_filter=[[]],
		merge_destinations='1',
		circuit_endpoint_type='ipv4',
		pending_operations_timeout='30'
	)
	# Check status
	if _result_['status'] != IxiaHlt.SUCCESS:
		ixnHLT_errorHandler('traffic_config', _result_)

	#  -- All current config elements
	config_elements = ixiatcl.convert_tcl_list(_result_['traffic_item'])

	#  -- Config Element //traffic/trafficItem:<2>/configElement:<1>
	ixnHLT_logger('Configuring options for config elem: //traffic/trafficItem:<2>/configElement:<1>')
	_result_ = ixiahlt.traffic_config(
		mode='modify',
		traffic_generator='ixnetwork_540',
		stream_id=config_elements[0],
		preamble_size_mode='auto',
		preamble_custom_size='8',
		data_pattern='',
		data_pattern_mode='incr_byte',
		enforce_min_gap='0',
		rate_mbps=ixiavar.traffic_dl_rate_mbps,
		frame_rate_distribution_port='apply_to_all',
		frame_rate_distribution_stream='split_evenly',
		frame_size=ixiavar.traffic_dl_frame_size,
		length_mode='fixed',
		tx_mode='advanced',
		transmit_mode='continuous',
		pkts_per_burst='1',
		tx_delay='0',
		tx_delay_unit='bytes',
		number_of_packets_per_stream='1',
		loop_count='1',
		min_gap_bytes='12'
	)
	# Check status
	if _result_['status'] != IxiaHlt.SUCCESS:
		ixnHLT_errorHandler('traffic_config', _result_)

	#  -- Endpoint set EndpointSet-1
	ixnHLT_logger('Configuring traffic for config elem: //traffic/trafficItem:<2>/configElement:<1>')
	ixnHLT_logger('Configuring traffic for endpoint set: EndpointSet-1')
	#  -- Stack //traffic/trafficItem:<2>/configElement:<1>/stack:"ethernet-1"
	_result_ = ixiahlt.traffic_config(
		mode='modify_or_insert',
		traffic_generator='ixnetwork_540',
		stream_id=config_elements[0],
		stack_index='1',
		l2_encap='ethernet_ii',
		mac_src_mode='fixed',
		mac_src_tracking='0',
		mac_src='00:00:00:00:00:00'
	)
	# Check status
	if _result_['status'] != IxiaHlt.SUCCESS:
		ixnHLT_errorHandler('traffic_config', _result_)

	#  -- Stack //traffic/trafficItem:<2>/configElement:<1>/stack:"ipv4-2"
	_result_ = ixiahlt.traffic_config(
		mode='modify_or_insert',
		traffic_generator='ixnetwork_540',
		stream_id=config_elements[0],
		stack_index='2',
		l3_protocol='ipv4',
		qos_type_ixn='tos',
		ip_precedence_mode='fixed',
		ip_precedence='0',
		ip_precedence_tracking='0',
		ip_delay_mode='fixed',
		ip_delay='0',
		ip_delay_tracking='0',
		ip_throughput_mode='fixed',
		ip_throughput='0',
		ip_throughput_tracking='0',
		ip_reliability_mode='fixed',
		ip_reliability='0',
		ip_reliability_tracking='0',
		ip_cost_mode='fixed',
		ip_cost='0',
		ip_cost_tracking='0',
		ip_cu_mode='fixed',
		ip_cu='0',
		ip_cu_tracking='0',
		ip_id_mode='fixed',
		ip_id='0',
		ip_id_tracking='0',
		ip_reserved_mode='fixed',
		ip_reserved='0',
		ip_reserved_tracking='0',
		ip_fragment_mode='fixed',
		ip_fragment='1',
		ip_fragment_tracking='0',
		ip_fragment_last_mode='fixed',
		ip_fragment_last='1',
		ip_fragment_last_tracking='0',
		ip_fragment_offset_mode='fixed',
		ip_fragment_offset='0',
		ip_fragment_offset_tracking='0',
		ip_ttl_mode='fixed',
		ip_ttl='64',
		ip_ttl_tracking='0',
		ip_src_mode='fixed',
		ip_src_addr='0.0.0.0',
		ip_src_tracking='0',
		ip_dst_mode='fixed',
		ip_dst_addr='0.0.0.0',
		ip_dst_tracking='0',
		track_by='none',
		egress_tracking='none'
	)
	# Check status
	if _result_['status'] != IxiaHlt.SUCCESS:
		ixnHLT_errorHandler('traffic_config', _result_)

	#  -- Post Options
	ixnHLT_logger('Configuring post options for config elem: //traffic/trafficItem:<2>/configElement:<1>')
	_result_ = ixiahlt.traffic_config(
		mode='modify',
		traffic_generator='ixnetwork_540',
		stream_id=config_elements[0],
		transmit_distribution='ipv4SourceIp0 ipv4DestIp0'
	)
	# Check status
	if _result_['status'] != IxiaHlt.SUCCESS:
		ixnHLT_errorHandler('traffic_config', _result_)

	#
	# Configure traffic for Layer 4-7 AppLibrary Profile
	#




	#
	# Start traffic configured earlier
	#
	ixnHLT_logger('Running Traffic...')
	_result_ = ixiahlt.traffic_control(
		action='run',
		traffic_generator='ixnetwork_540',
		type='l23'
	)
	# Check status
	if _result_['status'] != IxiaHlt.SUCCESS:
		ixnHLT_errorHandler('traffic_control', _result_)

	traffic_time =int(ixiavar.traffic_time)
	time.sleep(traffic_time)

	# ######################
	# stop phase of the test
	# ######################
	#
	# Stop traffic started earlier
	#
	ixnHLT_logger('Stopping Traffic...')
	_result_ = ixiahlt.traffic_control(
		action='stop',
		traffic_generator='ixnetwork_540',
		type='l23',
	)
	# Check status
	if _result_['status'] != IxiaHlt.SUCCESS:
		ixnHLT_errorHandler('traffic_control', _result_)

	ixnHLT_logger('Stopping all protocol(s) ...')

	_result_ = ixiahlt.test_control(action='stop_all_protocols')
	# Check status
	if _result_['status'] != IxiaHlt.SUCCESS:
		ixnHLT_errorHandler('ixiahlt::traffic_control', _result_)

# ----------------------------------------------------------------
# This dict keeps all generated handles and other info
ixnHLT = {}

# ----------------------------------------------------------------
#  chassis, card, port configuration
#
#  port_list needs to match up with path_list below
#
control_pc_lab = ixiavar.control_pc_lab
chassis = ixiavar.scenario_chassis
tcl_server = ixiavar.scenario_tcl_server
port_list = ixiavar.scenario_port_list
vport_name_list = ixiavar.scenario_vport_name_list
guard_rail = 'none'
#
#  this should match up w/ your port_list above
#
ixnHLT['path_list'] = [['//vport:<1>', '//vport:<2>']]
#
#
_result_ = ixiangpf.connect(
	reset=1,
	device=chassis,
	port_list=port_list,
	ixnetwork_tcl_server=control_pc_lab,
	tcl_server=tcl_server,
	#guard_rail=guard_rail,
	#return_detailed_handles=0
)
# Check status
if _result_['status'] != IxiaHlt.SUCCESS:
	ixnHLT_errorHandler('connect', _result_)
porthandles = []
for (ch, ch_ports, ch_vport_paths) in zip(chassis, port_list, ixnHLT['path_list']):
	ch_porthandles = []
	for (port, path) in zip(ch_ports, ch_vport_paths):
		try:
			ch_key = _result_['port_handle']
			for ch_p in ch.split('.'):
				ch_key = ch_key[ch_p]
			porthandle = ch_key[port]
		except:
			errdict = {'log': 'could not connect to chassis=%s,port=<%s>' % (ch, port)}
			ixnHLT_errorHandler('connect', errdict)

		ixnHLT['PORT-HANDLE,%s' % path] = porthandle
		ch_porthandles.append(porthandle)
	porthandles.append(ch_porthandles)

for (ch_porthandles, ch_vport_names) in zip(porthandles, vport_name_list):
	_result_ = ixiahlt.vport_info(
		mode='set_info',
		port_list=[ch_porthandles],
		port_name_list=[ch_vport_names]
	)
	if _result_['status'] != IxiaHlt.SUCCESS:
		ixnHLT_errorHandler('vport_info', _result_)


# ----------------------------------------------------------------

#call the procedure that configures legacy implementation
ixnHLT_Scriptgen_Configure(ixiahlt, ixnHLT)

#call the procedure that configures CPF
#this should be called after the call to legacy implementation
ixnCPF_Scriptgen_Configure(ixiangpf, ixnHLT)

ixnHLT_Scriptgen_RunTest(ixiahlt, ixnHLT)
