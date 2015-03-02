__author__ = 'Kevin Horecka, kevin.horecka@gmail.com'

from scipy import signal


def cheby1_lowpass_filter(_data, _sample_rate, _frequency_cutoff, order=2, minimum_attenuation=5):
    """
    Simple Chebyshev Type I filter. See the following for more details:
    http://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.cheby1.html#scipy.signal.cheby1
    http://en.wikipedia.org/wiki/Chebyshev_filter

    :param _sample_rate: The sample rate (in Samples/Second) of the data stream (used to calculate Nyquist).
    :param minimum_attenuation: The positive value in dB that the attenuation (-dB) will reach at the cutoff frequency.
          (default 5dB)
    :param _data: The data to be included in the lowpass filter operation.
    :param _frequency_cutoff: The frequency cutoff for the filter (in Hz).
    :param order: The order of the filter (default 2).
    :return: The output of the lowpass filter (entire window).
    """
    nyq = _sample_rate * 0.5
    low = _frequency_cutoff / nyq
    b, a = signal.cheby1(order, minimum_attenuation, low, 'low', analog=False, output='ba')
    return signal.lfilter(b, a, _data)


def butter_lowpass_filter(_data, _sample_rate, _frequency_cutoff, order=2):
    """
    Simple butterworth lowpass filter. See the following for more details:
    docs.scipy.org/doc/scipy/reference/generated/scipy.signal.butter.html#scipy.signal.butter
    http://en.wikipedia.org/wiki/Butterworth_filter

    :param _sample_rate: The sample rate (in Samples/Second) of the data stream (used to calculate Nyquist).
    :param _data: The data to be included in the lowpass filter operation.
    :param _frequency_cutoff: The frequency cutoff for the filter (in Hz).
    :param order: The order of the filter (default 2).
    :return: The output of the lowpass filter (entire window).
    """
    nyq = _sample_rate * 0.5
    low = _frequency_cutoff / nyq
    b, a = signal.butter(order, low, btype='low')
    return signal.lfilter(b, a, _data)


def cheby2_lowpass_filter(_data, _sample_rate, _frequency_cutoff, order=2, minimum_attenuation=5):
    """
    Simple Chebyshev Type II filter. See the following for more details:
    http://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.cheby2.html#scipy.signal.cheby2
    http://en.wikipedia.org/wiki/Chebyshev_filter

    :param _sample_rate: The sample rate (in Samples/Second) of the data stream (used to calculate Nyquist).
    :param minimum_attenuation: The positive value in dB that the attenuation (-dB) will reach at the cutoff frequency.
          (default 5dB)
    :param _data: The data to be included in the lowpass filter operation.
    :param _frequency_cutoff: The frequency cutoff for the filter (in Hz).
    :param order: The order of the filter (default 2).
    :return: The output of the lowpass filter (entire window).
    """
    nyq = _sample_rate * 0.5
    low = _frequency_cutoff / nyq
    b, a = signal.cheby2(order, minimum_attenuation, low, 'low', analog=False, output='ba')
    return signal.lfilter(b, a, _data)


def lowpass(_data, _sample_rate, _frequency_cutoff, order=2, minimum_attenuation=5, filter_type="cheby2"):
    """
    Lowpass filter wrapper function. This provides ability to call a variety of lowpass filters with various
    options.

    :param _sample_rate: The sample rate (in Samples/Second) of the data stream (used to calculate Nyquist).
    :param minimum_attenuation: The positive value in dB that the attenuation (-dB) will reach at the cutoff frequency.
          (default 5dB)
    :param _data: The data to be included in the lowpass filter operation.
    :param _frequency_cutoff: The frequency cutoff for the filter (in Hz).
    :param order: The order of the filter (default 2).
    :param filter_type: The type of filter ("cheby1", "butter", "cheby2" (default)).
    :return: The output of the lowpass filter (latest point only).
    """
    if len(_data) == 0:
        return 0
    elif len(_data) == 1:
        return _data[0]

    filter_window = _data
    if filter_type == "cheby1":
        return cheby1_lowpass_filter(filter_window, _sample_rate, _frequency_cutoff, order, minimum_attenuation)[-1]
    elif filter_type == "butter":
        return butter_lowpass_filter(filter_window, _sample_rate, _frequency_cutoff, order)[-1]
    elif filter_type == "cheby2":
        return cheby2_lowpass_filter(filter_window, _sample_rate, _frequency_cutoff, order, minimum_attenuation)[-1]

    return 0