from lxml import etree
import time

class IpaMmlItem(object):
    """ base class for items contained in CommonDict """
    def __str__(self):
        """ support a nice string representation with all attribute values"""
        name = self.name if hasattr(self, 'name') else ''
        showname = self.showname if hasattr(self, 'showname') else ''
        return 'Name: %s, Showame: %s, Index: %d, ParentIndex: %d' %(name, showname, self.index, self.parent_index)

    def __repr__(self):
        return self.__str__()

    def __unicode__(self):
        return self.__str__()

class pdml_object(IpaMmlItem):
    def __init__(self, node):
        self.node = node
        self.name = ''
        self.showname = ''
        for attr in self.node.attrib:
            setattr(self, attr.replace(' ', '_').replace('-', '_'), self.node.attrib[attr])

class pdml_packet(pdml_object):
    def __init__(self, packet_node):
        super(pdml_packet, self).__init__(packet_node)
        self.protos = []
        proto_nodes = packet_node.xpath('.//proto')
        for proto_node in proto_nodes:
            proto = pdml_proto(proto_node)
            proto.packet = self
            self.protos.append(proto)

    def has_proto(self, proto_name):
        return proto_name in [proto.name for proto in self.protos]

    def get_proto(self, proto_name):
        return [proto for proto in self.protos if proto.name.upper() == proto_name.upper()][0]

    def get_seq(self):
        geninfo = self.get_proto('geninfo')
        return 'Seq: %s, Timestamp: %s' %(geninfo.get_field_with_name('num').show, geninfo.get_field_with_name('timestamp').value)

    def __str__(self):
        return 'Packet: Proto count: %d' %(len(self.protos))


class pdml_proto(pdml_object):
    def __init__(self, proto_node):
        super(pdml_proto, self).__init__(proto_node)
        self.fields = []
        field_nodes = proto_node.xpath('.//field')
        for field_node in field_nodes:
            field = pdml_field(field_node)
            self.fields.append(field)

    def has_field_with_name(self, fieldname):
        return fieldname in [field.name for field in self.fields]

    def has_field_with_showname(self, fieldshowname):
        return fieldshowname in [field.showname for field in self.fields]

    def has_field_contain(self, attrname, attrvalue):
        return len([field for field in self.fields if hasattr(field, attrname) and attrvalue.upper() in getattr(field, attrname).upper()]) > 0

    def has_field_contains(self, condition):
        result = True
        for key in condition:
            result =  result & self.has_field_contain(key, condition[key])
            if not result:
                return result
        return result

    def get_field_with_name(self, fieldname):
        return [field for field in self.fields if field.name.upper() == fieldname.upper()][0]

    def get_field_with_showname(self, fieldshowname):
        return [field for field in self.fields if field.showname.upper() == fieldshowname.upper()][0]

    def get_field_contain(self, attrname, attrvalue):
        return [field for field in self.fields if hasattr(field, attrname) and atttrvalue.upper() in getattr(field, attrname).upper()]

    def get_sdr_message(self):
        sfn = self.get_field_with_name('lte_sdr.sfn').showname.split()[-1]
        sbf = self.get_field_with_name('lte_sdr.sbf').showname.split()[-1]
        return float(sfn) + float(sbf)/10


    def __str__(self):
        name = self.name if hasattr(self, 'name') else ''
        showname = self.showname if hasattr(self, 'showname') else ''
        return 'Proto  Name: %s, Showame: %s, Subfield count: %d' %(name, showname, len(self.fields))

class pdml_field(pdml_object):
    def __init__(self, field_node):
        super(pdml_field, self).__init__(field_node)

    def __str__(self):
        name = self.name if hasattr(self, 'name') else ''
        showname = self.showname if hasattr(self, 'showname') else ''
        return 'Field Name: %s, Showame: %s' %(name, showname)


