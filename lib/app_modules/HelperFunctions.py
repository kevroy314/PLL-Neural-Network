__author__ = 'Kevin Horecka, kevin.horecka@gmail.com'

import PIL
from pylab import *  # For PLL


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
    _img = PIL.Image.open(filename)
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


class LineIntegral:
    def __init__(self, _numElements):
        """
        Initialize a line integral calculator.

        :param _numElements: The number of elements being integrated independently
        """
        self.numElements = _numElements
        self.lengths = np.zeros((self.numElements, 1)).tolist()
        self.data = np.zeros((self.numElements, 1)).tolist()

    def update(self, _d):
        """
        Update the line integral with new points

        :param _d: List of new points of length specified in constructor. If different length, function does nothing.
        :return: Nothing
        """
        if len(self.data) != len(_d):
            return
        for i in range(len(self.data)):
            self.data[i].append(_d[i])
            # TODO Compute length

    def getAverage(self):
        """
        Get the average line length across iterations.

        :return:
        """
        output = []
        for i in range(len(self.lengths)):
            output.append(np.average(self.lengths[i]))
        return output

    def getTotal(self):
        """


        :return:
        """
        output = []
        for i in range(len(self.sums)):
            output.append(np.sum(self.sums[i]))
        return output