__author__ = 'Kevin Horecka, kevin.horecka@gmail.com'

from scipy import signal


def butter_lowpass_filter(_data, _frequency_cutoff, _carrier_frequency, order=5):
    """
    The lowpass filter used in the simulation.

    :param _data: The data to be lowpassed
    :param _frequency_cutoff: The frequency cutoff for the filter
    :param _carrier_frequency: The carrier frequency for the filter
    :param order: The order of the filter
    :return: The output of the lowpass filter (entire window)
    """
    nyq = 0.5 * _carrier_frequency
    low = _frequency_cutoff / nyq
    b, a = signal.butter(order, low, btype='low')
    return signal.lfilter(b, a, _data)


def cheby1_lowpass_filter(_data, _frequency_cutoff, _carrier_frequency, order):
    """

    :param _data: The data to be lowpassed
    :param _frequency_cutoff: The frequency cutoff for the filter
    :param _carrier_frequency: The carrier frequency for the filter
    :param order: The order of the filter
    :return: The output of the lowpass filter (entire window)
    """
    nyq = 0.5 * _carrier_frequency
    low = _frequency_cutoff / nyq
    b, a = signal.cheby1(order, 5, low, 'low', analog=False, output='ba')
    return signal.lfilter(b, a, _data)


def cheby2_lowpass_filter(_data, _frequency_cutoff, _carrier_frequency, order):
    """

    :param _data: The data to be lowpassed
    :param _frequency_cutoff: The frequency cutoff for the filter
    :param _carrier_frequency: The carrier frequency for the filter
    :param order: The order of the filter
    :return: The output of the lowpass filter (entire window)
    """
    nyq = 0.5 * _carrier_frequency
    low = _frequency_cutoff / nyq
    b, a = signal.cheby2(order, 5, low, 'low', analog=False, output='ba')
    return signal.lfilter(b, a, _data)


def lowpass(_data, _filter_window_size, _frequency_cutoff, _carrier_frequency, _order, filter_type="cheby2"):
    """

    :param _data: The data to be lowpassed (entire data set)
    :param _filter_window_size: The filter window size (subset of data to be lowpassed)
    :param _frequency_cutoff: The frequency cutoff for the filter
    :param _carrier_frequency: The carrier frequency for the filter
    :param _order: The order of the filter
    :param filter_type: The type of filter ("cheby1", "butter", "cheby2" (default))
    :return: The output of the lowpass filter (latest point only)
    """
    if len(_data) == 0:
        return 0
    elif len(_data) == 1:
        return _data[0]

    filter_window = _data
    if filter_type == "cheby1":
        return cheby1_lowpass_filter(filter_window, _frequency_cutoff, _carrier_frequency, _order)[-1]
    elif filter_type == "butter":
        return butter_lowpass_filter(filter_window, _frequency_cutoff, _carrier_frequency, _order)[-1]
    elif filter_type == "cheby2":
        return cheby2_lowpass_filter(filter_window, _frequency_cutoff, _carrier_frequency, _order)[-1]

    return 0