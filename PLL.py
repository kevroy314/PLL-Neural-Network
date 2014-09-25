__author__ = 'Kevin Horecka, kevin.horecka@gmail.com'

from scipy import signal
from collections import deque
from pylab import *
from biquad_module import Biquad  # For filters

# Class representing the functioning of a Phase-Locked Loop
class PLL:
    def __init__(self, _sample_rate, _carrier_frequency, _lowpass_cutoff_frequency, _voltage_gain, _phase_shift):
        """
        The constructor for a PLL.

        :param _sample_rate: sample rate in Hz
        :param _carrier_frequency: carrier frequency in Hz
        :param _voltage_gain: voltage gain as a ratio of existing voltage
        :param _phase_shift: phase shift in radians
        """
        self.sample_rate = _sample_rate

        self.current_phase_shift = 0
        self.next_phase_shift = 0
        self.persistent_phase_shift = _phase_shift

        self.carrier_frequency = _carrier_frequency
        self.voltage_gain = _voltage_gain

        self.voltage_output_lowpass_data = deque()
        self.lowpass_cutoff_frequency = _lowpass_cutoff_frequency
        self.filter_order = 2
        self.filter_window_size = 2
        self.bi_quad_lowpass = Biquad(Biquad.LOWPASS, _lowpass_cutoff_frequency, self.sample_rate, 1 / sqrt(2))
        self.output_voltage_log = []
        self.current_phase_shift_log = []
        self.detected_phase_log = []
        self.lock_feedback_signal = False
        self.lock_feedback_signal_value = 0
        self.previous_voltage = 1
        self.output_voltage_lowpass = []
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

    def lowpass(self, _data, _filter_window_size, _frequency_cutoff, _carrier_frequency, _order):
        if(len(_data) == 1):
            return _data[0]
        filter_window = _data[-_filter_window_size:-1]

        return self.butter_lowpass_filter(filter_window, _frequency_cutoff, _carrier_frequency, _order)[-1]

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
        #if self.lock_feedback_signal:
            # Override the existing feedback signal with the locked value
         #   detected_phase = (_y * self.lock_feedback_signal_value * self.voltage_gain)
        #elif len(self.output_voltage_log) != 0:
        detected_phase = _y * self.previous_voltage * self.voltage_gain
        self.detected_phase_log.append(detected_phase)

        # Lowpass Filter
        filtered_phase = self.lowpass(self.detected_phase_log, self.filter_window_size, self.lowpass_cutoff_frequency * 10,
                                      self.carrier_frequency, self.filter_order)
        #filtered_phase = self.bi_quad_lowpass(detected_phase)

        # Determine Weighted Phase Adjustment
        phase_aggregator = 0
        for _j in range(0, len(_PLLs)):
            v_ij = _connectivity_matrix[_self_index][_j] * cos(_weight_matrix[_self_index][_j]).real
            w_ij = _connectivity_matrix[_self_index][_j] * sin(_weight_matrix[_self_index][_j]).imag

            phase_aggregator += v_ij * self.v(_PLLs[_j].current_phase_shift - (pi / 2)) + \
                                w_ij * self.v(_PLLs[_j].current_phase_shift)

        self.next_phase_shift = (filtered_phase) + phase_aggregator + self.persistent_phase_shift
        self.current_phase_shift_log.append(self.next_phase_shift)

        # Voltage Controlled Oscillator

        output_voltage = float(1) * sin((2 * pi * self.carrier_frequency * _t) * detected_phase) + float(1)

        self.output_voltage_log.append(output_voltage)

        self.output_voltage_lowpass.append(self.lowpass(self.output_voltage_log, self.filter_window_size, self.lowpass_cutoff_frequency,
                                            self.carrier_frequency, self.filter_order))
        self.previous_voltage = self.output_voltage_lowpass[-1]
        # END PLL block

        return output_voltage

    def apply_next_phase_shift(self):
        """
        Updates the phase shift value (kept separate from the update function in order to allow pass-by-reference
        iteration of the system).

        """
        self.current_phase_shift = self.next_phase_shift

    def set_feedback_signal_lock(self, locked, lock_value=0):
        self.lock_feedback_signal = locked
        if locked:
            self.lock_feedback_signal_value = lock_value
        else:
            self.lock_feedback_signal_value = 0