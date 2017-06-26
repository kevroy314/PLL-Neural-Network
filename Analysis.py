import numpy
import csv
import os
from os import listdir
from os.path import isfile, join
import logging
import matplotlib.pyplot as plt

__author__ = 'Kevin Horecka'


def clean_dir_ending(directory_path):
    directory = directory_path
    if directory[-1] != '\\':
        directory += '\\'
    return directory


def get_files_in_dir(directory):
    files_list = []
    for current_dir in directory:
        files_list.extend([(current_dir + f) for f in listdir(current_dir) if isfile(join(current_dir, f))])
    return files_list


def get_params_from_filename_string(filename, prefix_string):
    params = []
    base = os.path.basename(filename)
    start_index = base.index(prefix_string)
    param_strings = str.split(base[start_index + len(prefix_string):-4], '_')
    params.append([float(x) for x in param_strings])
    return params[0]


def optimize(output_filename, ictal_files, interictal_files, enable_binning=False, bin_num=0, bin_size=100):
    # Create arrays for storing the optimiziation data
    ictal = []
    ictal_params = []
    interictal = []
    interictal_params = []

    # Load the data from both sets of files
    for fname in ictal_files:
        result = csv.reader(open(fname, 'rb'), delimiter=',', quoting=csv.QUOTE_NONNUMERIC)
        ictal_params.append(get_params_from_filename_string(fname, 'ictal_results'))
        ictal.append([])
        for row in result:
            ictal[-1].append(row)
    for fname in interictal_files:
        result = csv.reader(open(fname, 'rb'), delimiter=',', quoting=csv.QUOTE_NONNUMERIC)
        interictal_params.append(get_params_from_filename_string(fname, 'interictal_results'))
        interictal.append([])
        for row in result:
            interictal[-1].append(row)

    # Sanity check to confirm that the number of analysis parameters are the same (big problem if not)
    if len(ictal_params) != len(interictal_params):
        logging.error("Error: There are not an equal number of ictal and interictal analysis files.")

    # Check to make sure that, in our list of ictal vs interictal, the parameters for one match the parameters
    # for the other (they are one-to-one).
    mismatch_count = 0
    for i in range(len(ictal_params)):
        if len(ictal_params[i]) != len(interictal_params[i]):
            logging.error("Error: Parameter lists are not equal in size.")
        mismatch = False
        for j in range(0, len(ictal_params[i])):
            val0 = ictal_params[i][j]
            val1 = interictal_params[i][j]
            if val0 != val1:
                mismatch = True
        if mismatch:
            mismatch_count += 1
    if mismatch_count != 0:
        logging.error("Error: %d filename parameter sets do not match." % mismatch_count)

    # Set the calibration parameters to be the ictal parameters (arbitrary)
    params = ictal_params

    # If we're doing binning (file-by-file subsetting of the data - so you can analyze a specific dog), extract the
    # requested bin.
    if enable_binning:
        for i in range(0, len(ictal)):
            ictal[i] = ictal[i][bin_size * bin_num:(bin_size * bin_num) + bin_size]
        for i in range(0, len(interictal)):
            interictal[i] = interictal[i][bin_size * bin_num:(bin_size * bin_num) + bin_size]

    # Take the mean path length across electrodes
    ictal_means = numpy.mean(ictal, axis=2)
    interictal_means = numpy.mean(interictal, axis=2)

    # Define our internal charactarization function
    def characterize(positive_list, negative_list, threshold):
        true_pos = (positive_list >= threshold).sum()
        false_neg = (positive_list < threshold).sum()
        true_neg = (negative_list < threshold).sum()
        false_pos = (negative_list >= threshold).sum()
        return true_pos, true_neg, false_pos, false_neg

    # Create arrays for storing TP, TN ,FP, FN
    true_positives = []
    true_negatives = []
    false_positives = []
    false_negatives = []
    for i in range(0, len(interictal_means)):
        true_positives.append([])
        true_negatives.append([])
        false_positives.append([])
        false_negatives.append([])
        # Iterate through the mean value arrays and the candidate arrays - fill output arrays with values from
        # charactarization function.
        for j in range(0, len(interictal_means[i])):
            candidate = interictal_means[i][j]
            true_positive, true_negative, false_positive, false_negative = characterize(ictal_means[i],
                                                                                        interictal_means[i], candidate)
            true_positives[i].append(true_positive)
            true_negatives[i].append(true_negative)
            false_positives[i].append(false_positive)
            false_negatives[i].append(false_negative)

    # Define results arrays for each file
    # sums = []  # The sum of TP and TN
    accuracy = []  # The TP+TN/(len(TP) + len(TN)) for a given file - aka percent accuracy or "correctness" measure
    ftpn = []
    bests = []  # The best accuracy in the correctness array for this file (peak accuracy)

    # Create the output file w/ parameters (in file order), best accuracy, best threshold, and all accuracies
    output_fp = open(output_filename, 'wb')
    output_file = csv.writer(output_fp)
    ftpn_fp = open(output_filename + 'ftpn.csv', 'wb')
    ftpn_file = csv.writer(ftpn_fp)
    output_fp.write(
        'number_of_input_channels,sample_rate,duration,carrier_frequency,lowpass_cuttoff_frequency,filter_order,filter_window_size,path_length_window_size,best_correctness,best_correctness_threshold,correcnesses...\r\n')
    for i in range(0, len(true_positives)):
        # sums.append(numpy.add(numpy.array(true_positives[i]), numpy.array(true_negatives[i])))
        # correctness.append(sums[i] / float(len(true_positives[i]) + len(true_negatives[i])))
        acc = []
        for j in range(0, len(true_positives[i])):
            acc.append(float(true_positives[i][j] + true_negatives[i][j]) / float(
                true_positives[i][j] + false_positives[i][j] + false_negatives[i][j] + true_negatives[i][j]))
        print acc
        accuracy.append(acc)
        ftpn.append([true_positives[i], true_negatives[i], false_positives[i], false_negatives[i]])
        best_threshold = interictal_means[i][numpy.argmax(accuracy[i])]
        bests.append(max(list(accuracy[i])))
        output_row = params[i] + [bests[i]] + [best_threshold] + list(accuracy[i])
        output_file.writerow(output_row)

        ftpn_file.writerows(ftpn[i])

        # Output a report of the file success
        report = "Params: " + str(params[i]) + ", Best Score: " + str(bests[i]) + ", Threshold: " + str(best_threshold)
        print report


