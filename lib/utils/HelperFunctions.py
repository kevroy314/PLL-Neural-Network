__author__ = 'Kevin Horecka, kevin.horecka@gmail.com'

import PIL
from pylab import *  # For PLL
import lib.utils.pyeeg as pyeeg
from collections import deque


def print_padded_matrix(in_matrix):
    """
    Print the weight matrix in a readable way.

    :param in_matrix: 2D Matrix to be printed.
    """
    col_width = max(len(word.astype('|S10')) for row in in_matrix for word in row) + 2  # Padding
    for row in in_matrix:
        print "".join(word.astype('|S10').ljust(col_width) for word in row)


def get_image_data_from_file(filename):
    """
    Get a 2D array of 8-bit grayscale image data from a bmp file.

    :param filename: Filename from which to read 8-bit grayscale image data.
    :return: The 2D array of 8-bit grayscale image data.
    """
    _img = PIL.Image.open(filename)  # Ignored PIL.Image import error
    _bin_img = _img.convert("P")
    _data = list(_bin_img.getdata())
    _data_out = np.zeros((len(_data)))
    for _i in range(0, len(_data)):
        _data_out[_i] = _data[_i]
    return _data_out


def get_rgb_image_data_from_file(filename):
    """
    Get a 2D array representing the 3 color channels (RGB tuples), 8-bits each across the pixels in an image.

    :param filename: The filename of the color bmp.
    :return: A 2D array of image data (2D of tuples, RGB, 8-bits each).
    """
    _img = PIL.Image.open(filename)
    #_bin_img = _img.convert("P")
    _data = list(_img.getdata())
    return np.array(_data)

# TODO add file I/O option for measures


class WindowedPathLengthMeasure:
    def __init__(self, num_elements, buffer_length):
        """
        Initialize a line integral calculator.

        :param num_elements: The number of channels being integrated independently
        """
        self.numElements = num_elements
        self.bufferLength = buffer_length
        if self.bufferLength < 2:
            print "Buffer length is too small. Adjusting to length=2."
            self.bufferLength = 2
        self.rollingSums = np.zeros(num_elements)
        self.lengths = []
        self.data = []
        for i in range(0, num_elements):
            self.data.append(deque([], buffer_length))
            self.lengths.append(deque([], buffer_length))

    def update(self, _d):
        """
        Update the line integral with new points

        :param _d: List (channels) of new points (tuples) of length specified in constructor.
                   If different length, function does nothing.
        :return: Nothing
        """
        if len(self.data) != len(_d):
            return
        for i in range(len(self.data)):
            if len(self.data[i]) == self.bufferLength:
                self.data[i].popleft()
            self.data[i].append(_d[i])
            if len(self.data[i]) >= 2:
                a = self.data[i][-1]
                b = self.data[i][-2]
                s = np.subtract(a, b)  # Ignored missing np.subtract reference
                r = np.linalg.norm(s)
                self.rollingSums[i] += r
                if len(self.lengths[i]) == self.bufferLength:
                    self.rollingSums[i] -= self.lengths[i].popleft()
                self.lengths[i].append(r)

        return self.rollingSums


class WindowedApproximateEntropyMeasure:
    def __init__(self, num_elements, buffer_length, m, r):
        """
        Initialize an approximate entropy calculator.

        :param num_elements: The number of channels being measured independently
        """
        self.numElements = num_elements
        self.bufferLength = buffer_length
        if self.bufferLength < 2:
            print "Buffer length is too small. Adjusting to length=2."
            self.bufferLength = 2
        self.M = m
        self.R = r
        self.data = []
        for i in range(0, num_elements):
            self.data.append(deque([], buffer_length))

    def update(self, _d):
        """
        Update the entropy measure with new points

        :param _d: List (channels) of new points (tuples) of length specified in constructor.
                   If different length, function does nothing.
        :return: Nothing
        """
        if len(self.data) != len(_d):
            return
        for i in range(len(self.data)):
            if len(self.data[i]) == self.bufferLength:
                self.data[i].popleft()
            self.data[i].append(_d[i])

        output = []
        for i in range(self.numElements):
            if len(self.data[i]) >= 3:
                output.append(pyeeg.ap_entropy(self.data[i], self.M, self.R))
        return output