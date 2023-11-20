import numpy as np
import time
import argparse
import os
import csv

## This script runs over data which is initialy processed using scripts like "Multi_Data_Processer.py".
## If you haven't already processed the data in such a manner, please do so first.
## The input data path should contain 3 folders, "pre_data", "post_data", and "diff_data".

## Script is called like: python3 Bad_Sector_Identifier.py -p /path/to/processed_files -o /path/to/output_folder/output.csv

## Set to true if you want the output printed to the terminal
verbose_output = True

## Define the "bit flip" voltage using this parameter. The script will tell you how many transistors in a sector shifted by this amount.
voltage_shift_amount = -1000 #units of mV

## Uncomment to take absolute value of voltage shift.
# voltage_name = abs(voltage_shift_amount)

#Define parser arguments
parser = argparse.ArgumentParser()
parser.add_argument("-p", "--path", dest="dir_path", help="The directory for processed data")
parser.add_argument("-o", "--output", dest="output", help="The output file")
args = parser.parse_args()

if not args.dir_path:
    print("Must provide data directory using '-p' or '--path'")
    exit()

if not (args.output.lower().endswith(".csv")):
    print("Output file must be of type '.csv'")
    exit()

script_dir = os.path.dirname(os.path.abspath(__file__))

data_dir_path = os.path.join(script_dir, args.dir_path)

pre_file_dir = f'{data_dir_path}/pre_data/'
post_file_dir = f'{data_dir_path}/post_data/'
diff_file_dir = f'{data_dir_path}/diff_data/'

with open(args.output, 'w', newline='') as csvfile:

    writer = csv.writer(csvfile)

    # Write the header row
    writer.writerow(['sector', 'bit flips'])

    # Loop through each file
    for sect in range(0, 67108864, 65536):

        total_shifts = 0

        # Load the .npz file
        with np.load(f'{diff_file_dir}diff-data-{sect}.npz') as data:
            # Get the 2D array of values
            values = data['arr_0']
            # Reshape the array into a 1D array
            values = values.flatten()
            # Fill the ROOT histogram with the value counts
            for value in values:
                if value < voltage_shift_amount:
                    total_shifts = total_shifts + 1

        writer.writerow([sect, total_shifts])

        if (verbose_output):
            print(f'{sect}, {total_shifts}\n')


