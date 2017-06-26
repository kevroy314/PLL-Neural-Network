from Simulation import Simulation
from os import listdir
from os.path import isfile, join
import csv


def get_files_in_dir(directory):
    files = []
    for current_dir in directory:
        files.extend([(current_dir + f) for f in listdir(current_dir) if isfile(join(current_dir, f))])
    return files


def process_files(directory, params, conn_matrix):
    files = get_files_in_dir(directory)
    results = []
    count = 0
    for current_file in files:
        print "Processing file " + str(count) + " out of " + str(len(files))
        results.append(Simulation('', current_file,
                                  number_of_input_channels=int(params[0]), sample_rate=params[1], duration=params[2],
                                  carrier_frequency=params[3], lowpass_cuttoff_frequency=params[4],
                                  filter_order=int(params[5]), filter_window_size=int(params[6]),
                                  path_length_window_size=int(params[7]),
                                  connectivity_matrix=conn_matrix))
        count += 1
    return results


def generate_param_string(params):
    output = ""
    for current_param in params:
        output += str(current_param) + "_"
    output = output[0:-1]
    return output


'''connectivity_matrix = [[0, 0.08432127958685515, 0.08432127958685515, 0.11924829718838416, 0.1885481131059735, 0.1686425591737103, 0.266647298714324, 0.25296383876056544, 0.7988331750333647, 0.8831544546202198, 0.8032711371168835, 0.887170710126694, 0.8991118414747947, 0.8164402943868858, 0.9186688709410041, 0.837929081279775],
                               [0.08432127958685515, 0, 0.11924829718838416, 0.08432127958685515, 0.1686425591737103, 0.1885481131059735, 0.25296383876056544, 0.266647298714324, 0.8831544546202198, 0.9674757342070749, 0.887170710126694, 0.971143333638595, 0.9820639536426216, 0.8991118414747947, 1, 0.9186688709410041],
                               [0.08432127958685515, 0.11924829718838416, 0, 0.08432127958685515, 0.11924829718838416, 0.08432127958685515, 0.1885481131059735, 0.16864255917371027, 0.8032711371168835, 0.887170710126694, 0.7988331750333647, 0.8831544546202198, 0.887170710126694, 0.8032711371168835, 0.8991118414747947, 0.8164402943868858],
                               [0.11924829718838416, 0.08432127958685515, 0.08432127958685515, 0, 0.08432127958685515, 0.11924829718838416, 0.16864255917371027, 0.1885481131059735, 0.887170710126694, 0.971143333638595, 0.8831544546202198, 0.9674757342070749, 0.971143333638595, 0.887170710126694, 0.9820639536426216, 0.8991118414747947],
                               [0.1885481131059735, 0.1686425591737103, 0.11924829718838416, 0.08432127958685515, 0, 0.08432127958685515, 0.08432127958685513, 0.11924829718838414, 0.8991118414747947, 0.9820639536426216, 0.887170710126694, 0.971143333638595, 0.9674757342070749, 0.8831544546202198, 0.971143333638595, 0.887170710126694],
                               [0.1686425591737103, 0.1885481131059735, 0.08432127958685515, 0.11924829718838416, 0.08432127958685515, 0, 0.11924829718838414, 0.08432127958685513, 0.8164402943868858, 0.8991118414747947, 0.8032711371168835, 0.887170710126694, 0.8831544546202198, 0.7988331750333647, 0.887170710126694, 0.8032711371168835],
                               [0.266647298714324, 0.25296383876056544, 0.1885481131059735, 0.16864255917371027, 0.08432127958685513, 0.11924829718838414, 0, 0.08432127958685515, 0.9186688709410041, 1, 0.8991118414747947, 0.9820639536426216, 0.971143333638595, 0.887170710126694, 0.9674757342070749, 0.8831544546202198],
                               [0.25296383876056544, 0.266647298714324, 0.16864255917371027, 0.1885481131059735, 0.11924829718838414, 0.08432127958685513, 0.08432127958685515, 0, 0.837929081279775, 0.9186688709410041, 0.8164402943868858, 0.8991118414747947, 0.887170710126694, 0.8032711371168835, 0.8831544546202198, 0.7988331750333647],
                               [0.7988331750333647, 0.8831544546202198, 0.8032711371168835, 0.887170710126694, 0.8991118414747947, 0.8164402943868858, 0.9186688709410041, 0.837929081279775, 0, 0.08432127958685509, 0.08432127958685515, 0.11924829718838413, 0.18854811310597347, 0.1686425591737103, 0.26664729871432397, 0.25296383876056544],
                               [0.8831544546202198, 0.9674757342070749, 0.887170710126694, 0.971143333638595, 0.9820639536426216, 0.8991118414747947, 1, 0.9186688709410041, 0.08432127958685509, 0, 0.11924829718838413, 0.08432127958685515, 0.1686425591737103, 0.18854811310597347, 0.25296383876056544, 0.26664729871432397],
                               [0.8032711371168835, 0.887170710126694, 0.7988331750333647, 0.8831544546202198, 0.887170710126694, 0.8032711371168835, 0.8991118414747947, 0.8164402943868858, 0.08432127958685515, 0.11924829718838413, 0, 0.08432127958685509, 0.11924829718838413, 0.08432127958685515, 0.18854811310597347, 0.16864255917371027],
                               [0.887170710126694, 0.971143333638595, 0.8831544546202198, 0.9674757342070749, 0.971143333638595, 0.887170710126694, 0.9820639536426216, 0.8991118414747947, 0.11924829718838413, 0.08432127958685515, 0.08432127958685509, 0, 0.08432127958685515, 0.11924829718838413, 0.16864255917371027, 0.18854811310597347],
                               [0.8991118414747947, 0.9820639536426216, 0.887170710126694, 0.971143333638595, 0.9674757342070749, 0.8831544546202198, 0.971143333638595, 0.887170710126694, 0.18854811310597347, 0.1686425591737103, 0.11924829718838413, 0.08432127958685515, 0, 0.08432127958685509, 0.08432127958685513, 0.1192482971883841],
                               [0.8164402943868858, 0.8991118414747947, 0.8032711371168835, 0.887170710126694, 0.8831544546202198, 0.7988331750333647, 0.887170710126694, 0.8032711371168835, 0.1686425591737103, 0.18854811310597347, 0.08432127958685515, 0.11924829718838413, 0.08432127958685509, 0, 0.1192482971883841, 0.08432127958685513],
                               [0.9186688709410041, 1, 0.8991118414747947, 0.9820639536426216, 0.971143333638595, 0.887170710126694, 0.9674757342070749, 0.8831544546202198, 0.26664729871432397, 0.25296383876056544, 0.18854811310597347, 0.16864255917371027, 0.08432127958685513, 0.1192482971883841, 0, 0.08432127958685509],
                               [0.837929081279775, 0.9186688709410041, 0.8164402943868858, 0.8991118414747947, 0.887170710126694, 0.8032711371168835, 0.8831544546202198, 0.7988331750333647, 0.25296383876056544, 0.26664729871432397, 0.16864255917371027, 0.18854811310597347, 0.1192482971883841, 0.08432127958685513, 0.08432127958685509, 0]]
    '''


