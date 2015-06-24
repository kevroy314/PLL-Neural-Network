__author__ = 'Kevin Horecka, kevin.horecka@gmail.com'

'''
This helper function converts a row-wise csv file (where each row is a channel)
to a numpy array then saves it as a numpy binary file. This should be done
once, offline as a way of speeding load times in the primary simulation.

The numpy binary file will often be bigger than the csv due to a higher
precision value being stored. This will not be true of extremely large
or very precise numbers which take more than 8 ascii characters to store
in the csv file.

WARNING: This can take a while to run (seconds to minutes) and should
only be done on machines with sufficient RAM. a 200MB file can easily
balloon to 1GB during conversion.
'''

import csv
import numpy as np


input_dir = r"C:\Users\Kevin\Desktop" + '\\'
input_file = "dog1_ictal.csv"

input_filename = input_dir + input_file

signals = []
with open(input_filename, 'rb') as f:
    reader = csv.reader(f)
    print "File open " + input_filename + "."
    i = 0
    for row in reader:
        print "Converting row " + str(i) + " to numpy float64 array."
        signal = np.array(row).astype('float')
        signals.append(signal)
        i += 1
print "Done converting rows, converting master array."
signals = np.array(signals)
out_filename = input_dir + input_file[0:-4]
print "Saving to file " + out_filename + ".npy ."
np.save(out_filename, signals)
print "Done!"