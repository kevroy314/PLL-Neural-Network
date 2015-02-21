"""Copyleft 2010 Forrest Sheng Bao http://fsbao.net

PyEEG, a Python module to extract EEG features, v 0.02_r2

Project homepage: http://pyeeg.org

**Data structure**

PyEEG only uses standard Python and numpy data structures,
so you need to import numpy before using it.
For numpy, please visit http://numpy.scipy.org

**Naming convention**

I follow "Style Guide for Python Code" to code my program
http://www.python.org/dev/peps/pep-0008/

Constants: UPPER_CASE_WITH_UNDERSCORES, e.g., SAMPLING_RATE, LENGTH_SIGNAL.

Function names: lower_case_with_underscores, e.g., spectrum_entropy.

Variables (global and local): CapitalizedWords or CapWords, e.g., Power.

If a variable name consists of one letter, I may use lower case, e.g., x, y.

Functions listed alphabetically
--------------------------------------------------

"""

"""
File contents minimized and modified by Kevin Horecka, 2/20/15
"""

import numpy as np
from numpy.linalg import svd, lstsq


def hurst(x):
    n = len(x)

    t = np.array([float(i) for i in xrange(1, n + 1)])
    y = np.cumsum(x)
    ave_t = y / t

    s_t = np.zeros(n)
    r_t = np.zeros(n)
    for i in xrange(n):
        s_t[i] = np.std(x[:i + 1])
        x_t = y - t * ave_t[i]
        r_t[i] = max(x_t[:i + 1]) - min(x_t[:i + 1])

    r_s = r_t / s_t
    r_s = np.log(r_s)
    n = np.log(t).reshape(n, 1)
    h = lstsq(n[1:], r_s[1:])[0]
    return h[0]


def embed_seq(x, tau, d):
    n = len(x)

    if d * tau > n:
        print "Cannot build such a matrix, because D * Tau > n"
        exit()

    if tau < 1:
        print "Tau has to be at least 1"
        exit()

    y = np.zeros((n - (d - 1) * tau, d))
    for i in xrange(0, n - (d - 1) * tau):
        for j in xrange(0, d):
            y[i][j] = x[i + j * tau]
    return y


def in_range(template, scroll, distance):
    for i in range(0, len(template)):
        if abs(template[i] - scroll[i]) > distance:
            return False
    return True


def bin_power(x, band, fs):
    c = np.fft.fft(x)
    c = abs(c)
    power = np.zeros(len(band) - 1)
    for Freq_Index in xrange(0, len(band) - 1):
        freq = float(band[Freq_Index])  # Xin Liu
        next_freq = float(band[Freq_Index + 1])
        power[Freq_Index] = sum(c[np.floor(freq / fs * len(x)):np.floor(next_freq / fs * len(x))])
    power_ratio = power / sum(power)
    return power, power_ratio


def first_order_diff(x):
    d = []

    for i in xrange(1, len(x)):
        d.append(x[i] - x[i - 1])

    return d


def pfd(x, d=None):
    if d is None:  # Xin Liu
        d = first_order_diff(x)
    n_delta = 0  # number of sign changes in derivative of the signal
    for i in xrange(1, len(d)):
        if d[i] * d[i - 1] < 0:
            n_delta += 1
    n = len(x)
    return np.log10(n) / (np.log10(n) + np.log10(n / n + 0.4 * n_delta))


def hfd(x, kmax):
    l = []
    n = len(x)
    for k in xrange(1, kmax):
        lk = []
        for m in xrange(0, k):
            lmk = 0
            for i in xrange(1, int(np.floor((n - m) / k))):
                lmk += abs(x[m + i * k] - x[m + i * k - k])
            lmk = lmk * (n - 1) / np.floor((n - m) / float(k)) / k
            lk.append(lmk)
        l.append(np.log(np.mean(lk)))
        x.append([np.log(float(1) / k), 1])

    (p, r1, r2, s) = lstsq(x, l)
    return p[0]


def hjorth(x, d=None):
    if d is None:
        d = first_order_diff(x)

    d.insert(0, x[0])  # pad the first difference
    d = np.array(d)

    n = len(x)

    m2 = float(sum(d ** 2)) / n
    tp = sum(np.array(x) ** 2)
    m4 = 0
    for i in xrange(1, len(d)):
        m4 += (d[i] - d[i - 1]) ** 2
    m4 /= n

    return np.sqrt(m2 / tp), np.sqrt(float(m4) * tp / m2 / m2)  # Hjorth Mobility and Complexity