class pdml(object):
    def __init__(self, filename):
        self.filename = filename
        self.packets = []
        self.nodes = []
        self.packet_index = 0

    def get_proto_contain_field_showname(self, condition = {}, from_packet = None, direction = 'forward'):
        if from_packet:
            if hasattr(from_packet, 'packet'):
                packet = from_packet.packet
            else:
                packet = from_packet
            if direction == 'back':
                packets = list(reversed(self.packets[:packet.index]))
            else:
                packets = self.packets[packet.index:]
        else:
            packets = self.packets
        for packet in packets:
            protos = [proto for proto in packet.protos if proto.has_field_contains(condition)]
            if protos:
                return protos[0]

    def get_packet_contain_proto_with_conditions(self, conditions = {}, from_packet = None, direction = 'forward'):
        if from_packet:
            if hasattr(from_packet, 'packet'):
                packet = from_packet.packet
            else:
                packet = from_packet
            if direction == 'back':
                packets = list(reversed(self.packets[:packet.index]))
            else:
                packets = self.packets[packet.index:]
        else:
            packets = self.packets

        for packet in packets:
            found = True
            for proto_name in conditions:
                found = found & packet.has_proto(proto_name)
                if not found:
                    continue
                proto = packet.get_proto(proto_name)
                if proto:
                    found = found & proto.has_field_contains(conditions[proto_name])
                    if found == False:
                        break
                else:
                    found = False
                    break
            if found == True:
                return packet
        raise Exception, 'Could not find the expected packet'


    def parse(self):
        self.tree = etree.parse(self.filename)
        packet_nodes = self.tree.xpath('//packet')
        for packet_node in packet_nodes:
            packet = pdml_packet(packet_node)
            packet.index = self.packet_index
            self.packet_index += 1
            self.packets.append(packet)


class ho_latency_calc(object):
    def __init__(self, src_btslog_filename, dst_btslog_filename, pdml_filename):
        self.src_btslog_filename = src_btslog_filename
        self.dst_btslog_filename = dst_btslog_filename
        self.pdml_filename = pdml_filename
        self.pdml = pdml(pdml_filename)
        self.pdml.parse()
        self.time_pairs = []

# T1
#     starttime = Find "X2AP_HANDOVER_REQUEST_ACKNOWLEDGE, activeService=UEC_HO_SRC, serviceId=UEC_HO_SRC" in source btslog,
#     endtime = Find "asn1MsgId=RRC_CONNECTION_RECONFIGURATION" in source btslog
#     t1 = (endtime-starttime)*1000

    def calc_t1(self):
        print '\nCalculate T1: '
        def _gettime(line):
            ts = line.split()[6].split('T')[-1].replace('Z>', '')
            tstimes = ts.split(':')
            return float(tstimes[0])*3600 + float(tstimes[1])*60+ float(tstimes[2])
        lines = open(self.src_btslog_filename).read().splitlines()
        line1 = [x for x in lines if 'X2AP_HANDOVER_REQUEST_ACKNOWLEDGE, activeService=UEC_HO_SRC, serviceId=UEC_HO_SRC' in x]
        line2 = [x for x in lines if '_payloadSize=104, asn1MsgId=RRC_CONNECTION_RECONFIGURATION' in x]
        line1 = line1[0]
        line2 = line2[0]
        self.time_pairs.append([_gettime(line2) - _gettime(line1)])
        print '     Start Time: ', _gettime(line1)
        print '     End   Time: ', _gettime(line2)
        self.t1 = 1000*(_gettime(line2) - _gettime(line1)) + 0.6
        print '     T1 =  ', self.t1


# T2
#     T2 = 1
    def calc_t2(self):
        print '\nCalculate T2: '
        print '     T2 = 1 '
        self.t2 = 1
        return 1


# T3
#     endtime =
#             find ".... 1... Optional Field Bit: True (mobilityControlInfo is present)"
#             get its value
#             name: AMD PDU --reconfigration message
#             get the AMD PDU with: show = "**** **** = Data", name="lte_rlc", value contains above value,
#             get lte_sdr (sfn, sbf) from the AMD PDU:

