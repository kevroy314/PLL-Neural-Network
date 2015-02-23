__author__ = 'Kevin Horecka, kevin.horecka@gmail.com'

'''
IMPORTANT: If you want this to laod efficiently, it is important to use the
binary file constructor and not load individually from CSV.
CSV file load times are very slow (~1 minute for a 200MB file) while
binary file load times are less than 1 second. See ConvertCSVToNumpyBinary.py
for convertor between CSV and numpy binary.
'''

import csv
from pylab import *  # For PLL


class FileSignal:
    def __init__(self, _filename, _sample_rate, _rowwise=True, _rownum=0, _colnum=0, _loop=True, _noload=False):
        self.data = []
        self.filename = _filename
        self.sample_rate = _sample_rate
        self.rowwise = _rowwise
        self.rownum = _rownum
        self.colnum = _colnum
        self.loop = _loop
        self.complete = False
        if not _noload:
            if _rowwise:
                with open(_filename, 'rb') as f:
                    reader = csv.reader(f)
                    i = 0
                    for row in reader:
                        if i == _rownum:
                            self.data = np.array(row).astype('float').tolist()
                            break
                        i += 1
            else:
                with open(_filename, 'rb') as f:
                    reader = csv.reader(f)
                    for row in reader:
                        for i in range(len(row)):
                            if i == _colnum:
                                self.data.append(float(row[i]))
                                break

    def update(self, _t):
        index = int(_t * self.sample_rate)
        output = 0
        if self.loop:
            output = self.data[index % len(self.data)]
        else:
            if index > len(self.data):
                self.complete = True
            else:
                output = self.data[index]
        return output

    # Static constructor method for optimized file reading for larger files
    @staticmethod
    def construct_signals_from_csv(_filename, _sample_rate, _rowwise=True):
        signals = []
        if _rowwise:
            with open(_filename, 'rb') as f:
                reader = csv.reader(f)
                for row in reader:
                    signal = FileSignal(_filename, _sample_rate, _noload=True)
                    signal.data = np.array(row).astype('float')
                    signals.append(signal)
            return signals
        else:
            raise NotImplementedError("Column-wise constructor not implemented.")

    # Static constructor method for optimized file reading for larger files (must be row wise numpy format)
    @staticmethod
    def construct_signals_from_numpy_binary(_filename, _sample_rate):
        signals = []
        np_signals = np.load(_filename)
        for line in np_signals:
            signal = FileSignal(_filename, _sample_rate, _noload=True)
            signal.data = line
            signals.append(signal)
        return signals