def spectral_entropy(x, band, fs, power_ratio=None):
    if power_ratio is None:
        power, power_ratio = bin_power(x, band, fs)

    spectral_entropy_out = 0
    for i in xrange(0, len(power_ratio) - 1):
        spectral_entropy_out += power_ratio[i] * np.log(power_ratio[i])
    spectral_entropy_out /= np.log(len(power_ratio))  # to save time, minus one is omitted
    return -1 * spectral_entropy_out


def svd_entropy(x, tau, de, w=None):
    if w is None:
        y = embed_seq(x, tau, de)
        # noinspection PyTypeChecker
        w = svd(y, compute_uv=False)
        w /= sum(w)  # normalize singular values

    return -1 * sum(w * np.log(w))


def fisher_info(x, tau, de, w=None):
    if w is None:
        m = embed_seq(x, tau, de)
        # noinspection PyTypeChecker
        w = svd(m, compute_uv=False)
        w /= sum(w)

    fi = 0
    for i in xrange(0, len(w) - 1):  # from 1 to M
        fi += ((w[i + 1] - w[i]) ** 2) / (w[i])

    return fi


def ap_entropy(x, m, r):
    n = len(x)

    em = embed_seq(x, 1, m)
    emp = embed_seq(x, 1, m + 1)  # try to only build emp to save time

    cm, cm_p = np.zeros(n - m + 1), np.zeros(n - m)
    # in case there is 0 after counting. Log(0) is undefined.

    for i in xrange(0, n - m):
        #		print i
        for j in xrange(i, n - m):  # start from i, self-match counts in ApEn
            #			if max(abs(em[i]-em[j])) <= R:# compare N-M scalars in each subseq v 0.01b_r1
            if in_range(em[i], em[j], r):
                cm[i] += 1  # Xin Liu
                cm[j] += 1
                if abs(emp[i][-1] - emp[j][-1]) <= r:  # check last one
                    cm_p[i] += 1
                    cm_p[j] += 1
        if in_range(em[i], em[n - m], r):
            cm[i] += 1
            cm[n - m] += 1
        # try to count Cm[j] and cm_p[j] as well here

        #		if max(abs(em[N-M]-em[N-M])) <= R: # index from 0, so N-M+1 is N-M  v 0.01b_r1
        #	if in_range(em[i], em[N - M], R):  # for Cm, there is one more iteration than cm_p
        #			Cm[N - M] += 1 # cross-matches on Cm[N - M]

    cm[n - m] += 1  # Cm[N - M] self-matches
    #	import code;code.interact(local=locals())
    cm /= (n - m + 1)
    cm_p /= (n - m)
    #	import code;code.interact(local=locals())
    phi_m, phi_mp = sum(np.log(cm)), sum(np.log(cm_p))

    ap_en = (phi_m - phi_mp) / (n - m)

    return ap_en


def samp_entropy(x, m, r):
    n = len(x)

    em = embed_seq(x, 1, m)
    emp = embed_seq(x, 1, m + 1)

    cm, cm_p = np.zeros(n - m - 1) + 1e-100, np.zeros(n - m - 1) + 1e-100
    # in case there is 0 after counting. Log(0) is undefined.

    for i in xrange(0, n - m):
        for j in xrange(i + 1, n - m):  # no self-match
            #			if max(abs(Em[i]-Em[j])) <= R:  # v 0.01_b_r1
            if in_range(em[i], em[j], r):
                cm[i] += 1
                #			if max(abs(emp[i] - emp[j])) <= R: # v 0.01_b_r1
                if abs(emp[i][-1] - emp[j][-1]) <= r:  # check last one
                    cm_p[i] += 1

    samp_en = np.log(sum(cm) / sum(cm_p))

    return samp_en


def dfa(x, ave=None, l=None):
    x = np.array(x)

    if ave is None:
        ave = np.mean(x)

    y = np.cumsum(x)
    y -= ave

    if l is None:
        l = np.floor(len(x) * 1 / (2 ** np.array(range(4, int(np.log2(len(x))) - 4))))

    f = np.zeros(len(l))  # f(n) of different given box length n

    for i in xrange(0, len(l)):
        n = int(l[i])  # for each box length L[i]
        if n == 0:
            print "time series is too short while the box length is too big"
            print "abort"
            exit()
        for j in xrange(0, len(x), n):  # for each box
            if j + n < len(x):
                c = range(j, j + n)
                c = np.vstack([c, np.ones(n)]).T  # coordinates of time in the box
                y = y[j:j + n]  # the value of data in the box
                f[i] += lstsq(c, y)[1]  # add residue in this box
        f[i] /= ((len(x) / n) * n)
    f = np.sqrt(f)

    alpha = lstsq(np.vstack([np.log(l), np.ones(len(l))]).T, np.log(f))[0][0]

    return alpha