def test(threshold, output_filename, ictal_files, interictal_files, enable_binning=False, bin_num=0, bin_size=100):
    # Create arrays for storing the optimiziation data
    ictal = []
    ictal_params = []
    interictal = []
    interictal_params = []

    # Load the data from both sets of files
    for fname in ictal_files:
        result = csv.reader(open(fname, 'rb'), delimiter=',', quoting=csv.QUOTE_NONNUMERIC)
        ictal_params.append(get_params_from_filename_string(fname, 'ictal_results'))
        ictal.append([])
        for row in result:
            ictal[-1].append(row)
    for fname in interictal_files:
        result = csv.reader(open(fname, 'rb'), delimiter=',', quoting=csv.QUOTE_NONNUMERIC)
        interictal_params.append(get_params_from_filename_string(fname, 'interictal_results'))
        interictal.append([])
        for row in result:
            interictal[-1].append(row)

    # Sanity check to confirm that the number of analysis parameters are the same (big problem if not)
    if len(ictal_params) != len(interictal_params):
        logging.error("Error: There are not an equal number of ictal and interictal analysis files.")

    # Check to make sure that, in our list of ictal vs interictal, the parameters for one match the parameters
    # for the other (they are one-to-one).
    mismatch_count = 0
    for i in range(len(ictal_params)):
        if len(ictal_params[i]) != len(interictal_params[i]):
            logging.error("Error: Parameter lists are not equal in size.")
        mismatch = False
        for j in range(0, len(ictal_params[i])):
            val0 = ictal_params[i][j]
            val1 = interictal_params[i][j]
            if val0 != val1:
                mismatch = True
        if mismatch:
            mismatch_count += 1
    if mismatch_count != 0:
        logging.error("Error: %d filename parameter sets do not match." % mismatch_count)

    # Set the calibration parameters to be the ictal parameters (arbitrary)
    params = ictal_params

    # If we're doing binning (file-by-file subsetting of the data - so you can analyze a specific dog), extract the
    # requested bin.
    if enable_binning:
        for i in range(0, len(ictal)):
            ictal[i] = ictal[i][bin_size * bin_num:(bin_size * bin_num) + bin_size]
        for i in range(0, len(interictal)):
            interictal[i] = interictal[i][bin_size * bin_num:(bin_size * bin_num) + bin_size]

    # Take the mean path length across electrodes
    ictal_means = numpy.mean(ictal, axis=2)
    interictal_means = numpy.mean(interictal, axis=2)

    # Define our internal charactarization function
    def characterize(positive_list, negative_list, t):
        true_pos = (positive_list >= t).sum()
        false_neg = (positive_list < t).sum()
        true_neg = (negative_list < t).sum()
        false_pos = (negative_list >= t).sum()
        return true_pos, true_neg, false_pos, false_neg

    # Create arrays for storing TP, TN ,FP, FN
    true_positives = []
    true_negatives = []
    false_positives = []
    false_negatives = []
    for i in range(0, len(interictal_means)):
        true_positive, true_negative, false_positive, false_negative = characterize(ictal_means[i],
                                                                                    interictal_means[i], threshold)
        true_positives.append(true_positive)
        true_negatives.append(true_negative)
        false_positives.append(false_positive)
        false_negatives.append(false_negative)

    # Define results arrays for each file
    accuracy = []  # The TP+TN/(len(TP) + len(TN)) for a given file - aka percent accuracy or "correctness" measure
    ftpn = []

    # Create the output file w/ parameters (in file order), best accuracy, best threshold, and all accuracies
    output_fp = open(output_filename, 'wb')
    output_file = csv.writer(output_fp)
    output_fp.write(
        'number_of_input_channels,sample_rate,duration,carrier_frequency,lowpass_cuttoff_frequency,filter_order,filter_window_size,path_length_window_size,accuracy,threshold,tp,tn,fp,tn\r\n')
    for i in range(0, len(true_positives)):
        # sums.append(numpy.add(numpy.array(true_positives[i]), numpy.array(true_negatives[i])))
        # correctness.append(sums[i] / float(len(true_positives[i]) + len(true_negatives[i])))
        acc = float(true_positives[i] + true_negatives[i]) / float(
            true_positives[i] + false_positives[i] + false_negatives[i] + true_negatives[i])
        print acc
        accuracy.append(acc)
        ftpn.append([true_positives[i], true_negatives[i], false_positives[i], false_negatives[i]])
        output_row = params[i] + [acc] + [true_positives[i]] + [true_negatives[i]] + [false_positives[i]] + [false_negatives[i]]
        output_file.writerow(output_row)

        # Output a report of the file success
        report = "Params: " + str(params[i]) + ", Accuracy: " + str(acc) + ", Threshold: " + str(threshold)
        print report