#     starttime =
#             from ADM PDU, search backward: lte_sdr = "UL MAC", 2. Radio Bear type:User Plan Radio Bearer;
#             get is lte_sdr
    def calc_t3(self):
        print '\nCalculate T3: '
        proto = self.pdml.get_proto_contain_field_showname({'showname': '.... 1... Optional Field Bit: True (mobilityControlInfo is present)'})
        self.pac_rrc_reconfiguration = proto.packet
        value = proto.get_field_with_name('lte-rrc.c1').value
        amdpdu = self.pdml.get_proto_contain_field_showname({'value': value, 'show':'**** **** = Data', 'name': 'lte_rlc'}, proto, 'back')
        self.pac_admpdu_contain_rrc_reconfiguration = amdpdu.packet
        end_time_sdr = self.pac_admpdu_contain_rrc_reconfiguration.get_proto('lte_sdr')
        end_time_sdr_msg = end_time_sdr.get_sdr_message()
        start_packet = self.pdml.get_packet_contain_proto_with_conditions(
                            {'lte_rlc': {'showname':'Radio Bearer Type: User Plane Radio Bearer'},
                             'lte_sdr': {'showname':'Packet Type: UL MAC'}
                            }, amdpdu, 'back'
                            )
        start_time_sdr = start_packet.get_proto('lte_sdr')
        start_time_sdr_msg = start_time_sdr.get_sdr_message()
        self.end_time_t3 = end_time_sdr_msg

        print '     RRC Reconfiguration packet: ', proto.packet.get_seq()
        print '     Start PDU: ', start_packet.get_seq()
        # print '     Start Time SDR: ', start_time_sdr
        print '     Start Time =  ', start_time_sdr_msg
        print '     End Time Packet: ', end_time_sdr.packet.get_seq()
        # print '     End Time SDR: ', end_time_sdr
        print '     End Time =  ', end_time_sdr_msg
        self.t3 = (end_time_sdr_msg - start_time_sdr_msg)*10
        print '     T3 = ', self.t3

# T4:
#     start time =
#             from reconfigruation messgae, search backword, lte_sdr="DL MAC", 2. Radio Bear type:User Plan Radio Bearer;
#             get its lte_sdr
#     end time = endt time of T3;
    def calc_t4(self):
        print '\nCalculate T4: '
        start_packet = self.pdml.get_packet_contain_proto_with_conditions(
                            {'lte_rlc': {'showname':'Radio Bearer Type: User Plane Radio Bearer'},
                             'lte_sdr': {'showname':'Packet Type: DL MAC'}
                            }, self.pac_rrc_reconfiguration, 'back'
                            )
        start_time_sdr = start_packet.get_proto('lte_sdr')
        start_time_sdr_msg = start_time_sdr.get_sdr_message()
        print '     Start PDU: ', start_packet.get_seq()
        # print '     Start Time SDR: ', start_time_sdr
        print '     Start Time =  ', start_time_sdr_msg
        print '     End Time =  ', self.end_time_t3
        self.t4 = (self.end_time_t3 - start_time_sdr_msg)*10
        print '     T4 = ', self.t4

# T5:
#     start time = end time of T4;
#     end time =
#             find "reconfiguraitonComplte" message, get its value,
#             search forward, find PDU which with: show = "**** **** = Data", name="lte_rlc", value contains above value,
#             get lte_sdr of the AMD PDU

