__author__ = 'Kevin Horecka, kevin.horecka@gmail.com'

from lib.app_modules.HelperFunctions import *
from lib.signals.FileSignal import FileSignal
from lib.signals.TestSignals import ComplexSineSignal
from lib.PLLs.PLL_Complex import PLL_Complex
import os


class Complex_PLL_Network:
    def __init__(self, number_of_PLLs, sample_rate, carrier_frequency, lowpass_cutoff_frequency,
                 filter_order=3, filter_window_size=100,
                 keys_dir=".\\input\\complex_keys\\", in_signal_dir=".\\input\\in_signals_complex\\",
                 in_signal_filename=""):
        # Simulation Properties
        self.sample_rate = sample_rate
        self.carrier_frequency = carrier_frequency  # Decomposes (higher=more decomposition/jaggedness, lower=smoother relative to sample rate)
        self.lowpass_cutoff_frequency = lowpass_cutoff_frequency  # Must be <= carrier_frequency/2, effects loose/tight/noise
                                          # low=less noise and tighter, high=more noise/looser
        self.filter_order = filter_order
        self.filter_window_size = filter_window_size
        self.number_of_PLLs = number_of_PLLs

        self.keys_dir = keys_dir
        self.in_signal_dir = in_signal_dir
        self.in_signal_filename = in_signal_filename

        self.t = 0
        self.tick = 1 / self.sample_rate
        self.PLLs = []

        self.noise_level = 0

        self.test_signals = []

        keys = []  # Adding keys means you need to calibrate the filter to work with the keys

        for _file in os.listdir(self.keys_dir):
            if _file.endswith(".bmp"):
                keys.append(get_rgb_image_data_from_file(self.keys_dir+_file))

        # Make the connectivity matrix fully connected
        self.connectivity_matrix = array(np.ones([self.number_of_PLLs, self.number_of_PLLs]), dtype=complex)

        for _i in range(0, self.number_of_PLLs):
            for _j in range(0, self.number_of_PLLs):
                _sum = float(0)
                for _k in range(0, len(keys)):
                    ki = complex(float(keys[_k][_i][0])/255, float(keys[_k][_i][2])/255)
                    kj = complex(float(keys[_k][_j][0])/255, float(keys[_k][_j][2])/255).conjugate()  # conjugate
                    _sum += ki * kj
                self.connectivity_matrix[_i][_j] = _sum / self.number_of_PLLs
                self.connectivity_matrix[_i][_j] = complex(np.abs(self.connectivity_matrix[_i][_j].real), np.abs(self.connectivity_matrix[_i][_j].imag))

        #print "Real Part"
        #print_padded_matrix(self.connectivity_matrix.real)
        #print "Real Part Transpose"
        #print_padded_matrix(np.transpose(self.connectivity_matrix.real))
        #print "Imag Part"
        #print_padded_matrix(self.connectivity_matrix.imag)
        #print "Imag Part Transpose"
        #print_padded_matrix(np.transpose(self.connectivity_matrix.imag))

        # Validate Weight Matrix Symmetry
        if (np.array(self.connectivity_matrix).transpose() != np.array(self.connectivity_matrix)).any():
            print "Error: Phase Offset Matrix Not Symmetric Across Diagonal."
        else:
            print "Array Symmetry Validated."

        # Create PLLs
        for i in range(0, self.number_of_PLLs):
            self.PLLs.append(PLL_Complex(self.sample_rate, self.carrier_frequency, self.lowpass_cutoff_frequency, 1.57079,
                                         filter_order=self.filter_order, filter_window_size=self.filter_window_size))

        for _file in os.listdir(self.in_signal_dir):
            if _file.endswith(".bmp"):
                self.input_signals = get_rgb_image_data_from_file(self.in_signal_dir+_file)
                break

        # Create Test Signals
        for i in range(0, self.number_of_PLLs):
            if in_signal_filename == "":
                self.test_signals.append(ComplexSineSignal(1, carrier_frequency, self.input_signals[i][0], noise_level=self.noise_level))
            else:
                self.test_signals.append(FileSignal(self.in_signal_filename, self.sample_rate, _rownum=i))

    def update(self):
                # Update the test signal and the ppl (iterate simulation)
        for _i in range(0, self.number_of_PLLs):
            self.PLLs[_i].update(self.t, self.test_signals[_i].update(self.t), self.PLLs, _i, self.connectivity_matrix)
        # Update internal states for next iteration
        # (done separately from previous call to maintain consistent internal state across all iterations)
        for _i in range(0, self.number_of_PLLs):
            self.PLLs[_i].apply_next_phase_shift()
        # Iterate the time counter according to the sample rate
        self.t += self.tick