def load_roc_arrays(filename):
    file_reader = csv.reader(open(filename, 'rb'), delimiter=',', quoting=csv.QUOTE_NONNUMERIC)
    i = 0
    outputs = [[], [], [], []]
    for row in file_reader:
        outputs[i % len(outputs)].append(row)
        i += 1
    return outputs[0], outputs[1], outputs[2], outputs[3]


def visualize_single_roc(tp, tn, fp, fn):
    if not (len(tp) == len(tn) and len(tp) == len(fp) and len(tp) == len(fn)):
        logging.error(
            'Error: Cannot build ROC with unequal length input arrays. Confirm lengths of arrays and try again.')
    roc_x = []
    roc_y = []
    for i in range(0, len(tp)):
        try:
            fpr = fp[i] / (fp[i] + tn[i])
            tpr = tp[i] / (tp[i] + fn[i])
            roc_x.append(fpr)
            roc_y.append(tpr)
        except ZeroDivisionError:
            print "Div 0 at i=%d" % i
    sorter = zip(roc_x, roc_y)
    sorter.sort(reverse=True)
    roc_x, roc_y = zip(*sorter)
    lin = numpy.linspace(0, 1, len(roc_x))
    plt.plot(lin, lin)
    plt.plot(roc_x, roc_y)
    plt.show()


def visualize_multiple_roc(tps, tns, fps, fns, labels=None, title='', subplot=None):
    if not labels:
        labels = []
    if not (len(tps) == len(tns) and len(tps) == len(fps) and len(tps) == len(fns)):
        logging.error(
            'Error: Cannot build ROC with unequal length input arrays. Confirm lengths of arrays and try again.')
    roc_x = []
    for k in range(0, len(tps)):
        tp = tps[k]
        tn = tns[k]
        fp = fps[k]
        fn = fns[k]
        if not (len(tp) == len(tn) and len(tp) == len(fp) and len(tp) == len(fn)):
            logging.error(
                'Error: Cannot build ROC with unequal length input arrays. Confirm lengths of arrays and try again.')
        roc_x = []
        roc_y = []
        for i in range(0, len(tp)):
            if tp[i] == '':
                continue
            try:
                fpr = fp[i] / (fp[i] + tn[i])
                tpr = tp[i] / (tp[i] + fn[i])
                roc_x.append(fpr)
                roc_y.append(tpr)
            except ZeroDivisionError:
                print "Div 0 at i=%d" % i
        sorter = zip(roc_x, roc_y)
        sorter.sort()
        roc_x, roc_y = zip(*sorter)
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.title(title)
        if not subplot:
                f = plt.figure()
                ax = f.add_subplot(1, 1, 1, title=title)
        else:
            ax = subplot[0].add_subplot(subplot[1], subplot[2], subplot[3], title=title)
        if labels:
            ax.plot(roc_x, roc_y, label=labels[k % len(labels)])
        else:
            ax.plot(roc_x, roc_y, color='g')
    lin = numpy.linspace(0, 1, len(roc_x))
    ax.plot(lin, lin, color='k')
    if labels:
        ax.legend(loc=4)
    if not subplot:
        plt.title(title)
        plt.show()


