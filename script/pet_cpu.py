from petbase import *

class c_cpuload_manager(object):
    def __init__(self, dire):
        self.dire = dire
        self.data = []

    def _parse_a_data_file(self, filename):
        filename = os.sep.join([self.dire, filename])
        if '.xz' in filename:
            import lzma
            lines = lzma.LZMAFile(filename).read().splitlines()
        else:
            lines = open(filename).readlines()
        return [float(line.split(';')[1]) for line in lines[1:]]

    def parse_data_files(self):
        for filename in os.listdir(self.dire):
            if 'SystemCpu' in filename:
                self.data += self._parse_a_data_file(filename)

    def calculate_kpi(self):
        if len(self.data):
            return sum(self.data)/len(self.data)
        else:
            return 0

    def calculate_standard_deviation(self):
        if len(self.data):
            avg = sum(self.data)/len(self.data)
            sdsq = sum([(i - avg) ** 2 for i in self.data])
            stdev = (sdsq / (len(self.data) - 1)) ** .5
            return stdev
        else:
            return 0

if __name__ == '__main__':
    manager = c_cpuload_manager('/home')
    manager.data = [0,5,9,14]
    print manager.calculate_kpi()
    print manager.calculate_standard_deviation()
    manager.data = [5,6,8,9]
    print manager.calculate_kpi()
    print manager.calculate_standard_deviation()
