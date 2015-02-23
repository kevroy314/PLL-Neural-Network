__author__ = 'Kevin Horecka, kevin.horecka@gmail.com'

from pylab import *  # For PLL


def tracksig(_it):
    return sin(_it / 100 + pi/3)
numiterations = 100

# Initialize variables
vcofreq = np.zeros(numiterations)
ervec = np.zeros(numiterations)
# keep track of last states of reference, signal, and error signal
qsig = 0
qref = 0
lref = 0
lsig = 0
lersig = 0
phs = 0
freq = 0

# Loop filter constants (proportional and derivative)
# Currently powers of two to facilitate multiplication by shifts
prop = 1/128
deriv = 64

for it in range(1, numiterations):
    # Simulate a local oscillator using a 16-bit counter
    phs = mod(phs + np.floor(freq/2 ^ 16), 2 ^ 16)
    ref = phs < 32768
    # Get the next digital value (0 or 1) of the signal to track
    sig = tracksig(it)
    # Implement the phase-frequency detector
    rst = ~(qsig & qref)  # Reset the "flip-flop" of the phase-frequency
                    # detector when both signal and reference are high
    qsig = (qsig | (sig & ~lsig)) & rst   # Trigger signal flip-flop and leading edge of signal
    qref = (qref | (ref & ~lref)) & rst   # Trigger reference flip-flop on leading edge of reference
    lref = ref
    lsig = sig  # Store these values for next iteration (for edge detection)
    ersig = qref - qsig    # Compute the error signal (whether frequency should increase or decrease)
                            # Error signal is given by one or the other flip flop signal
    # Implement a pole-zero filter by proportional and derivative input to frequency
    filtered_ersig = ersig + (ersig - lersig) * deriv
    # Keep error signal for proportional output
    lersig = ersig
    # Integrate VCO frequency using the error signal
    freq = freq - 2 ^ 16 * filtered_ersig * prop
    # Frequency is tracked as a fixed-point binary fraction
    # Store the current VCO frequency
    vcofreq[it] = freq / 2 ^ 16
    # Store the error signal to show whether signal or reference is higher frequency
    ervec[it] = ersig


plot(vcofreq, label='vcofreq')
plot(ervec, label='ervec')