def merge_function_pairs(x1, y1, x2, y2):
    first_index = 0
    second_index = 0
    x_new = []
    y1_new = []
    y2_new = []
    while first_index < len(x1) and second_index < len(x2):
        y1_new.append(y1[first_index])
        y2_new.append(y2[second_index])
        if x1[first_index] == x2[second_index]:
            x_new.append(x1[first_index])
            first_index += 1
            second_index += 1
        elif x1[first_index] < x2[second_index]:
            x_new.append(x1[first_index])
            first_index += 1
        elif x1[first_index] > x2[second_index]:
            x_new.append(x2[second_index])
            second_index += 1
    return x_new, y1_new, y2_new


def visualize_min_max_middle_roc(tps, tns, fps, fns, labels=None, axis_labels=None, title='', subplot=None):
    if not labels:
        labels = []
    if len(tps) != 3 or len(tns) != 3 or len(fps) != 3 or len(fns) != 3 or len(labels) != 3:
        logging.error("visualize_min_max_middle_roc requires 3 of each of the input elements (min, middle, max).")
        return
    min_x = []
    max_x = []
    min_y = []
    max_y = []
    roc_x = []
    manual_colors = ['#aaaaaa', '#666666', '#222222']
    for k in range(0, len(tps)):
        tp = tps[k]
        tn = tns[k]
        fp = fps[k]
        fn = fns[k]
        if not (len(tp) == len(tn) and len(tp) == len(fp) and len(tp) == len(fn)):
            logging.error(
                'Error: Cannot build ROC with unequal length input arrays. Confirm lengths of arrays and try again.')
        roc_x = []
        roc_y = []
        for i in range(0, len(tp)):
            if tp[i] == '':
                continue
            try:
                fpr = fp[i] / (fp[i] + tn[i])
                tpr = tp[i] / (tp[i] + fn[i])
                roc_x.append(fpr)
                roc_y.append(tpr)
            except ZeroDivisionError:
                print "Div 0 at i=%d" % i
        sorter = zip(roc_x, roc_y)
        sorter.sort()
        roc_x, roc_y = zip(*sorter)
        if not subplot:
            f = plt.figure()
            ax = f.add_subplot(1, 1, 1, title=title)
        else:
            ax = subplot[0].add_subplot(subplot[1], subplot[2], subplot[3], title=title)
        if not axis_labels:
            ax.set_xlabel('False Positive Rate')
            ax.set_ylabel('True Positive Rate')
        else:
            ax.set_xlabel(axis_labels[0])
            ax.set_ylabel(axis_labels[1])
        if k == 0:
            min_x = roc_x
            min_y = roc_y
        elif k == 2:
            max_x = roc_x
            max_y = roc_y
        if labels:
            ax.plot(roc_x, roc_y, label=labels[k % len(labels)], color=manual_colors[k])
        else:
            ax.plot(roc_x, roc_y, color='g')
    x, y1, y2 = merge_function_pairs(min_x, min_y, max_x, max_y)
    ax.fill_between(x, y1, y2, color='gray', alpha=0.5)
    lin = numpy.linspace(0, 1, len(roc_x))
    ax.plot(lin, lin, color='#000000', linestyle='--')
    if labels:
        ax.legend(loc=4)
    if not subplot:
        ax.title(title)
        ax.show()


def visualize_lines(meta_filename, x_var_col_index=4, y_var_col_index=8, line_var_col_index=5, show_score=True,
                    title=''):
    file_p = open(meta_filename, 'rb')
    header = file_p.readline()
    col_names = header.split(',')
    reader = csv.reader(file_p, delimiter=',', quoting=csv.QUOTE_NONNUMERIC)
    correctnesses = []
    orders = []
    freqs = []
    scores = []
    for row in reader:
        correctnesses.append(row[10:-1])
        orders.append(row[line_var_col_index])
        freqs.append(row[x_var_col_index])
        scores.append(row[y_var_col_index])

    sorter = zip(orders, freqs, scores)
    sorter.sort()
    orders, freqs, scores = zip(*sorter)

    seen = set()
    seen_add = seen.add
    unique_orders = [x for x in orders if not (x in seen or seen_add(x))]
    num_orders = len(unique_orders)
    freq_by_order = []
    for i in range(num_orders):
        freq_by_order.append([])
    score_by_order = []
    for i in range(num_orders):
        score_by_order.append([])

    for i in range(0, len(freqs)):
        freq_by_order[unique_orders.index(orders[i])].append(freqs[i])
        score_by_order[unique_orders.index(orders[i])].append(scores[i])

    score_max = []
    freq_max = []
    report_strs = []
    for i in range(0, len(freq_by_order)):
        score_max_index = numpy.argmax(score_by_order[i])
        score_max.append(score_by_order[i][score_max_index])
        freq_max.append(freq_by_order[i][score_max_index])
        report_strs.append("S: " + str(score_max[i]) + ", f: " + str(freq_max[i]))
    print "Order Bests: " + str(report_strs)

    if show_score:
        color_idx = numpy.linspace(0, 1, len(freq_by_order))
        for i in range(0, len(freq_by_order)):
            plt.plot(freq_by_order[i], score_by_order[i],
                     label="%s %f" % (col_names[line_var_col_index], unique_orders[i]),
                     color=plt.get_cmap('Accent')(color_idx[i]))
        plt.legend()
    plt.savefig(meta_filename + ".png")
    plt.title(title)
    plt.show()


