__author__ = 'Kevin Horecka, kevin.horecka@gmail.com'

from lib.utils.HelperFunctions import *
from lib.signals.FileSignal import FileSignal
from lib.PLLs.PLL import Pll


class PllNetwork:
    def __init__(self, number_of_plls, sample_rate, carrier_frequency, lowpass_cutoff_frequency, connectivity_matrix,
                 filter_order=2, filter_window_size=100, minimum_filter_attenuation=5,
                 in_signals_filename=""):
        # Simulation Properties
        """
        This simulation object represents the interconnected PLL network.

        :param number_of_plls: The number of PLLs to be used in the system.
        :param sample_rate: The sample rate of the input stream.
        :param carrier_frequency: The carrier frequency (frequency of the VCO) of each PLL.
        :param lowpass_cutoff_frequency: The frequency cutoff (in Hz) of the lowpass filter.
        :param connectivity_matrix: The connectivity matrix for the PLLs' influence on each other.
        :param filter_order: The order of the lowpass filter (default 2).
        :param filter_window_size: The number of elements to be used in the lowpass filter (default 100).
        :param minimum_filter_attenuation: The attenuation point (in dB) the filter should reach at the cutoff (default 5).
        :param in_signals_filename: The filename for the file which contains the input signal data.
        """
        self.sample_rate = sample_rate
        self.carrier_frequency = carrier_frequency  # Decomposes (higher=more jagged, lower=smoother)
        self.lowpass_cutoff_frequency = lowpass_cutoff_frequency  # Must be <= carrier_freq/2, effects loose/tight/noise
        # low=less noise and tighter, high=more noise/looser
        self.filter_order = filter_order
        self.filter_window_size = filter_window_size
        self.minimum_filter_attenuation = minimum_filter_attenuation
        self.number_of_PLLs = number_of_plls

        self.in_signals_filename = in_signals_filename

        self.t = 0
        self.tick = 1 / self.sample_rate
        self.PLLs = []

        self.input_signals = []

        self.last_input = [0] * number_of_plls

        self.connectivity_matrix = connectivity_matrix

        self.pi_over_2_approx = 1.57079  # The exact value isn't used due to precision issues with floats

        # Validate Weight Matrix Symmetry # Ignored unresolved reference for numpy bool.any() and boo.all()
        if (np.array(self.connectivity_matrix).transpose() != np.array(self.connectivity_matrix)).any():
            print "Error: Phase Offset Matrix Not Symmetric Across Diagonal."
        else:
            print "Array Symmetry Validated."

        # Create PLLs
        for i in range(0, self.number_of_PLLs):
            self.PLLs.append(Pll(self.sample_rate, self.carrier_frequency, self.lowpass_cutoff_frequency,
                                 self.pi_over_2_approx,
                                 filter_order=self.filter_order, filter_window_size=self.filter_window_size,
                                 minimum_filter_attenuation=self.minimum_filter_attenuation))

        # Create Input Signals
        start_time = datetime.datetime.now()
        if self.in_signals_filename[-4:] == '.npy':
            self.input_signals = FileSignal.construct_signals_from_numpy_binary(self.in_signals_filename, self.sample_rate)
        elif self.in_signals_filename[-4:] == '.csv':
            self.input_signals = FileSignal.construct_signals_from_csv(self.in_signals_filename, self.sample_rate)
        execution_time = datetime.datetime.now() - start_time
        print "Input file loaded in " + str(execution_time) + "ms"

    def update(self):  # Update the test signal and the ppl (iterate simulation)
        for _i in range(0, self.number_of_PLLs):
            self.last_input[_i] = self.input_signals[_i].update(self.t)
            self.PLLs[_i].update(self.t, self.last_input[_i], self.PLLs, _i, self.connectivity_matrix)
        # Update internal states for next iteration
        # (done separately from previous call to maintain consistent internal state across all iterations)
        for _i in range(0, self.number_of_PLLs):
            self.PLLs[_i].apply_next_phase_shift()
        # Iterate the time counter according to the sample rate
        self.t += self.tick