#     T-rach: = msg2 - msg1
#         msg1 = frame+subframe/10
#                 search target btslog, "PrachReceiverProces INF/ULPHY/PRACH#, detect", like: 043879 12.04 16:39:37.201 [192.168.255.129] a8 FSP-1245 <2017-04-12T08:36:59.164772Z> 25-PrachReceiverProces INF/ULPHY/PRACH#, detect 1 preambles on frame 484 subframe 3 subcell 0 cellId 27633,prachIndex is 60,TA is 229(Ts),freOff is -32768,channelizerDataIndCounter is 2211205
#                 get frame and subframe, msg1 = frame+subframe/10
#         msg2 =
#                 from T3 ADM PDU, search forward: "RA Response", get its lte_sdr
#         msg3 =
#                 end time of T5

    def calc_t5(self):
        print '\nCalculate T5: '
        start_time_t5 = self.end_time_t3
        self.pac_rrc_compete = self.pdml.get_packet_contain_proto_with_conditions(
                            {'lte_rrc': {'showname':'rrcConnectionReconfigurationComplete'},
                            }, self.pac_rrc_reconfiguration, 'forward'
                            )
        value = self.pac_rrc_compete.get_proto('lte_rrc').get_field_with_name('lte-rrc.c1').value
        amdpdu = self.pdml.get_proto_contain_field_showname(
                {'value': value, 'show':'**** **** = Data', 'name': 'lte_rlc'}, self.pac_rrc_compete, 'forward')
        self.pac_rrc_reconfiguration_complete = amdpdu.packet
        end_time_sdr = amdpdu.packet.get_proto('lte_sdr')
        end_time_sdr_msg = end_time_sdr.get_sdr_message()
        self.end_time_t5 = end_time_sdr_msg

        lines = open(self.dst_btslog_filename).read().splitlines()
        line1 = [x for x in lines if 'PrachReceiverProces INF/ULPHY/PRACH#, detect' in x][0]
        import re
        frame1 = int(re.findall(r' frame [\d]* ', line1)[0].split()[-1])
        frame2 = int(re.findall(r' subframe [\d]* ', line1)[0].split()[-1])
        msg1 = float(frame1) + float(frame2)/10
        ra_response = self.pdml.get_packet_contain_proto_with_conditions(
                            {'lte_mac': {'showname':'RA Response'},
                            }, self.pac_rrc_reconfiguration, 'forward'
                            )
        ra_response_sdr = ra_response.get_proto('lte_sdr')
        msg2 = ra_response_sdr.get_sdr_message()
        msg3 = end_time_sdr_msg
        self.trach = (msg2 - msg1)*10


        print '     Start Time =  ', start_time_t5
        print '     RRC Complete: ', self.pac_rrc_compete.get_seq()
        print '     AMD PDU for RRC Complete: ', amdpdu.packet.get_seq()
        # print '     End Time SDR: ', end_time_sdr
        print '     End Time =  ', end_time_sdr_msg
        print '     RA Response: ', ra_response.get_seq()
        # print '     RA Response SDR: ', ra_response_sdr
        print '     msg1 =  ', msg1
        print '     msg2 =  ', msg2
        print '     msg3 =  ', msg3
        print '     T-RACH =  ', self.trach
        self.t5 = (end_time_sdr_msg - start_time_t5)*10
        print '     T5 = ', self.t5


# T6:
#     T6=1
    def calc_t6(self):
        print '\nCalculate T6: '
        print '     T6 = 1 '
        self.t6 = 1
        return 1

# T7:
#     start time = end time of T5
#     end time =
#             from AMD PDU of T5 end time, search forward: lte_sdr="uplink control infomation" and "uplink control infomation, Format 0",
#             get the lte_sdr of this pdu

    def calc_t7(self):
        print '\nCalculate T7: '
        start_time = self.end_time_t5
        self.uplink_control = self.pdml.get_packet_contain_proto_with_conditions(
                            {'lte_sdr': {'showname':'Packet Type: Uplink Control Information',
                                         'show':    'Uplink Control Information, Format 0'},
                            }, self.pac_rrc_reconfiguration_complete, 'forward'
                            )
        uplink_control_sdr = self.uplink_control.get_proto('lte_sdr')
        end_time = uplink_control_sdr.get_sdr_message()
        self.end_time_t7 = end_time
        print '     Start Time =  ', start_time
        print '     Uplink Control: ', self.uplink_control.get_seq()
        # print '     End Time SDR: ', uplink_control_sdr
        print '     End Time =  ', end_time
        self.t7 = (end_time - start_time)*10 - 1
        print '     T7 = ', self.t7

