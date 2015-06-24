__author__ = 'Kevin Horecka, kevin.horecka@gmail.com'

import os
import csv
import numpy as np

name = "dog1_ictal"
input_dir = r"C:\Users\Kevin\Desktop\School\First Paper Data\First Paper Misc\randomly chosen data\random_per_dog"
input_dir += '\\' + name + '\\'

out_filename = r"C:\Users\Kevin\Desktop"
out_filename += '\\' + name + ".csv"

f = open(out_filename, 'wb')
writer = csv.writer(f)

input_files = []

for _file in os.listdir(input_dir):
    if _file.endswith(".csv"):
        input_files.append(_file)

rows = np.empty((16, 0)).tolist()
for _file in input_files:
    reader = csv.reader(open(input_dir + _file, "rb"))
    i = 0
    for row in reader:
        print row
        rows[i].extend(row)
        i += 1
    print "Done writing file: " + _file

writer.writerows(rows)