# -*- coding: utf-8 -*-
import operator as op
from plyplus import Grammar, STransformer
import re
from decimal import *
import logging
from petbase import *


calc_grammar = Grammar("""
    start: add;
    // Rules
    ?add: (add add_symbol)? mul;
    ?mul: (mul mul_symbol)? atom;
    @atom: neg | number | '\(' add '\)';
    neg: '-' atom;
    // Tokens
    number: '[\d.]+';
    mul_symbol: '\*' | '/';
    add_symbol: '\+' | '-';
    WS: '[ \t]+' (%ignore);
""")

class c_calc(STransformer):
    number      = lambda self, exp: float(exp.tail[0])
    neg         = lambda self, exp: -exp.tail[0]
    __default__ = lambda self, exp: exp.tail[0]

    def _bin_operator(self, exp):
        arg1, operator_symbol, arg2 = exp.tail
        operator_func = { '+': op.add, '-': op.sub, '*': op.mul, '/': op.div }[operator_symbol]
        return operator_func(arg1, arg2)

    add = _bin_operator
    mul = _bin_operator

    def __init__(self, datasource, exp):
        self.logger = logging.getLogger(__file__)
        self.exp = exp
        self.count_result_list = datasource

    def calc_counter_sum(self, counter):
        l = [x.value for x in self.count_result_list if x.counter == counter]
        if len(l) == 0:
            return  'NA'
        else:
            return Decimal(sum(l))

    def calc_counter_max(self, counter):
        l = [x.value for x in self.count_result_list if x.counter == counter]
        if len(l) == 0:
            return 'NA'
        else:
            return Decimal(max(l))

    def calc_counter_min(self, counter):
        l = [x.value for x in self.count_result_list if x.counter == counter]
        if len(l) == 0:
            return 'NA'
        else:
            return Decimal(min(l))

    def calc_avg_exp(self):
        rexp1 = r'AVG[(][^())]*[)]'
        for subexp in re.findall(rexp1, self.exp):
            length=len(re.findall(r'\+',subexp))+1
            rexp2=r'[(][^())]*[)|\+|\-|\*|\/]'
            counter=re.findall(rexp2,subexp)[0].replace('(','').replace(')','')
            repeat_time = len([x.value for x in self.count_result_list if x.counter == counter])
            subexp_avg = subexp.replace('AVG', '')+'/'+'%d'%((length)*(repeat_time))
            self.exp = self.exp.replace(subexp, subexp_avg)

    def calc_max_exp(self):
        rexp = r'MAX[(][^())]*[)]'
        all_exp = self.exp.upper()
        for subexp in re.findall(rexp, all_exp):
            counter = subexp.replace('MAX(', '').replace(')', '')
            self.exp = self.exp.replace(subexp, str(self.calc_counter_max(counter)))

    def calc_min_exp(self):
        rexp = r'MIN[(][^())]*[)]'
        all_exp = self.exp.upper()
        for subexp in re.findall(rexp, all_exp):
            counter = subexp.replace('MIN(', '').replace(')', '')
            self.exp = self.exp.replace(subexp, str(self.calc_counter_min(counter)))

    def calc_normal_exp(self):
        rexp =r'M.*?[\+|\-|\*|\/|\s|)]'
        all_exp = self.exp.upper()
        for subexp in re.findall(rexp, all_exp):
            counter=subexp.replace('+','').replace('-','').replace('*','').replace('/','').replace('(','').replace(')','')
            self.exp = self.exp.replace(counter, str(self.calc_counter_sum(counter)))

    def do_calculate(self):
        tmp_exp = self.exp
        self.exp = self.exp.replace('[','').replace(']','').replace(' ','').upper()
        if 'SUM' in self.exp.upper():
            self.exp = self.exp.upper().replace('SUM','')
        self.calc_max_exp()
        self.calc_avg_exp()
        self.calc_min_exp()
        self.calc_normal_exp()
        try:
            if not 'NA' in str(self.exp):
                print tmp_exp, self.exp
                tree = calc_grammar.parse(self.exp)
                result = self.transform(tree)
                return float(self.transform(tree))
                resultstr = '%0.2f' %(float(result))
            else:
                print tmp_exp, self.exp
                return 'NA'
        except ZeroDivisionError:
            print tmp_exp, self.exp
            return 'NA'


