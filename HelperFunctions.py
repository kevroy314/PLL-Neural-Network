__author__ = 'Kevin Horecka, kevin.horecka@gmail.com'

import PIL
from pylab import *  # For PLL


# Print the weight matrix in a readable way
def print_padded_matrix(in_matrix):
    col_width = max(len(word.astype('|S10')) for row in in_matrix for word in row) + 2  # Padding
    for row in in_matrix:
        print "".join(word.astype('|S10').ljust(col_width) for word in row)


def get_image_data_from_file(filename):
    _img = PIL.Image.open(filename)
    _bin_img = _img.convert("P")
    _data = list(_bin_img.getdata())
    _data_out = np.zeros((len(_data)))
    for _i in range(0, len(_data)):
        _data_out[_i] = _data[_i]
    return _data_out