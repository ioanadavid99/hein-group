"""
a script to collect data from the Quantos in order to test reproducibility

Author(s):      Ioana David
Last modified:  Mar. 13th, 2020

"""
from quantos.api import Quantos
import json
import os
import csv
from quantos.data import SampleData
from unithandler.base import UnitFloat

quan = Quantos(address='10.0.0.1', logging_level=10)

# setting json file path to save to
cur_dir = os.path.abspath(os.path.curdir)
DATA_FILE_PATH = os.path.join(cur_dir, 'quantos_data.json')


def change_mass_and_dispense(target_mass):
    """
    PURPOSE     update the target mass (mg), dispense powder
    PARAMETERS  target mass: sets the desired target mass (mg) for the quantos to dispense
    RETURN      the sample data (quantity dispensed, in mg)
    """
    quan.target_mass = target_mass
    quan.start_dosing(wait_for=True)
    x = quan.sample_data.quantity        # making sure that we have the correct numbers coming out, nothing's jumbled
    return float(x)      # type conversion to make sure we can use the information


def run_script(json_file_name):
    """
    PURPOSE     runs experiments with the user inputting their desired lower & upper mass, increment, and number of trials
    PARAMETER   the name of the JSON file in which you store the data
    RETURN      a list of all of the desired masses passed to the function, as well as the number of trials for each

    """
    stored_data = {}        # empty dictionary to store everything
    list_data = []
    percent_data = []
    sum_error = 0           # initialize the variable
    cond_values = []

    run_experiment = True

    while run_experiment:
        lower_mass = int(input("Lower mass (mg): "))
        while lower_mass <= 0:
            lower_mass = int(input("Error: lower mass cannot be less than, or equal to 0. Please enter a new value (mg): "))
        upper_mass = int(input("Upper mass (mg): "))
        while upper_mass < lower_mass:
            upper_mass = int(input("Upper mass cannot be lower than lower mass. Please enter a new value (mg): "))
        if upper_mass > lower_mass:
            increment = int(input("Mass (mg) by which to increment: "))
        if upper_mass == lower_mass:
            increment = 1
        while lower_mass + increment > upper_mass & upper_mass != lower_mass:
            increment = int(input("Increment is invalid, please enter a new value (mg): "))
        iterations = int(input("Number of trials: "))
        mass = lower_mass
        count = 0
        while mass <= upper_mass:
            count += 1
            mass += increment
        cond_values.append(count)       # this is the number of conditions
        mass = lower_mass
        while mass <= upper_mass:
            cond_values.append(mass)
            # print("mass:", mass)
            mass += increment
        cond_values.append(iterations)

        for desired_mass in range(lower_mass, upper_mass + 1, increment):
            for i in range(0, iterations):
                sample_data = change_mass_and_dispense(desired_mass)
                list_data.insert(i, sample_data)
                percent_error = abs((sample_data - desired_mass) / desired_mass)
                percent_data.insert(i, percent_error)
            for j in range(0, iterations):      # calculate the average percent error
                sum_error += percent_data[j]
                if j == (iterations - 1):
                    avg_error = sum_error / iterations
                    list_data.insert(iterations, avg_error)  # add the avg % error to the end of the list
                    stored_data.update({desired_mass: list_data[0:(iterations + 1)]})  # append the dictionary
        with open(json_file_name, 'w') as file:
            json.dump(stored_data, file)
        run_experiment = input("run experiment again? TRUE (yes) or FALSE (no): ")
        if run_experiment == 'FALSE':
            break
        if run_experiment == 'no':
            break
        if run_experiment == 'yes':
            run_experiment = True
        if run_experiment == 'TRUE':
            run_experiment = True
        with open(json_file_name, 'a') as file:
            json.dump(stored_data, file)
    print("\nexiting experiment ... ")
    print("Stored data:", stored_data)  # debugging
    return cond_values


def create_json_file_path():
    """
    PURPOSE    gets the file path of the json file
    PARAMETER   none
    RETURN     the name of the json file (str)

    credit: veronica lai
    source: https://gitlab.com/heingroup/ika/-/blob/master/ika/tests/json_utilities.py
    """
    count = True
    get_json_file_name = True
    print("If you do not already have a JSON file created, enter your desired names in the prompt below and they will be automatically made and stored in the same folder as this script.")
    print("If you have a JSON file already made and would like to use those (overwriting their contents), enter their names below when prompted.")
    while get_json_file_name:
        json_file_name = input("What is the name of your JSON file? ")
        if json_file_name[-4:] != '.json':
            json_file_name += '.json'
        print("Your JSON file is:", json_file_name)
        response = input("Confirm JSON file name with a yes/no (case sensitive): ")
        if response == 'yes':
            get_json_file_name = False
        else:
            get_json_file_name = True
    return json_file_name