def visualize_heatmap(meta_filename, x_var_col_index=4, y_var_col_index=3, z_var_col_index=8, constraints=None,
                      subplot=None, show_points=False,
                      title='', fixed_z_scale=None, labels=None, cmap=plt.cm.gray_r):
    file_p = open(meta_filename, 'rb')
    file_p.readline()
    # If headers are wanted, comment line above and uncomment lines below
    # header = file_p.readline()
    # col_names = header.split(',')
    reader = csv.reader(file_p, delimiter=',', quoting=csv.QUOTE_NONNUMERIC)
    y = []
    x = []
    z = []
    for row in reader:
        if not constraints:
            x.append(row[x_var_col_index])
            y.append(row[y_var_col_index])
            z.append(row[z_var_col_index])
        else:
            satisfied = True
            for i in range(0, len(constraints)):
                satisfied = satisfied and (float(row[constraints[i][0]]) == float(constraints[i][1]))
            if satisfied:
                x.append(row[x_var_col_index])
                y.append(row[y_var_col_index])
                z.append(row[z_var_col_index])

    if len(x) == 0:
        logging.error("No values satisfy constraints or no values exist.")
        return

    if not subplot:
        f = plt.figure()
        ax = f.add_subplot(1, 1, 1, title=title)
    else:
        ax = subplot[0].add_subplot(subplot[1], subplot[2], subplot[3], title=title)
    ax.set_yscale('log')
    ax.set_autoscaley_on(False)
    ax.set_autoscalex_on(False)
    ax.set_xlim([min(x), max(x)])
    ax.set_ylim([min(y), max(y)])
    if fixed_z_scale:
        cs = ax.tricontourf(x, y, z, 20, cmap=cmap, levels=numpy.linspace(fixed_z_scale[0], fixed_z_scale[1],
                                                                          20))  # choose 20 contour levels, just to show how good its interpolation is
    else:
        cs = ax.tricontourf(x, y, z, 20,
                            cmap=cmap)  # choose 20 contour levels, just to show how good its interpolation is
        print cs.levels
    cbar = plt.colorbar(cs, ticks=cs.levels, format='%.4f')
    if labels:
        ax.set_xlabel(labels[0])
        ax.set_ylabel(labels[1])
        cbar.set_label(labels[2], rotation=270, labelpad=20)
    if show_points:
        ax.plot(x, y, 'kx ')
    if not subplot:
        plt.savefig(meta_filename + ".png")
        plt.title(title)
        plt.show()


data_dir = clean_dir_ending(r'C:\Users\Kevin\Desktop\Work\Validation Output')
output_dir = clean_dir_ending(r'C:\Users\Kevin\Desktop\Work\Optimization Results')

files = get_files_in_dir([data_dir])

ictal_filenames = [s for s in files if 'inter' not in s]
interictal_filenames = [s for s in files if 'inter' in s]

'''This section has a variety of commands which can be run using the above analysis tools'''


# Commands for optimizing data files
# optimize(output_dir + r'worst.csv', ictal_filenames, interictal_filenames, enable_binning=False, bin_num=0, bin_size=100)
# optimize(output_dir + r'worst_dog1.csv', ictal_filenames, interictal_filenames, enable_binning=True, bin_num=0, bin_size=100)
# optimize(output_dir + r'worst_dog2.csv', ictal_filenames, interictal_filenames, enable_binning=True, bin_num=1, bin_size=100)
# optimize(output_dir + r'worst_dog3.csv', ictal_filenames, interictal_filenames, enable_binning=True, bin_num=2, bin_size=100)
# optimize(output_dir + r'worst_dog4.csv', ictal_filenames, interictal_filenames, enable_binning=True, bin_num=3, bin_size=100)


# Commands for outputting multiple heatmaps on same plot (uncomment sections 1 and 3 plus desired section 2 elements)
# Section 1, create a figure
# f = plt.figure(figsize=(25, 10))

