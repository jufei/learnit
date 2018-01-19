from petbase import *

scfns = {"scfns": "raml21.xsd"}

def get_classnamelist(bts):
    if bts.scftree:
        classnames = bts.scftree.xpath('//scfns:managedObject', namespaces=scfns)
        classnames = [x.get('class') for x in classnames]
        classnames = list(set(classnames))
        classnames.sort()
        bts.classnames = classnames
    else:
        bts.classnames = []

def convert_cn(bts, oldname):
    if ':' in oldname:
        return oldname
    else:
        for classname in bts.classnames:
            if classname.split(':')[-1].upper() == oldname.upper():
                return classname
    return oldname

def get_parameters(bts, pname):
    if bts.scftree:
        return bts.scftree.xpath('//scfns:p[@name="%s"]' %(pname), namespaces=scfns)
    else:
        return []

def get_mos(bts, classname='LNCEL', distname=''):
    classname = convert_cn(bts, classname)
    if bts.scftree:
        mos = bts.scftree.xpath('//scfns:managedObject[@class="%s"]' %(classname), namespaces=scfns)
        if distname:
            mos = [x for x in mos if x.get('distName') == distname]
        return mos
    else:
        return []

def get_mos_distname(bts, classname):
    return [x.get('distName') for x in get_mos(bts, classname)]

def get_parent_mo(bts, node):
    if 'managedObject' in node.getparent().tag:
        return node.getparent()
    else:
        return get_parent_mo(bts, node.getparent())

def get_all_parameter_under_node(node, pname):
    return  node.xpath('.//scfns:p[@name="%s"]' %(pname), namespaces=scfns)

def get_parameter_under_node(node, pname):
    return  node.xpath('scfns:p[@name="%s"]' %(pname), namespaces=scfns)

def scf_has_parameter(bts, pname):
    return len(get_parameters(bts, pname)) <> 0

def scf_has_node(bts, distname = '', pname = '', pvalue = ''):
    node = bts.scftree.xpath('//scfns:*[@distName="%s"]' %(distname), namespaces=scfns)
    if len(node) > 0:
        if pname:
            pnode = node[0].xpath('.//scfns:*[@name="%s"]' %(pname), namespaces=scfns)
            if len(pnode) > 0:
                if pvalue:
                    vnode =  pnode[0].xpath('.//scfns:*[contains(text(),"%s")]' %(pvalue), namespaces=scfns)
                    return len(vnode) > 0
                else:
                    return True
            else:
                return False
        else:
            return True
    else:
        return False

def sort_mos_by_distnames(mos):
    def pack_digit(s):
        return '%0.5d' %(int(s)) if s.isdigit() else s
    def unpack_digit(s):
        return str('%d' %(int(s))) if s.isdigit() else s

    def f1(s):
        return '/'.join(['-'.join([pack_digit(y) for y in x.split('-')]) for x in s.split('/')])

    def f2(s):
        return '/'.join(['-'.join([unpack_digit(y) for y in x.split('-')]) for x in s.split('/')])

    mo_dict = {}
    for mo in mos:
        mo_dict[mo.get('distName')] = mo

    tlist = [f1(s) for s in mo_dict.keys()]
    tlist.sort()
    tlist = [f2(s) for s in tlist]
    return [mo_dict[distName] for distName in tlist]


def sort_nodes_by_parent_mo_distname(bts, nodes):
    parents = [get_parent_mo(bts, node) for node in nodes]
    node_dict = {}
    for node in nodes:
        node_dict[get_parent_mo(bts, node).get('distName')] = node
    parents = sort_mos_by_distnames(parents)
    distnames = [parent.get('distName') for parent in parents]
    return [node_dict[distname] for distname in distnames]
    # if len(nodes) == 0:
    #     return []

    # node_dict = {}
    # for node in nodes:
    #     node_dict[get_parent_mo(bts, node).get('distName')] = node

    # tmplist = []
    # for distname in node_dict.keys():
    #     alist = ['%s-%0.5d' %(phase.split('-')[0], int(phase.split('-')[1])) for phase in distname.split('/')]
    #     tmplist.append('/'.join(alist))
    # tmplist.sort()

    # rlist = []
    # for distname in tmplist:
    #     alist = ['%s-%d' %(phase.split('-')[0], int(phase.split('-')[1])) for phase in distname.split('/')]
    #     rlist.append('/'.join(alist))

    # return [node_dict[distName] for distName in rlist]