class c_counter_manager(object):
    def __init__(self, xktfile, counterdeffile, data_dire):
        self.xkt_filename = xktfile
        self.counterdeffile = counterdeffile
        self.data_dire = data_dire

        self.pmconfig = None
        self.counter_list = None
        self.data = None
        self.grouplist = None

        self.cellinfolist=None
        self.data_by_cell=None

    def parse_xkt_file(self):
        fields = ['Name', 'Formula', 'Unit', 'SummaryTarget', 'ReportType']
        def _getstr(kpi, fieldname):
            ostr = kpi.xpath(fieldname)[0].text if kpi.xpath(fieldname)[0].text else ''
            ostr = ostr.replace('\n', '')
            return ostr

        def _process_kpi_node(node, groupname, group_report_type):
            item = IpaMmlItem()
            for fieldname in fields:
                setattr(item, fieldname.lower(), _getstr(node, fieldname))
            item.formula = item.formula.replace(u'–', '-').replace(u'＋', '+')
            item.needcheck = item.summarytarget.lower() != '-1.7976931348623157E+308'.lower()
            item.groupname = groupname
            item.reporttype = group_report_type if item.reporttype.lower() =='notset' else item.reporttype
            if item.name.startswith('LTE_'):
                item.counter_alias_name = item.name.split('/')[-1] if '/' in item.name else ' '.join(item.name.split(' ')[1:])
            else:
                item.counter_alias_name = item.name.strip()
            return item

        from lxml import etree
        tree = etree.parse(self.xkt_filename)
        lines = []
        for group in tree.xpath('//Group'):
            groupname = group.xpath('Name')[0].text
            group_report_type = group.xpath('ReportType')[0].text.lower()
            for attemplist in group.xpath('AttemptList'):
                for kpi in attemplist.xpath('KPI'):
                    lines.append(_process_kpi_node(kpi, groupname, group_report_type))
            for attemplist in group.xpath('KPIList'):
                for kpi in attemplist.xpath('KPI'):
                    lines.append(_process_kpi_node(kpi, groupname, group_report_type))
        self.pmconfig = lines
        self.grouplist = list(set([x.groupname for x in self.pmconfig]))
        self.grouplist.sort()

    def parse_data_file(self):
        self.data = []
        for filename in [x for x in os.listdir(self.data_dire) if 'PM.' in x and '.xz' in x]:
            self.data += self.read_counter_from_xml(os.sep.join([self.data_dire, filename]))
        # print self.data

        self.cellinfolist=list(set([x.cellinfo[1] for x in self.data if has_attr(x,'cellinfo') and re.findall(r'LNCEL*' , x.cellinfo[1]) ]))
        # print self.cellinfolist

    def save_data_file(self, csvfile):
        timeslist = list(set([x.starttime for x in self.data]))
        counterlist = list(set([x.counter for x in self.data]))
        timeslist.sort()
        counterlist.sort()
        lines = []
        lines.append(','.join(['']+timeslist))
        for counter in counterlist:
            tstr = counter + ','
            for timestamp in timeslist:
                items = [str(x.value) for x in self.data if x.starttime == timestamp and x.counter == counter]
                if items:
                    tstr += items[0]+','
            lines.append(tstr[:-1])
        with open(csvfile, 'w') as f:
            for line in lines:
                f.write(line+'\n')


    def read_counter_from_xml(self, xzfile):
        from lxml import etree
        import lzma
        result = []
        tree = etree.fromstring(lzma.LZMAFile(xzfile).read())
        for pmsetup in tree.xpath('//PMSetup'):
            for counter in self.counter_list:
                for node in pmsetup.xpath('.//%s' %(counter)):
                    aresult = IpaMmlItem()
                    aresult.starttime = pmsetup.attrib['startTime']
                    aresult.counter = counter
                    aresult.value = float(node.text)
                    parent_node=node.xpath('..')[0]
                    if len(parent_node.xpath('..//%s' %('localMoid'))[0].text.split(r'/')[:2]) > 1:
                        aresult.cellinfo=parent_node.xpath('..//%s' %('localMoid'))[0].text.split(r'/')[:2]
                    result.append(aresult)
        return result


    def _get_counterlist(self):
        result = []
        for expression in [x.formula for x in self.pmconfig]:
            for counter in re.findall(r'M[0-9A-Z]+', expression):
                if not counter in result:
                    result.append(counter)
        result.sort()
        self.counter_list = result

    def prepare_counter_source(self):
        self.parse_xkt_file()
        self._get_counterlist()

    def calc_all_counters(self):
        for groupname in self.grouplist:
            for item in [x for x in self.pmconfig if x.groupname == groupname]:
                calculator = c_calc(self.data, item.formula)
                item.result = calculator.do_calculate()
                item.result_cell=[]
                item.result_cell_show=[]

        report_by_cell = False
        if report_by_cell == True:
            for cell in self.cellinfolist:
                self.data_by_cell = []
                for item in [x for x in self.data if has_attr(x, 'cellinfo') and x.cellinfo[1] == cell]:
                    self.data_by_cell.append(item)
                for groupname in self.grouplist:
                    for item in [x for x in self.pmconfig if x.groupname == groupname]:
                        calculator_by_cell = c_calc(self.data_by_cell, item.formula)
                        item.result_cell.append(calculator_by_cell.do_calculate())
                        item.result_cell_show.append(cell+'/'+str(calculator_by_cell.do_calculate()))

        self.check_result()

    def check_result(self):
        for groupname in self.grouplist:
            for item in [x for x in self.pmconfig if x.groupname == groupname]:
                item.passed = True
                item.resultstr = format('%0.2f' %(float(item.result))) if not 'NA' in str(item.result) else 'NA'
                if item.needcheck:
                    if 'NA' in str(item.result) or\
                        item.reporttype.lower() == 'SuccessRatio'.lower() and float(item.summarytarget) > float(item.result) or\
                        item.reporttype.lower() == 'FailureRatio'.lower() and float(item.summarytarget) < float(item.result):
                        item.passed = False

    def show_check_result_in_html(self):
        for groupname in self.grouplist:
            print '*HTML* <font color="blue">Group Name: %s</font>' %(groupname)
            for item in [x for x in self.pmconfig if x.groupname == groupname]:
                rstr = '    %-80s       %10s%s' %(item.name, item.resultstr, item.unit)
                rstr = '%s    %s%s' %(rstr, item.summarytarget, item.unit ) if item.needcheck else rstr
                if item.needcheck:
                    rstr = rstr + '     PASS' if item.passed else rstr + '      FAIL'
                    color = 'green' if item.passed else 'red'
                else:
                    rstr = rstr +'  SHOW'
                    color = 'blue'
                print '*HTML* <font color="%s">%s</font>' %(color, rstr)

    def show_failed_items(self):
        for item in [x for x in self.pmconfig if not x.passed]:
            print '*HTML* <font color="red">%s----%s----%s</font>' %(item.name, item.formula, item.resultstr)

    def show_check_result_in_table(self):
        table = []
        table.append('Check|KPI|Value|Target|Unit')
        for groupname in self.grouplist:
            for item in [x for x in self.pmconfig if x.groupname == groupname]:
                table_str = '%s|%s' %(item.name, item.resultstr)
                if item.needcheck:
                    table_str += '|'+item.summarytarget
                    #if 'NA' in item.resultstr:
                    if not item.passed:
                        table_str = '<font color="red">FAIL|' +table_str
                    else:
                        table_str = '<font color="green">PASS|'+table_str
                else:
                    table_str = 'Show|'+table_str
                table_str += '|%s</font>' %(item.unit)
                table.append(table_str)
        print_in_table(table)

    def show_check_for_ta_analysis(self):
        table = []
        table.append('*****TAANALYSIS******')
        for groupname in self.grouplist:
            for item in [x for x in self.pmconfig if x.groupname == groupname]:
                table.append('%s|%s' %(item.counter_alias_name, item.resultstr))
        return '\n'.join(table)