# Section 2, specify heatmaps
# visualize_heatmap(output_dir + r'carrier_frequency_order_2_3.csv', constraints=[[5, 2]], subplot=[f, 1, 2, 1], title='All Dogs Order 2', labels=['Lowpass Filter Cutoff Frequency (Hz)', 'VCO Carrier Frequency (Hz)', 'Accuracy'], fixed_z_scale=[0.655, 0.745])
# visualize_heatmap(output_dir + r'carrier_frequency_order_2_3_dog1.csv', constraints=[[5, 2]], subplot=[f, 1, 2, 1], title='Dog 1 Order 2', labels=['Lowpass Filter Cutoff Frequency (Hz)', 'VCO Carrier Frequency (Hz)', 'Accuracy'], fixed_z_scale=[0.824, 0.912])
# visualize_heatmap(output_dir + r'carrier_frequency_order_2_3_dog2.csv', constraints=[[5, 2]], subplot=[f, 1, 2, 1], title='Dog 2 Order 2', labels=['Lowpass Filter Cutoff Frequency (Hz)', 'VCO Carrier Frequency (Hz)', 'Accuracy'], fixed_z_scale=[0.51, 0.825])
# visualize_heatmap(output_dir + r'carrier_frequency_order_2_3_dog3.csv', constraints=[[5, 2]], subplot=[f, 1, 2, 1], title='Dog 3 Order 2', labels=['Lowpass Filter Cutoff Frequency (Hz)', 'VCO Carrier Frequency (Hz)', 'Accuracy'], fixed_z_scale=[0.948, 0.986])
# visualize_heatmap(output_dir + r'carrier_frequency_order_2_3_dog4.csv', constraints=[[5, 2]], subplot=[f, 1, 2, 1], title='Dog 4 Order 2', labels=['Lowpass Filter Cutoff Frequency (Hz)', 'VCO Carrier Frequency (Hz)', 'Accuracy'], fixed_z_scale=[0.576, 0.76])

# visualize_heatmap(output_dir + r'carrier_frequency_order_3.csv', constraints=[[5, 3]], subplot=[f, 1, 2, 2], title='All Dogs Order 3', labels=['Lowpass Filter Cutoff Frequency (Hz)', 'VCO Carrier Frequency (Hz)', 'Accuracy'], fixed_z_scale=[0.655, 0.745])
# visualize_heatmap(output_dir + r'carrier_frequency_order_3_dog1.csv', constraints=[[5, 3]], subplot=[f, 1, 2, 2], title='Dog 1 Order 3', labels=['Lowpass Filter Cutoff Frequency (Hz)', 'VCO Carrier Frequency (Hz)', 'Accuracy'], fixed_z_scale=[0.824, 0.912])
# visualize_heatmap(output_dir + r'carrier_frequency_order_3_dog2.csv', constraints=[[5, 3]], subplot=[f, 1, 2, 2], title='Dog 2 Order 3', labels=['Lowpass Filter Cutoff Frequency (Hz)', 'VCO Carrier Frequency (Hz)', 'Accuracy'], fixed_z_scale=[0.51, 0.825])
# visualize_heatmap(output_dir + r'carrier_frequency_order_3_dog3.csv', constraints=[[5, 3]], subplot=[f, 1, 2, 2], title='Dog 3 Order 3', labels=['Lowpass Filter Cutoff Frequency (Hz)', 'VCO Carrier Frequency (Hz)', 'Accuracy'], fixed_z_scale=[0.948, 0.986])
# visualize_heatmap(output_dir + r'carrier_frequency_order_3_dog4.csv', constraints=[[5, 3]], subplot=[f, 1, 2, 2], title='Dog 4 Order 3', labels=['Lowpass Filter Cutoff Frequency (Hz)', 'VCO Carrier Frequency (Hz)', 'Accuracy'], fixed_z_scale=[0.576, 0.76])

# Figure try
# visualize_heatmap(output_dir + r'carrier_frequency_order_2_3_dog1.csv', constraints=[[5, 2]], subplot=[f, 2, 4, 1], title='Dog 1 Order 2', labels=['', 'VCO Carrier Frequency (Hz)', ''], fixed_z_scale=[0.824, 0.912])
# visualize_heatmap(output_dir + r'carrier_frequency_order_2_3_dog2.csv', constraints=[[5, 2]], subplot=[f, 2, 4, 2], title='Dog 2 Order 2', labels=['', '', ''], fixed_z_scale=[0.51, 0.825])
# visualize_heatmap(output_dir + r'carrier_frequency_order_2_3_dog3.csv', constraints=[[5, 2]], subplot=[f, 2, 4, 3], title='Dog 3 Order 2', labels=['', '', ''], fixed_z_scale=[0.948, 0.986])
# visualize_heatmap(output_dir + r'carrier_frequency_order_2_3_dog4.csv', constraints=[[5, 2]], subplot=[f, 2, 4, 4], title='Dog 4 Order 2', labels=['', '', 'Accuracy'], fixed_z_scale=[0.576, 0.76])
# visualize_heatmap(output_dir + r'carrier_frequency_order_3_dog1.csv', constraints=[[5, 3]], subplot=[f, 2, 4, 5], title='Dog 1 Order 3', labels=['Lowpass Filter Cutoff Frequency (Hz)', 'VCO Carrier Frequency (Hz)', ''], fixed_z_scale=[0.824, 0.912])
# visualize_heatmap(output_dir + r'carrier_frequency_order_3_dog2.csv', constraints=[[5, 3]], subplot=[f, 2, 4, 6], title='Dog 2 Order 3', labels=['Lowpass Filter Cutoff Frequency (Hz)', '', ''], fixed_z_scale=[0.51, 0.825])
# visualize_heatmap(output_dir + r'carrier_frequency_order_3_dog3.csv', constraints=[[5, 3]], subplot=[f, 2, 4, 7], title='Dog 3 Order 3', labels=['Lowpass Filter Cutoff Frequency (Hz)', '', ''], fixed_z_scale=[0.948, 0.986])
# visualize_heatmap(output_dir + r'carrier_frequency_order_3_dog4.csv', constraints=[[5, 3]], subplot=[f, 2, 4, 8], title='Dog 4 Order 3', labels=['Lowpass Filter Cutoff Frequency (Hz)', '', 'Accuracy'], fixed_z_scale=[0.576, 0.76])