def modify_parameter(bts, pname, newvalue):
    nodes = get_parameters(bts, pname)
    if not nodes:
        print "%s not exist" %(pname)
    nodes = sort_nodes_by_parent_mo_distname(bts, nodes)
    if isinstance(newvalue, list):
        newvalue = newvalue * int(bts.cell_count/len(newvalue))
    result = []
    for i in range(len(nodes)):
        distname = get_parent_mo(bts, nodes[i]).get('distName')
        if isinstance(newvalue, list):
            result.append('modify|text=%s|distName=%s iterchild name=%s' %(newvalue[i], distname, pname))
        else:
            result.append('modify|text=%s|distName=%s iterchild name=%s' %(newvalue, distname, pname))
    return result

def delete_parameter(bts, pname):
    nodes = get_parameters(bts, pname)
    result = []
    for i in range(len(nodes)):
        distname = get_parent_mo(bts, nodes[i]).get('distName')
        result.append('delete||distName=%s iterchild name=%s' %(distname, pname))
    return result

def remove_namespace(doc, namespace):
    """Remove namespace in the passed document in place."""
    ns = u'{%s}' % namespace
    nsl = len(ns)
    for elem in doc.getiterator():
        if elem.tag.startswith(ns):
            elem.tag = elem.tag[nsl:]

def re_organize_scf(src_file, dst_file):
    from lxml.etree import tostring
    intree = etree.parse(src_file)
    root = intree.getroot()
    remove_namespace(root, scfns['scfns'])
    cmData = intree.xpath('//cmData')[0]
    header = intree.xpath('//header')[0]

    mrbts = intree.xpath('//managedObject[contains(@class,"MRBTS")]')
    # if mrbts:
    #     if not mrbts[0].xpath('.//extension'):
    #         extension_node = etree.SubElement(mrbts[0], "extension", name="BTSExtensions")
    #         etree.SubElement(extension_node, "p", name="scope").text = "full"

    raml = etree.Element("raml", xmlns="raml21.xsd", version="2.1")
    print raml,cmData.get('id')
    ocmData = etree.SubElement(raml, "cmData", id='3221225472', scope="all", type="plan")
    ocmData.append(header)
    mos = sort_mos_by_distnames(intree.xpath('//managedObject'))
    for mo in mos:
        ocmData.append(mo)
    with open(dst_file, 'w') as f:
        f.writelines(tostring(raml, pretty_print=True))


if __name__ == '__main__':
    filename = '/home/work/tacase/Resource/config/bts/BTS1724/scfc_cap.xml'
    filename = '/home/work/tacase/Resource/config/bts/BTS138/scfc_cap_2cc.xml'

    bts = IpaMmlItem()
    bts.scftree = etree.parse(filename)
    # lcells = get_mos(bts, 'LCELL')
    # node = lcells[0]
    # print len(node.xpath('scfns:p[@name="antlId"]', namespaces=scfns))
    nodes = get_parameters(bts, 'earfcn')
    print nodes
    nodes = sort_nodes_by_parent_mo_distname(bts, nodes)
    print [node.text for node in nodes]

    # print [get_parent_mo(bts, node).get('distName') for node in nodes]
    # print nodes
    # print [get_parent_mo(bts, node).get('distName') for node in nodes]
    # print get_all_parameter_under_node(bts, node, 'antlId')
