__author__ = 'Kevin Horecka, kevin.horecka@gmail.com'

from scipy import signal
from pylab import *
import matplotlib.pyplot as plt


def cheby2_lowpass_filter(_data, _frequency_cutoff, _carrier_frequency, order):
        nyq = 0.5 * _carrier_frequency
        low = _frequency_cutoff / nyq
        b, a = signal.cheby2(order, 5, low, 'low', analog=False, output='ba')
        return signal.lfilter(b, a, _data)

size = 100
a = np.array(np.zeros(size), dtype=complex)
a.real = np.random.randn(size)
a.imag = np.random.randn(size)
print a

b = cheby2_lowpass_filter(a, 1, 10, 2)
print b


def plotComplexArray(data, labelType):
    plt.plot([data[0].real], [data[0].imag], labelType, label='python')
    for x in range(len(a)-1):
        plt.plot([data[x-1].real, data[x].real], [data[x-1].imag, data[x].imag], labelType, label='python')


plotComplexArray(a, 'ro-')
plotComplexArray(b, 'b^-')

plt.show()
#plt.plot(a)
#plt.plot(b)