# Section 3, layout figure and show
# plt.tight_layout()
# plt.show()


# Commands for optimizing final parameter checks
# optimize(output_dir + r'final_param_check.csv', ictal_filenames, interictal_filenames, bin=False, bin_num=0, bin_size=100)
# optimize(output_dir + r'final_param_check_dog1.csv', ictal_filenames, interictal_filenames, bin=True, bin_num=0, bin_size=100)
# optimize(output_dir + r'final_param_check_dog2.csv', ictal_filenames, interictal_filenames, bin=True, bin_num=1, bin_size=100)
# optimize(output_dir + r'final_param_check_dog3.csv', ictal_filenames, interictal_filenames, bin=True, bin_num=2, bin_size=100)
# optimize(output_dir + r'final_param_check_dog4.csv', ictal_filenames, interictal_filenames, bin=True, bin_num=3, bin_size=100)

# Commands for original ROC visualization with all 5 bests for each order displayed together
# tp, tn, fp, fn = load_roc_arrays(r'C:\Users\Kevin\Desktop\roc_order_2_best.csv')
# visualize_multiple_roc(tp, tn, fp, fn, labels=['All Dogs', 'Dog 1', 'Dog 2', 'Dog 3', 'Dog 4'], title="Filter Order 2")

# tp, tn, fp, fn = load_roc_arrays(r'C:\Users\Kevin\Desktop\roc_order_3_best.csv')
# visualize_multiple_roc(tp, tn, fp, fn, labels=['All Dogs', 'Dog 1', 'Dog 2', 'Dog 3', 'Dog 4'], title="Filter Order 3")

# Commands for outputting multiple ROCs on same plot (uncomment sections 1 and 3 plus desired section 2 elements)
# Section 1, create a figure
f = plt.figure(figsize=(25, 10))

# Section 2, specify ROCs
# Commands for new ROC visualization with each individual order/dog best/worst/group optimized together
tp, tn, fp, fn = load_roc_arrays(r'C:\Users\Kevin\Google Drive\School\Projects\PLL\Paper Figures\roc\roc_order_2_dog_1.csv')
visualize_min_max_middle_roc(tp, tn, fp, fn, labels=['Worst', 'Group Optimized', 'Best'], axis_labels=['', 'True Positive Rate'], title="Dog 1 Order 2", subplot=[f, 2, 4, 1])

tp, tn, fp, fn = load_roc_arrays(r'C:\Users\Kevin\Google Drive\School\Projects\PLL\Paper Figures\roc\roc_order_2_dog_2.csv')
visualize_min_max_middle_roc(tp, tn, fp, fn, labels=['Worst', 'Group Optimized', 'Best'], axis_labels=['', ''], title="Dog 2 Order 2", subplot=[f, 2, 4, 2])

tp, tn, fp, fn = load_roc_arrays(r'C:\Users\Kevin\Google Drive\School\Projects\PLL\Paper Figures\roc\roc_order_2_dog_3.csv')
visualize_min_max_middle_roc(tp, tn, fp, fn, labels=['Worst', 'Group Optimized', 'Best'], axis_labels=['', ''], title="Dog 3 Order 2", subplot=[f, 2, 4, 3])

tp, tn, fp, fn = load_roc_arrays(r'C:\Users\Kevin\Google Drive\School\Projects\PLL\Paper Figures\roc\roc_order_2_dog_4.csv')
visualize_min_max_middle_roc(tp, tn, fp, fn, labels=['Worst', 'Group Optimized', 'Best'], axis_labels=['', ''], title="Dog 4 Order 2", subplot=[f, 2, 4, 4])