def create_csv_file_path():
    """
    PURPOSE     creates a file path to a CSV file
    PARAMETER   none
    RETURN      the name of the csv file (str)

    """
    get_csv_file_name = True
    print("If you do not already have a CSV file created, enter your desired names in the prompt below and they will be automatically made and stored in the same folder as this script.")
    print("If you have a CSV file already made and would like to use those (overwriting their contents), enter their names below when prompted.")
    while get_csv_file_name:
        csv_file_name = input("What is the name of your CSV file? ")
        if csv_file_name[-3:] != '.csv':
            csv_file_name += '.csv'
        print("Your CSV file is:", csv_file_name)
        response = input("Confirm CSV file name with a yes/no (case sensitive): ")
        if response == 'yes':
            get_csv_file_name = False
        else:
            get_csv_file_name = True
    return csv_file_name


def convert_dict_to_flat_list(json_file_name):
    """
    PURPOSE     converts the dictionaries produced in the script and stored in the JSON file to a flattened list
    PARAMETER   the json file, which contains one or more dictionaries with experimental data
    RETURN      a flattened str list made from the dictionaries in the json file
    """
    temp = []
    temp2 = []
    dict_list = []
    flat_list = []
    with open(json_file_name, 'r') as file:
        dictionary = json.load(file)
    # converts dictionary to list
    for key, value in dictionary.items():
        temp = [key, value]
        dict_list.extend(temp)          # extend vs append
    # takes care of the nested lists as those are not flattened
    for i in range(0, len(dict_list)):
        if type(dict_list[i]) == list:
            temp2 = str(dict_list[i])
            dict_list[i] = temp2[1:-1]  # get rid of the square brackets
        if type(dict_list[i]) == int:
            dict_list[i] = str(dict_list[i])
    return dict_list


def convert_flat_dict_to_list(list_str):
    """
    PURPOSE     will parse through a list with str values and convert them to int
                will look for comma separated values and assign them their own index
    PARAMETERS  list_str: a flattened list of string values
    RETURN      a float list that can be then sent to a CSV file easily :-)
    """
    final_list = []     # empty list
    for i in range(0, len(list_str)):
        temp_str = list_str[i]
        if i % 2 == 0:          # even index
            final_list.append(float(temp_str))
        else:                   # odd index
            temp_split = temp_str.split(', ')
            for j in range(0, len(temp_split)):
                temp_int = float(temp_split[j])
                final_list.append(temp_int)
    print("final_list:", final_list)
    return final_list


def list_to_csv(flat_list, cond_values, csv_file_name):
    """
    PURPOSE     takes the list of values from the JSON file, and the different condition values from the experiment script to send data to a CSV file
    PARAMETERS  flat_list:      a list of data parsed from a JSON file
                cond_values:    a list formatted in [number_of_conditions, cond_1, cond_2, ... , cond_n, number_of_trials]
                csv_file_name:  the name of the csv file we wish to send the data
    RETURN       none
    """
    mass_list = []

    with open(csv_file_name, 'w', newline="") as csv_file:
        writer = csv.writer(csv_file)
        mass_list.clear()
        num_conditions = cond_values[0]
        mass_list.extend(cond_values[1:num_conditions + 1])  # write the different condition values & the number of trials at the end
        num_trials = cond_values[-1]
        for j in range(0, len(flat_list)+2, 1):
            if j >= len(flat_list):
                j = 0
            if len(flat_list) == 0:
                break
            if mass_list[0] == flat_list[j]:      # if the number matches a desired_mass that we have sent it
                writer.writerow(flat_list[0:num_trials+2])   # this will cause a new row every time it is written
                del mass_list[0]
                # L = 0
                for L in range(0, num_trials+2):
                    del flat_list[0]            # pop the number of trials that we have successfully written


json_name = create_json_file_path()
csv_name = create_csv_file_path()
values = run_script(json_name)
flat_str_list = convert_dict_to_flat_list(json_name)
csv_dictionary = convert_flat_dict_to_list(flat_str_list)
list_to_csv(csv_dictionary, values, csv_name)
print("all done!")


# TODO - maybe add a thing where we can give a name to the powder we're using?
# like we have a string etc. so that when the data is saved to the JSON file it's easy to identify
# TODO - clarify that the values we gave it are the ones we want to use (in case we accidentally send it the wrong #)
# TODO - add titles to the headers that we're printing (eg. mass, trial #)?