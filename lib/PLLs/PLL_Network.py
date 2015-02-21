__author__ = 'Kevin Horecka, kevin.horecka@gmail.com'

from lib.utils.HelperFunctions import *
from lib.signals.FileSignal import FileSignal
from lib.PLLs.PLL import PllComplex


class ComplexPllNetwork:
    def __init__(self, number_of_plls, sample_rate, carrier_frequency, lowpass_cutoff_frequency, connectivity_matrix,
                 filter_order=3, filter_window_size=100,
                 in_signals_filename=""):
        # Simulation Properties
        self.sample_rate = sample_rate
        self.carrier_frequency = carrier_frequency  # Decomposes (higher=more jagged, lower=smoother)
        self.lowpass_cutoff_frequency = lowpass_cutoff_frequency  # Must be <= carrier_freq/2, effects loose/tight/noise
                                                                  # low=less noise and tighter, high=more noise/looser
        self.filter_order = filter_order
        self.filter_window_size = filter_window_size
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
            self.PLLs.append(PllComplex(self.sample_rate, self.carrier_frequency, self.lowpass_cutoff_frequency,
                                        self.pi_over_2_approx,
                                        filter_order=self.filter_order, filter_window_size=self.filter_window_size))

        # Create Input Signals
        for i in range(0, self.number_of_PLLs):
            self.input_signals.append(FileSignal(self.in_signals_filename, self.sample_rate, _rownum=i))

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