tp, tn, fp, fn = load_roc_arrays(r'C:\Users\Kevin\Google Drive\School\Projects\PLL\Paper Figures\roc\roc_order_3_dog_1.csv')
visualize_min_max_middle_roc(tp, tn, fp, fn, labels=['Worst', 'Group Optimized', 'Best'], axis_labels=['False Positive Rate', 'True Positive Rate'], title="Dog 1 Order 3", subplot=[f, 2, 4, 5])

tp, tn, fp, fn = load_roc_arrays(r'C:\Users\Kevin\Google Drive\School\Projects\PLL\Paper Figures\roc\roc_order_3_dog_2.csv')
visualize_min_max_middle_roc(tp, tn, fp, fn, labels=['Worst', 'Group Optimized', 'Best'], axis_labels=['False Positive Rate', ''], title="Dog 2 Order 3", subplot=[f, 2, 4, 6])

tp, tn, fp, fn = load_roc_arrays(r'C:\Users\Kevin\Google Drive\School\Projects\PLL\Paper Figures\roc\roc_order_3_dog_3.csv')
visualize_min_max_middle_roc(tp, tn, fp, fn, labels=['Worst', 'Group Optimized', 'Best'], axis_labels=['False Positive Rate', ''], title="Dog 3 Order 3", subplot=[f, 2, 4, 7])

tp, tn, fp, fn = load_roc_arrays(r'C:\Users\Kevin\Google Drive\School\Projects\PLL\Paper Figures\roc\roc_order_3_dog_4.csv')
visualize_min_max_middle_roc(tp, tn, fp, fn, labels=['Worst', 'Group Optimized', 'Best'], axis_labels=['False Positive Rate', ''], title="Dog 4 Order 3", subplot=[f, 2, 4, 8])

# Section 3, layout figure and show
# plt.tight_layout()
plt.show()

# Commands for optimizing final parameter checks
# test(19.04174239, output_dir + r'validation_order3_max.csv', ictal_filenames, interictal_filenames, enable_binning=False, bin_num=0, bin_size=50)
# test(36.50667746, output_dir + r'validation_dog1_order3_max.csv', ictal_filenames, interictal_filenames, enable_binning=True, bin_num=0, bin_size=50)
# test(10.44726796, output_dir + r'validation_dog2_order3_max.csv', ictal_filenames, interictal_filenames, enable_binning=True, bin_num=1, bin_size=50)
# test(5.055105062, output_dir + r'validation_dog3_order3_max.csv', ictal_filenames, interictal_filenames, enable_binning=True, bin_num=2, bin_size=50)
# test(5.905523785, output_dir + r'validation_dog4_order3_max.csv', ictal_filenames, interictal_filenames, enable_binning=True, bin_num=3, bin_size=50)

# test(18.23979995, output_dir + r'validation_order2_max.csv', ictal_filenames, interictal_filenames, enable_binning=False, bin_num=0, bin_size=50)
# test(66.26801104, output_dir + r'validation_dog1_order2_max.csv', ictal_filenames, interictal_filenames, enable_binning=True, bin_num=0, bin_size=50)
# test(12.09231881, output_dir + r'validation_dog2_order2_max.csv', ictal_filenames, interictal_filenames, enable_binning=True, bin_num=1, bin_size=50)
# test(4.849560335, output_dir + r'validation_dog3_order2_max.csv', ictal_filenames, interictal_filenames, enable_binning=True, bin_num=2, bin_size=50)
# test(5.923866524, output_dir + r'validation_dog4_order2_max.csv', ictal_filenames, interictal_filenames, enable_binning=True, bin_num=3, bin_size=50)

# test(3.166956224, output_dir + r'validation_dog1_order2_min.csv', ictal_filenames, interictal_filenames, enable_binning=True, bin_num=0, bin_size=50)
# test(15.90808099, output_dir + r'validation_dog2_order2_min.csv', ictal_filenames, interictal_filenames, enable_binning=True, bin_num=1, bin_size=50)
# test(17.4370032, output_dir + r'validation_dog3_order2_min.csv', ictal_filenames, interictal_filenames, enable_binning=True, bin_num=2, bin_size=50)
# test(229.934675, output_dir + r'validation_dog4_order2_min.csv', ictal_filenames, interictal_filenames, enable_binning=True, bin_num=3, bin_size=50)
# test(4.579139712, output_dir + r'validation_dog1_order3_min.csv', ictal_filenames, interictal_filenames, enable_binning=True, bin_num=0, bin_size=50)
# test(59.47652158, output_dir + r'validation_dog2_order3_min.csv', ictal_filenames, interictal_filenames, enable_binning=True, bin_num=1, bin_size=50)
# test(18.38598471, output_dir + r'validation_dog3_order3_min.csv', ictal_filenames, interictal_filenames, enable_binning=True, bin_num=2, bin_size=50)
# test(187.5238623, output_dir + r'validation_dog4_order3_min.csv', ictal_filenames, interictal_filenames, enable_binning=True, bin_num=3, bin_size=50)