def batch_all_data(batch_params, input_dirs_ictal, input_dirs_interictal, output_dir):

    connectivity_matrix = [[0.5] * 16] * 16

    results_ictal = process_files(input_dirs_ictal, batch_params, connectivity_matrix)
    results_interictal = process_files(input_dirs_interictal, batch_params, connectivity_matrix)

    csv.writer(open(output_dir + 'ictal_results' + generate_param_string(batch_params) + '.csv', 'wb'), delimiter=',').writerows(results_ictal)
    csv.writer(open(output_dir + 'interictal_results' + generate_param_string(batch_params) + '.csv', 'wb'), delimiter=',').writerows(results_interictal)

# parameters = [16, 400.0, 1, 1, 0.3, 1, 100, 2]
# parameters[5] = 3
# parameter_to_range = 4
# parameter_start = 0.28
# parameter_end = 0.36
# parameter_step = 0.001
# points = np.linspace(parameter_start, parameter_end, ((parameter_end - parameter_start) / parameter_step) + 2)


def get_parameters(input_filename, modulus, mod_index):
    import csv

    csv_file = csv.reader(open(input_filename), delimiter=',', quoting=csv.QUOTE_NONNUMERIC)
    rows = []
    index = 0
    for row in csv_file:
        if index % modulus == mod_index:
            rows.append(row)
        index += 1
    return rows

config_core = 5
config_num_cores_to_use = 6

config_input_dirs_ictal = [
    r"C:\Users\Kevin\Desktop\Work\PLL Data\validation_data\dog1_ictal" + '\\',
    r"C:\Users\Kevin\Desktop\Work\PLL Data\validation_data\dog2_ictal" + '\\',
    r"C:\Users\Kevin\Desktop\Work\PLL Data\validation_data\dog3_ictal" + '\\',
    r"C:\Users\Kevin\Desktop\Work\PLL Data\validation_data\dog4_ictal" + '\\'
]
config_input_dirs_interictal = [
    r"C:\Users\Kevin\Desktop\Work\PLL Data\validation_data\dog1_interictal" + '\\',
    r"C:\Users\Kevin\Desktop\Work\PLL Data\validation_data\dog2_interictal" + '\\',
    r"C:\Users\Kevin\Desktop\Work\PLL Data\validation_data\dog3_interictal" + '\\',
    r"C:\Users\Kevin\Desktop\Work\PLL Data\validation_data\dog4_interictal" + '\\'
]

config_output_dir = r'C:\Users\Kevin\Desktop\Work\Validation Output' + '\\'

config_parameter_list_file = r'C:\Users\Kevin\Google Drive\School\Projects\PLL\parameters_to_test.csv'


params_under_test = get_parameters(config_parameter_list_file, config_num_cores_to_use, config_core)

existing_files = get_files_in_dir([config_output_dir])

for p in params_under_test:
    param_str = generate_param_string(p)
    file_found = False
    for filename in existing_files:
        p2 = p[0]
        if param_str in filename:
            print 'Skipping parameters ' + str(param_str) + ' because they have already been run.'
            file_found = True
    if not file_found:
        batch_all_data(p, config_input_dirs_ictal, config_input_dirs_interictal, config_output_dir)
