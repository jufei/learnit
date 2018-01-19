from petbase import *

scfns = {"scfns": "raml21.xsd"}


class c_scf_looker(object):
    def __init__(self, tree):
        self.scftree = tree

    def get_parameters(self, pname):
        if self.scftree:
            return self.scftree.xpath('//scfns:p[@name="%s"]' %(pname), namespaces=scfns)
        else:
            return []

    def get_mos(self, classname='LNCEL', distname=''):
        if self.scftree:
            mos = self.scftree.xpath('//scfns:managedObject[@class="%s"]' %(classname), namespaces=scfns)
            if distname:
                mos = [x for x in mos if x.get('distName') == distname]
            return mos
        else:
            return []

    def get_mos_distname(self, classname):
        return [x.get('distName') for x in self.get_mos(classname)]

    def get_parent_mo(self, node):
        if 'managedObject' in node.getparent().tag:
            return node.getparent()
        else:
            return self.get_parent_mo(node.getparent())

    def get_all_parameter_under_node(self, node, pname):
        return  node.xpath('.//scfns:p[@name="%s"]' %(pname), namespaces=scfns)

    def get_parameter_under_node(self, node, pname):
        return  node.xpath('scfns:p[@name="%s"]' %(pname), namespaces=scfns)

    def scf_has_parameter(self, pname):
        return len(self.get_parameters(pname)) <> 0

    def modify_parameter(self, pname, newvalue):
        nodes = self.get_parameters(pname)
        result = []
        for i in range(len(nodes)):
            distname = self.get_parent_mo(nodes[i]).get('distName')
            if isinstance(newvalue, list):
                result.append('modify|text=%s|distName=%s iterchild name=%s' %(newvalue[i], distname, pname))
            else:
                result.append('modify|text=%s|distName=%s iterchild name=%s' %(newvalue, distname, pname))
        return result

    def delete_parameter(self, pname):
        nodes = self.get_parameters(pname)
        result = []
        for i in range(len(nodes)):
            distname = self.get_parent_mo(nodes[i]).get('distName')
            result.append('delete||distName=%s iterchild name=%s' %(distname, pname))
        return result

    def get_cells(self):
        cells = self.get_mos('LNCEL')
        cellnames = self.get_mos_distname('LNCEL')
        cellnames.sort()
        ncells = []
        for cellname in cellnames:
            ncells.append([cell for cell in cells if cell.get('distName') == cellname][0])
        cells = ncells[:]
        return cells


if __name__ == '__main__':
    pass