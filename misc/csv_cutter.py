__author__ = 'Kevin Horecka, kevin.horecka@gmail.com'

import os

directory = r"C:\Users\Kevin\Desktop\School"
filename = r"data_transpose.csv"

event_times = [1471.65, 3463.04, 4372.31, 5985.45, 7593.59, 8886.11, 9858.01, 11922.03, 13622.85, 15178.38, 16498.46, 17272.47, 19273.87, 20791.83, 21593.39, 23339.30, 24160.90]
pre_samples = 800
pos_samples = 800

row_starts = []
for i in range(0, len(event_times)):
    row_starts.append(event_times[i] - pre_samples)
row_count = pre_samples + pos_samples


def extract_csv(_directory, _filename, _row_start, _row_count, has_header_row=False, include_header_row=False):
    if not _directory.endswith('\\'):
        _directory += '\\'

    if os.path.isfile(_directory + _filename):
        filename_no_extension = os.path.splitext(_filename)[0]

        out_filename = _directory + filename_no_extension + "__cut_" + str(_row_start) + "_" + str(_row_count) + ".csv"

        writer = open(out_filename, 'w')

        row_end = _row_start + _row_count
        if has_header_row:
            _row_start += 1
            row_end += 1
        with open(_directory + _filename, 'r') as f:
            i = 0
            for row in f:
                if has_header_row and include_header_row and i == 0:
                    writer.write(row)
                if _row_start <= i < row_end:
                    writer.write(row)
                if i >= row_end:
                    writer.close()
                    f.close()
                    break
                i += 1

for i in range(0,len(row_starts)):
    extract_csv(directory, filename, row_starts[i], row_count)