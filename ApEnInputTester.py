__author__ = 'Kevin Horecka, kevin.horecka@gmail.com'

from lib.app_modules.HelperFunctions import *
from lib.signals.FileSignal import FileSignal
import os

# Populate list of csv files in directory
input_dir = r'C:\Users\Kevin\Desktop\randomly chosen data\random_pre_dog\dog4_ictal'+'\\'
top_dir = os.path.split(os.path.relpath(input_dir))[-1]
timestring = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")

input_files = []

for _file in os.listdir(input_dir):
    if _file.endswith(".csv"):
        input_files.append(_file)

# Create output file
results_file = open('.\\results\\' + top_dir + '_input_apen_' + timestring + '.csv', 'w')

sample_rate = 400
tick = 1.0 / sample_rate
t = 0
num_channels = 16
num_ticks = 400

for i in range(len(input_files)):
    print datetime.datetime.now().isoformat() + \
          ": Starting Iteration " + str(i) + ", Filename=\"" + input_files[i] + "\""
    """
    Initialize the Simulation
    """
    ApEn = ApproximateEntropy(num_channels, 2, 0.1)

    inputs = []
    # Create Test Signals
    for j in range(0, num_channels):
        inputs.append(FileSignal(input_dir+input_files[i], sample_rate, _rownum=j))

    for j in range(0, num_ticks):
        data = []
        for k in range(0, num_channels):
            dat = inputs[k].update(t)
            tpl = (dat, 0)
            data.append(tpl)
        ApEn.update(data)
        t += tick

    result = str(ApEn.getTotal(0))[1:-1]
    print result
    results_file.write(result + "\n")
    results_file.flush()