# T8:
#     T8=1
    def calc_t8(self):
        print '\nCalculate T8: '
        print '     T8 = 1 '
        self.t8  = 1
        return 1

# T9:
#     start time = endtime of T7
#     end time =
#         from end time of T7 pdu, search forward: 1. lte_sdr = "UL MAC", 2. Radio Bear type:User Plan Radio Bearer;
#         get the lte_sdr the this pdu
    def calc_t9(self):
        print '\nCalculate T9: '
        start_time = self.end_time_t7
        self.amdpdu_t9 = self.pdml.get_packet_contain_proto_with_conditions(
                            {'lte_sdr': {'showname':'Packet Type: UL MAC'},
                             'lte_rlc': {'showname':'Radio Bearer Type: User Plane Radio Bearer'},
                            }, self.uplink_control, 'forward'
                            )
        end_time = self.amdpdu_t9.get_proto('lte_sdr').get_sdr_message()
        self.end_time_t9 = end_time
        print '     Start Time =  ', start_time
        print '     UL MAC PDU: ', self.amdpdu_t9.get_seq()
        # print '     End Time SDR: ', self.amdpdu_t9.get_proto('lte_sdr')
        print '     End Time =  ', end_time
        self.t9 = (end_time - start_time)*10
        print '     T9 = ', self.t9

# T10:
#     T10=1
    def calc_t10(self):
        print '\nCalculate T10: '
        print '     T10 = 1 '
        self.t10 = 1
        return 1

# T11:
#     start time = end time of T9
#     end time =
#         from end time of T9 pdu, search forward: 1. lte_sdr = "DL MAC", 2. Radio Bear type:User Plan Radio Bearer;
#         get the lte_sdr the this pdu
    def calc_t11(self):
        print '\nCalculate T11: '
        start_time = self.end_time_t9
        self.amdpdu_t11 = self.pdml.get_packet_contain_proto_with_conditions(
                            {'lte_sdr': {'showname':'Packet Type: DL MAC'},
                             'lte_rlc': {'showname':'Radio Bearer Type: User Plane Radio Bearer'},
                            }, self.amdpdu_t9, 'forward'
                            )
        end_time = self.amdpdu_t11.get_proto('lte_sdr').get_sdr_message()
        self.end_time_t11 = end_time
        print '     Start Time =  ', start_time
        print '     UL MAC PDU: ', self.amdpdu_t11.get_seq()
        # print '     End Time SDR: ', self.amdpdu_t11.get_proto('lte_sdr')
        print '     End Time =  ', end_time
        self.t11 = (end_time - start_time)*10 - 1
        print '     T11 = ', self.t11

# T12:
#     T12=1
    def calc_t12(self):
        print '\nCalculate T12: '
        print '     T12 = 1 '
        self.t12 = 1
        return 1

    def summary(self):
        print 'C-plane interruption:    eNB %0.4f, E2E: %0.4f' %(self.t1+self.trach, self.t1 + self.t2 + self.t5 + self.t6)
        print 'U-plane DL interruption: eNB %0.4f, E2E: %0.4f' %(self.t7+self.trach+self.t11,
                        self.t4 + self.t5 + self.t6 + self.t7 + self.t8 + self.t9 + self.t10 + self.t11 + self.t12)
        print 'U-plane UL interruption: eNB %0.4f, E2E: %0.4f' %(self.t7+self.trach,
                        self.t5 + self.t6 + self.t7 + self.t8 + self.t9)

    def do_all_calculate(self):
        for i in range(12):
            getattr(self, 'calc_t%d' %(i+1))()
        self.summary()


if __name__ == '__main__':
    latency = ho_latency_calc('source.log', 'target.log', 'pdml.xml')
    latency.do_all_calculate()


