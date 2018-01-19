import os
from petbase import *
from lxml import etree
from copy import deepcopy


class c_usr_builder(object):
    def __init__(self):
        self.root = etree.Element('db',     name="subscribers",
                                            formatname="subscribers",
                                            version="2.1",
                                            external="good.mdl",
                                            AppVersion="AirMosaic LTE UU 6.7.0P1")
        self.tree = etree.ElementTree(self.root)
        self.sample_user = etree.fromstring(node_tamp.usr.user_str)

    def save(self, filename):
        self.tree.write(filename, pretty_print=True)

    def add_a_user(self, attrib_list):
        usr = deepcopy(self.sample_user)
        if isinstance(attrib_list, list):
            pass
        else:
            attrib_list = [attrib_list]
        for attrib in attrib_list:
            key, value = attrib.split(':')[0], attrib.split(':')[1]
            child = usr.xpath('*[@name="%s"]' %(key))
            if child:
                child[0].attrib['value'] = '"%s"' %(value)
        self.root.append(usr)

class c_sid_builder(object):
    def __init__(self, filename):
        self.root = etree.Element('SimulatorInitData', AppVersion="AirMosaic LTE UU 6.8.0P8")
        self.tree = etree.ElementTree(self.root)
        etree.SubElement(self.root, 'CommonServices', LSUHostname=lsu_ip)

    def config_lsu(self):
        self.lsu = etree.SubElement(self.root, 'LSUConfig', Name='TALSU')

    def save(self, filename):
        self.tree.write(filename, pretty_print=True)

class c_sce_builder(object):
    def __init__(self, filename):
        self.tree = etree.parse(filename)

    def save(self, filename):
        self.tree.write(filename, pretty_print=True)



if __name__ == '__main__':
    # usrs = c_usr_builder()
    # usrs.add_a_user('IMEI_SNR:1235')
    # usrs.save('/tmp/usr.xml')

    sid = c_sid_builder('192.168.125.32')
    sid.config_lsu()
    sid.save('/tmp/sid.xml')

    pass
