import numpy as np

# carrier_frequency=params[3] # 0.01, 0.1, 0.5 to 1.5 (11), 2, 4, 8, 16, 32 ----------- 18
# lowpass_cuttoff_frequency=params[4] # 2 0.080 to 0.150; 3 0.300 to 0.410 ------------ 88
# filter_order=params[5] # 2 or 3 ----------------------------------------------------- 2

parameters = [16, 400.0, 1, 1, 0.3, 3, 100, 2]

parameter_start = 0.268
parameter_end = 0.444
num_params = 88
# parameter_step = 0.001
# points = np.linspace(parameter_start, parameter_end, ((parameter_end - parameter_start) / parameter_step) + 2)
points = np.linspace(parameter_start, parameter_end, num_params)

parameters_under_test = []
for p3 in [0.01, 0.1, 0.5, 0.6, 0.7, 0.8, 0.9, 1, 1.1, 1.2, 1.3, 1.4, 1.5, 2, 4, 8, 16, 32]:
    for p4 in points:
        test_parameter = parameters[:]
        test_parameter[3] = p3
        test_parameter[4] = p4
        test_parameter[5] = 3
        parameters_under_test.append(test_parameter)

print '\n'.join([str(s) for s in parameters_under_test])


# np.savetxt(r'C:\Users\Kevin\Google Drive\School\Projects\PLL\parameters_to_test_carrier_frequency_order3.csv', np.array(parameters_under_test), delimiter=',')


def get_parameters(filename, modulus, mod_index):
    import csv

    csv_file = csv.reader(open(filename), delimiter=',', quoting=csv.QUOTE_NONNUMERIC)
    rows = []
    index = 0
    for row in csv_file:
        if index % modulus == mod_index:
            rows.append(row)
        index += 1
    return rows


params = get_parameters(
    r'C:\Users\Kevin\Google Drive\School\Projects\PLL\parameters_to_test_carrier_frequency_order3.csv', 1, 0)
print '\n'.join([str(s) for s in params])
