# source: https://plot.ly/python/line-and-scatter/
# author: Ioana David

import plotly.graph_objects as go
import pandas as pd
import os
import csv
import aghplctools
from aghplctools.ingestion import text
from aghplctools import hplc
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import QDate, QTime


def create_csv_file_path():
    """
    :return the name of the CSV file
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


def xlsx_to_csv(full_path):
    """
    :param full_path: the location where the CSV file will be created
    :return the directory of the CSV file
    """
    excel_file_name = 'push_volumes.xlsx'
    xlsx_len = len(excel_file_name)
    xlsx_directory = input("Please enter the directory where your push_volumes.xlsx file is located:\n")
    if xlsx_directory[-xlsx_len:0] != excel_file_name:
        xlsx_directory = os.path.join(xlsx_directory, excel_file_name)
    file_info = xlsx_directory[-(20 + xlsx_len):-xlsx_len-1]
    csv_file_name = file_info + ' push_volumes.csv'
    data_xls = pd.read_excel(xlsx_directory, 'Sheet1', index_col=False, index=False, row_names=False)
    csv_directory = os.path.join(full_path, csv_file_name)
    data_xls.to_csv(csv_directory, encoding='utf-8', index=False)
    return csv_directory


def get_csv_file_path(csv_dir):
    """
    :param csv_dir: the location of the CSV file
    :return: the full directory to the CSV file, including the name
    """
    csv_name = "push_volumes.csv"
    csv_len = len(csv_name)
    if csv_dir[-csv_len:0] != csv_name:
        csv_file_path = os.path.join(csv_dir, csv_name)
    return csv_file_path


def get_directory_name(des_date, des_time):
    """
    :param des_date: the date of the experiment, str
    :param des_time: the time of the experiment, str
    :return: the path to the master folder through which to parse
    """
    master_directory = '/Users/idavi/OneDrive/Desktop/hein lab/HPLC data/'
    # todo - determine what the master directory is on the lab computer
    exp_folder = f"PS_pushramp {des_date} {des_time}"
    path = os.path.join(master_directory, des_date)
    full_path = os.path.join(path, exp_folder)
    return full_path


def create_text_file(full_path):
    """
    :param full_path: the path to the master folder
    :return: the path to the text file in the master folder
    """
    text_path = f"{full_path[-19:]} directory_names.txt"
    full_text_file_path = os.path.join(full_path, text_path)
    # text_file = open(full_text_file_path, 'w')
    return full_text_file_path


def pywalker(full_path, full_text_file_path):
    """
    :param full_path: the path to the master folder
    :param full_text_file_path: the path of the text file that stores the data

    :purpose: finds all of the instances of desired_file and writes the directories to a text file
    """
    desired_file = 'Report.TXT'
    for root, dirs, files in os.walk(full_path):
        for file_ in files:
            complete_name = os.path.join(root, file_)
            if file_ == desired_file:
                text_file = open(full_text_file_path, 'a')
                text_file.write(f'{complete_name}\n')


def get_retention_time():
    """
    :param: none
    :return: the retention time, to a precision of three digits
    """
    run_again = True
    desired_ret_time = float(input("Please enter your desired retention time, in minutes, to a precision of 3 decimal places:\n"))
    while run_again:
        confirm_response = input(f"Please confirm your retention time of <<{desired_ret_time}>> with a yes or no (case-sensitive)\n")
        if confirm_response == 'yes':
            run_again = False
            return desired_ret_time
        else:
            desired_ret_time = float(input("Please enter your desired retention time, in minutes, to a precision of 3 decimal places:\n"))
            run_again = True


def get_flexibility_time():
    """
    :return: the range in which the retention time will be considered valid
    """
    desired_flex_time = float(input("Please enter your desired retention time flexibility, in minutes, to a precision of 3 decimal places:\n"))
    run_again = True
    while run_again:
        confirm_response = input(f"Please confirm your retention time of <<{desired_flex_time}>> with a yes or no (case-sensitive)\n")
        if confirm_response == 'yes':
            run_again = False
            return desired_flex_time
        else:
            desired_flex_time = float(input("Please enter your desired retention time flexibility, in minutes, to a precision of 3 decimal places:\n"))
            run_again = True


def parse_dict(complete_name, ret_time, flex_time, signal):
    """
    :param complete_name: the path to the file in which we are interested
    :param ret_time: the retention time in which we are interested, with 3 decimal places
    :param flex_time: the flexibility to be considered when looking at the retention times
    :param signal: the wavelength we are interested in
    :return area: the area associated with that retention time
    :return actual_ret_time: the actual retention time (ie. the retention time within the bounds)
    """
    dictionary = aghplctools.ingestion.text.pull_hplc_area_from_txt(filename=complete_name)
    values = aghplctools.hplc.HPLCTarget(wavelength=signal, retention_time=ret_time, wiggle=flex_time).add_from_pulled(dictionary)
    area = values[0]    # this gets just the area
    signal_values = dictionary.get(signal)
    keys = tuple(signal_values.keys())
    for i in (0, len(keys)-1):
        upper_bound = ret_time + flex_time
        lower_bound = ret_time - flex_time
        if (keys[i] >= lower_bound) & (keys[i] <= upper_bound):
            actual_ret_time = keys[i]
            return area, actual_ret_time
        else:
            actual_ret_time = None
            return area, actual_ret_time

    # return area, actual_ret_time


def write_to_csv(des_date, des_time, des_ret_time, des_flex_time, des_signal, csv_dir):
    """
    :param des_time: the desired time, str
    :param des_date: the desired date, str
    :param des_ret_time: the desired retention time, float
    :param des_flex_time: the desired flex time, float
    :param des_signal: the desired signal, int
    :param csv_dir: directory of the CSV file containing the push volumes
    :return: the directory of the CSV file that contains all of the information we need to graph
    """
    # constant variables - do not change while in the loop
    # todo - make these inputs external to the method
    full_path = get_directory_name(des_date, des_time)
    csv_file_name = full_path + '/graph_data.csv'
    full_text_file_path = create_text_file(full_path)           # creates a text file in which we store the directory names through which we wish to parse
    pywalker(full_path, full_text_file_path)                    # populates the text file with the directories
    push_vol_dir = get_csv_file_path(csv_dir)                     # creates a CSV file & returns the path
    with open(csv_file_name, 'w', newline='') as csv_file:
        writer = csv.writer(csv_file, delimiter=",")
        writer.writerow(["retention time", "area", "push volume", "directory"])
    with open(push_vol_dir, 'r') as push_vol_file:
        rows = list(csv.reader(push_vol_file, delimiter=","))
        push_vol_rows = [val for sublist in rows for val in sublist]    # flatten the list
    with open(full_text_file_path, 'r') as txt_file:
        count = 1
        for line in txt_file:
            directory = line.strip('\n')
            short_dir = directory[49:-25]
            area, actual_ret_time = parse_dict(directory, des_ret_time, des_flex_time, des_signal)
            if (area != None) & (actual_ret_time != None):
                push_vol = int(push_vol_rows[count])
                count += 1
                if count >= len(push_vol_rows):
                    break
                with open(csv_file_name, 'a', newline='') as csv_file:
                    # todo - check the condition where the retention time doesn't fall within bounds
                    # todo - update what part of the directory gets written (interested in day, time + folder)
                    writer = csv.writer(csv_file, delimiter=",")
                    # todo - parse the text file with the directories
                    row = [actual_ret_time, area, push_vol, short_dir]
                    writer.writerow(row)
    return csv_file_name


def graph_stuff(graph_data):
    """
    :param graph_data: the path to the CSV file that contains all of the data we need to graph
    :return: none
    """
    data = pd.read_csv(graph_data)
    # todo - add units
    fig = go.Figure(data=go.Scatter(x=data['push volume'],  # this will be push volume
                                    y=data['area'],  # this will be the area
                                    mode='markers',
                                    marker_color=data['retention time'],
                                    text=data[
                                        'directory']))  # hover text goes here - will be the directory or the timestamp of the experiment
    fig.update_layout(title='HPLC Graph')
    fig.show()

# GUI stuff below


class graphingGui(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(graphingGui, self).__init__()
        uic.loadUi('graph_gui.ui', self)

        self.okButton = self.findChild(QtWidgets.QPushButton, 'okButton')
        self.okButton.clicked.connect(self.ok_button_pressed)
        self.okButton.clicked.connect(self.close)

        self.cancelButton = self.findChild(QtWidgets.QPushButton, 'cancelButton')
        self.cancelButton.clicked.connect(self.close)

    def ok_button_pressed(self):
        # getting the date
        raw_date = self.dateEdit.date()             # type str
        des_date = str(QDate.toPyDate(raw_date))
        print("desired date:", des_date)

        # getting the time
        raw_time = self.timeEdit.time()             # type str
        str_time = str(QTime.toPyTime(raw_time))
        seg_1 = str_time[0:2]
        seg_2 = str_time[3:5]
        seg_3 = str_time[6:]
        des_time = seg_1 + '-' + seg_2 + '-' + seg_3
        print("desired time:", des_time)

        # getting the ret_time
        ret_time = float(self.retTimeBox.text())    # type float
        print("ret time:", ret_time)

        # getting the flex_time
        flex_time = float(self.flexTimeBox.text())  # type float
        print("flex time:", flex_time)

        # getting the directory
        directory = self.directoryLineEdit.text()   # type str
        print("directory:", directory)

        # getting the signal
        sig = self.signalComboBox.currentText()     # type str
        des_sig = int(sig[0:3])
        print("signal:", sig)
        print("des_sig:", des_sig)

        graph_data = write_to_csv(des_date, des_time, ret_time, flex_time, des_sig, directory)
        graph_stuff(graph_data)


def start():
    m = graphingGui()
    m.show()
    return m


if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = start()
    app.exec_()