if __name__ == '__main__':
     #from pet_counter import parse_xkt_template, parse_counter_files_in_dire, get_counter_list_from_xkt
    configfile= '/home/work/tacase/Resource/config/case/TL17SP.xkt'
    # # pmconfig = parse_xkt_template('/home/work/tacase/Resource/config/case/all.xkt')
    # # counter_list = get_counter_list_from_xkt(pmconfig)
    # # #counter_file_dir=counterfiledir if counterfiledir else  '/home/work/Jenkins2/workspace/MR_TL17_MJ/20160730_2025/TA_TL17FSIH_OBSAI_CAP_00105_20M_20_20_20M_ULDL1_SSF7_TM3_TM3_TM3_TM3_3CC_MR_DRX__2016_07_30__20_25_11/F_EPA5_NO3/counter'
    # counter_file_dir='/home/work/Jenkins2/workspace/MR_TL17_MJ/20160816_1024/TA_TL17FSIH_OBSAI_CAP_00008_20M_ULDL1_SSF7_TM3_8PIPE__2016_08_16__10_25_01/01_MIX_NO2/counter/'
    counter_file_dir='/home/work/Jenkins2/workspace/MR_TL17_CC/20160825_0643/TA_TL17FSMF_OBSAI_CAP_00012_20M_ULDL2_SSF7_TM4X2_2CC_4PIPE__2016_08_25__11_43_44/01_MIX_NO1/counter/'
    counter_file_dir='/home/work/Jenkins2/workspace/MR_TL17_CC/20160906_0930/TA_TL17FSMF_OBSAI_CAP_00005_20M_ULDL2_SSF7_TM4X2_4PIPE_F1235_F2026__2016_09_06__09_30_28/L_DROP_NO5/counter/'
    counter_file_dir='/home/work/Jenkins2/workspace/MR_TL17_BTS2150/20160925_2059/TA_TL17_CAP_00005_20M_ULDL2_SSF7_TM4X2_2CC_4PIPE__2016_09_25__20_59_11/_VOLTE_NO1/counter/'
    # # counter_result = parse_counter_files_in_dire(counter_file_dir, counter_list)
    counter_file_dir = '/home/work/Jenkins2/workspace/MR_TL17_MJ/649/2017_05_01__21_15_48/MPAIRED_RF/counter/'

    manager = c_counter_manager(configfile, '', counter_file_dir)
    manager.parse_xkt_file()
    l = [x for x in manager.pmconfig if '5117d' in x.name][0]
    print l.formula
    # print manager.pmconfig
    # for line in ['%s----%s' %(x.groupname, x.name) for x in manager.pmconfig if x.needcheck]:
    #     print line
    # lines = [x for x in manager.pmconfig if x.needcheck]
    # with open('/home/work/temp/xkt.csv', 'w') as f:
    #     for line in lines:
    #         print '"%s","%s"' %(line.groupname, line.name)
    #         f.write('"%s","%s"\n' %(line.groupname, line.name))
    # print lines
    manager.prepare_counter_source()
    manager.parse_data_file()
    manager.calc_all_counters()
    # manager.show_raw_data()
    manager.show_check_result_in_table()
    # manager.show_check_result_in_html()
    # manager.show_check_result_in_table()
    # manager.show_failed_items()

    #cpu = c_cpuload_manager('/home/work/temp/6')
    # cpu.parse_data_files()
    # print cpu.data
