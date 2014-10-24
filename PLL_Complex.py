__author__ = 'Kevin Horecka, kevin.horecka@gmail.com'

from scipy import signal
from pylab import *


# Class representing the functioning of a Phase-Locked Loop
class PLL_Complex:
    def __init__(self, _sample_rate, _carrier_frequency, _lowpass_cutoff_frequency, _phase_shift,
                 phase_detector_voltage_gain=1, vco_voltage_gain=1, vco_voltage_offset=0):
        """
        The constructor for a PLL.

        :param _sample_rate: sample rate in Hz
        :param _carrier_frequency: carrier frequency in Hz
        :param _lowpass_cutoff_frequency: frequency above which components are removed in Hz
        :param _phase_shift: phase shift in radians
        """
        self.sample_rate = _sample_rate

        self.current_phase_shift = 1
        self.next_phase_shift = 1
        self.persistent_phase_shift = _phase_shift

        self.carrier_frequency = _carrier_frequency
        self.two_pi_carrier_frequency = 2 * pi * _carrier_frequency
        self.phase_detector_voltage_gain = phase_detector_voltage_gain
        self.vco_voltage_offset = vco_voltage_offset
        self.vco_voltage_gain = vco_voltage_gain

        self.lowpass_cutoff_frequency = _lowpass_cutoff_frequency
        self.filter_order = 2
        self.filter_window_size = 2

        self.previous_voltage = 1

        self.detected_phase_log = []
        self.applied_phase_shift_log = []
        self.output_voltage_log = []

    @staticmethod
    def butter_lowpass_filter(_data, _frequency_cutoff, _carrier_frequency, order=5):
        """
        The lowpass filter used in the simulation.

        :param _data: the data array representing the filter history
        :param _frequency_cutoff: the frequency cutoff above which all signal components will be filtered
        :param _carrier_frequency: the frequency of the carrier frequency
        :param order: the order of the filter
        :return: a filtered data array containing only low frequency signal components
        """
        nyq = 0.5 * _carrier_frequency
        low = _frequency_cutoff / nyq
        b, a = signal.butter(order, low, btype='low')
        return signal.lfilter(b, a, _data)

    @staticmethod
    def cheby1_lowpass_filter(_data, _frequency_cutoff, _carrier_frequency, order):
        nyq = 0.5 * _carrier_frequency
        low = _frequency_cutoff / nyq
        b, a = signal.cheby1(order, 5, low, 'low', analog=False, output='ba')
        return signal.lfilter(b, a, _data)

    @staticmethod
    def cheby2_lowpass_filter(_data, _frequency_cutoff, _carrier_frequency, order):
        nyq = 0.5 * _carrier_frequency
        low = _frequency_cutoff / nyq
        b, a = signal.cheby2(order, 5, low, 'low', analog=False, output='ba')
        return signal.lfilter(b, a, _data)

    def lowpass(self, _data, _filter_window_size, _frequency_cutoff, _carrier_frequency, _order, filter_type="cheby2"):
        if len(_data) == 0:
            return 0
        elif len(_data) == 1:
            return _data[0]

        filter_window = _data[-_filter_window_size:-1]
        if filter_type == "cheby1":
            return self.cheby1_lowpass_filter(filter_window, _frequency_cutoff, _carrier_frequency, _order)[-1]
        elif filter_type == "butter":
            return self.butter_lowpass_filter(filter_window, _frequency_cutoff, _carrier_frequency, _order)[-1]
        elif filter_type == "cheby2":
            return self.cheby2_lowpass_filter(filter_window, _frequency_cutoff, _carrier_frequency, _order)[-1]

        return 0

    @staticmethod
    def v(theta):
        """
        The periodic odd-even function used in updating the simulation.

        :param theta: the signal phase for the template function
        :return: the odd-even satisfying periodic function output
        """
        return sin(theta)

    def update(self, _t, _y, _PLLs, _self_index, _weight_matrix, _connectivity_matrix):
        """
        The primary update function for the simulation.

        :param _t: the current simulation time in seconds
        :param _y: the input signal voltage in volts
        :param _PLLs: the list of PLLs in the simulation to interact with
        :param _self_index: the index of the PLL being called
        :param _weight_matrix: the phase weight matrix to use for updating
        :param _connectivity_matrix: the connectivity matrix to use for updating
        :return: the next sample output from the PLL in volts
        """
        # BEGIN PLL block

        # Phase Detector
        detected_phase = 0
        if len(self.output_voltage_log) != 0:
            detected_phase = _y * self.previous_voltage * self.phase_detector_voltage_gain
        self.detected_phase_log.append(detected_phase)

        # Lowpass Filter
        filtered_phase = self.lowpass(self.detected_phase_log, self.filter_window_size, self.lowpass_cutoff_frequency,
                                      self.carrier_frequency, self.filter_order)

        # Determine Weighted Phase Adjustment

        phase_aggregator = float(0)
        for _j in range(0, len(_PLLs)):
            phase_aggregator += (_connectivity_matrix[_self_index][_j].real *
                                 self.v(_PLLs[_j].current_phase_shift - pi/2)) \
                                + (_connectivity_matrix[_self_index][_j].imag *
                                   self.v(_PLLs[_j].current_phase_shift))
        if len(_PLLs) == 1:
            self.next_phase_shift = filtered_phase
        else:
            self.next_phase_shift = (self.v(filtered_phase) * phase_aggregator)
        self.applied_phase_shift_log.append(self.next_phase_shift)

        # TODO DEBUG VCO OVERFLOW IN SIN

        # Voltage Controlled Oscillator
        output_voltage = self.vco_voltage_gain * sin(_t * self.two_pi_carrier_frequency + self.next_phase_shift) + \
                         self.vco_voltage_offset
        self.output_voltage_log.append(output_voltage)
        self.previous_voltage = output_voltage

        # END PLL block

        return output_voltage

    def apply_next_phase_shift(self):
        """
        Updates the phase shift value (kept separate from the update function in order to allow pass-by-reference
        iteration of the system).

        """
        self.current_phase_shift = self.next_phase_shift