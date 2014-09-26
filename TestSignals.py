__author__ = 'Kevin Horecka, kevin.horecka@gmail.com'

from pylab import *  # For PLL
import random

# Class representing the functioning of sine signal
class SineSignal:
    def __init__(self, _amplitude, _frequency, _phase, _noise_level):
        """
        The constructor for a sine wave signal.

        :param _amplitude: the amplitude of the sine wave in volts
        :param _frequency: the frequency of the sine wave in Hz
        :param _phase: the phase of the sine wave in radians
        :param _noise_level: the absolute noise level of the sine wave
        """
        self.frequency = _frequency
        self.two_pi_frequency = 2 * pi * _frequency
        self.amplitude = _amplitude
        self.phase = _phase
        self.noise_level = _noise_level
        self.signal_log = []

    def update(self, _t):
        """
        The update function for the sine signal.

        :param _t: the time of the simulation in seconds
        :return: the next sample from the sine wave in volts
        """
        test_sig = \
            self.amplitude * \
            sin(_t * self.two_pi_frequency + self.phase) + \
            ((random.random() * 2 - 1) * self.noise_level)
        self.signal_log.append(test_sig)
        return test_sig
