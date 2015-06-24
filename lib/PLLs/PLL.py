__author__ = 'Kevin Horecka, kevin.horecka@gmail.com'

from pylab import *
from collections import deque
from Filters import *


class Pll:
    def __init__(self, _sample_rate, _carrier_frequency, _lowpass_cutoff_frequency, _phase_shift,
                 filter_order=2, filter_window_size=100, minimum_filter_attenuation=5,
                 phase_detector_voltage_gain=1, vco_voltage_gain=1, vco_voltage_offset=0):
        """
        The constructor for a PLL.

        :param filter_order: The order of the filter (default 2).
        :param filter_window_size: The number of elements which should be included in filtering.
        :param minimum_filter_attenuation: The positive value in dB that the attenuation (-dB) will
        reach at the cutoff frequency (default 5dB).
        :param phase_detector_voltage_gain: Gain to be applied upon phase detection.
        :param vco_voltage_gain: VCO gain (applied when generating output/feedback signal).
        :param vco_voltage_offset: VCO offset in Volts (applied when generating output/feedback signal).
        :param _sample_rate: Sample rate in samples/second.
        :param _carrier_frequency: Carrier frequency in Hz.
        :param _lowpass_cutoff_frequency: The frequency cutoff for the filter (in Hz).
        :param _phase_shift: Phase shift in radians.
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
        self.filter_order = filter_order  # Smoother Curvature
        # (low=jagged, high=smooth: little to no effect on noise level compared to window size)
        self.filter_window_size = filter_window_size  # Tighter Cruve
        # (low=tight, high=loose) with order 2, 3 window size is enough to smooth noise)
        self.minimum_filter_attenuation = minimum_filter_attenuation
        self.previous_voltage = 1
        self.filtered_phase = 0

        self.disable_lowpass = False

        self.disable_logging = True
        if self.disable_logging:
            self.detected_phase_log = deque(np.zeros(self.filter_window_size, dtype='f'), self.filter_window_size)
        else:
            self.detected_phase_log = []
        self.applied_phase_shift_log = []
        self.output_voltage_log = []

        self.filter_settings = get_lowpass_filter_settings(_sample_rate, _lowpass_cutoff_frequency, filter_order,
                                                           minimum_filter_attenuation, filter_type="cheby1")

    @staticmethod
    def v(theta):
        """
        The periodic odd-even function used in updating the simulation.

        :param theta: the signal phase for the template function
        :return: the odd-even satisfying periodic function output
        """
        return sin(theta)

    def update(self, _t, _y, _plls, _self_index, _connectivity_matrix):
        """
        The primary update function for the simulation.

        :param _t: the current simulation time in seconds
        :param _y: the input signal voltage in volts
        :param _plls: the list of PLLs in the simulation to interact with
        :param _self_index: the index of the PLL being called
        :param _connectivity_matrix: the connectivity matrix to use for updating
        :return: the next sample output from the PLL in volts
        """
        # BEGIN PLL block

        # Phase Detector
        detected_phase = 0
        if len(self.detected_phase_log) != 0 or self.disable_logging:
            detected_phase = _y * self.previous_voltage * self.phase_detector_voltage_gain

        if self.disable_logging:
            self.detected_phase_log.append(detected_phase)
            self.detected_phase_log.popleft()  # Ignored unresolved reference for popleft
        else:
            self.detected_phase_log.append(detected_phase)

        if not self.disable_lowpass:
            # Lowpass Filter
            self.filtered_phase = filter_data(self.filter_settings, self.detected_phase_log, latest_point_only=True)
        else:
            self.filtered_phase = detected_phase

        # Determine Weighted Phase Adjustment

        phase_aggregator = float(0)
        for _j in range(0, len(_plls)):
            phase_aggregator += (_connectivity_matrix[_self_index][_j].real *
                                 self.v(_plls[_j].current_phase_shift - pi / 2)) + \
                                (_connectivity_matrix[_self_index][_j].imag *
                                 self.v(_plls[_j].current_phase_shift))

        if len(_plls) == 1:
            self.next_phase_shift = self.filtered_phase
        else:
            self.next_phase_shift = (self.v(self.filtered_phase) * phase_aggregator)
        if not self.disable_logging:
            self.applied_phase_shift_log.append(self.next_phase_shift)

        # Voltage Controlled Oscillator
        output_voltage = self.vco_voltage_gain * self.v(
            _t * self.two_pi_carrier_frequency + self.next_phase_shift) + \
            self.vco_voltage_offset
            # WARNING: Absolute value of phase should be taken
            # if there is an asymmetric complex-valued connectivity matrix.

        if not self.disable_logging:
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