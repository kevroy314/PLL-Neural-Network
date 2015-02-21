__author__ = 'Kevin Horecka, kevin.horecka@gmail.com'  # TODO - Change this function to read file in update, not init

import csv
from pylab import *  # For PLL


class FileSignal:
    def __init__(self, _filename, _sample_rate, _rowwise=True, _rownum=0, _colnum=0, _loop=True):
        self.data = []
        self.filename = _filename
        self.sample_rate = _sample_rate
        self.rowwise = _rowwise
        self.rownum = _rownum
        self.colnum = _colnum
        self.loop = _loop
        self.complete = False

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