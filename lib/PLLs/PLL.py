__author__ = 'Kevin Horecka, kevin.horecka@gmail.com'

from pylab import *
from Filters import *


class PLL:
    def __init__(self, _sample_rate, _carrier_frequency, _lowpass_cutoff_frequency, _phase_shift,
                 phase_detector_voltage_gain=1, vco_voltage_gain=1, vco_voltage_offset=0):
        """
        The constructor for a PLL.

        :param phase_detector_voltage_gain: Gain to be applied upon phase detection
        :param vco_voltage_gain: VCO gain (applied when generating output/feedback signal)
        :param vco_voltage_offset: VCO offset (applied when generating output/feedback signal)
        :param _sample_rate: Sample rate in Hz
        :param _carrier_frequency: Carrier frequency in Hz
        :param _lowpass_cutoff_frequency: Frequency above which components are removed in Hz
        :param _phase_shift: Phase shift in radians
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
    def v(theta):
        """
        The periodic odd-even function used in updating the simulation.

        :param theta: the signal phase for the template function
        :return: the odd-even satisfying periodic function output
        """
        return sin(theta)

    def update(self, _t, _y, _PLLs, _self_index, _connectivity_matrix):
        """
        The primary update function for the simulation.

        :param _t: the current simulation time in seconds
        :param _y: the input signal voltage in volts
        :param _PLLs: the list of PLLs in the simulation to interact with
        :param _self_index: the index of the PLL being called
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
        filtered_phase = lowpass(self.detected_phase_log, self.filter_window_size, self.lowpass_cutoff_frequency,
                                 self.carrier_frequency, self.filter_order)

        # Determine Weighted Phase Adjustment
        phase_aggregator = float(0)
        for _j in range(0, len(_PLLs)):
            phase_aggregator += _connectivity_matrix[_self_index][_j] * cos(_PLLs[_j].current_phase_shift)
        if len(_PLLs) == 1:
            self.next_phase_shift = filtered_phase
        else:
            self.next_phase_shift = (sin(filtered_phase) * phase_aggregator)
        self.applied_phase_shift_log.append(self.next_phase_shift)

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