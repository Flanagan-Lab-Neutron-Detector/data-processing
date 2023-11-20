import numpy as np
import argparse
import os
import sys
import multiprocessing
from tqdm import tqdm

## Script is called like: python3 Multi_Data_Processer_CSV.py -pre /path/to/Pre_Exposure/CSV_files -post /path/to/Post_Exposure/CSV_files -dest /path/to/output_folder

## Pre-exposure voltage info
pre_read_start_voltage = 5000
pre_read_stop_voltage = 7000 # needs to be 100 more than final value in the CSV file
pre_read_step_voltage = 100

## Post-exposure voltage info
post_read_start_voltage = 4000
post_read_stop_voltage = 7000 # needs to be 100 more than final value in the CSV file
post_read_step_voltage = 100

def process_data(input_args):

    sect = input_args[0]
    input_pre_path = input_args[1]
    input_post_path = input_args[2]
    pre_path = input_args[3]
    post_path = input_args[4]
    diff_path = input_args[5]

    ########
    # Initialize an empty numpy array to store the results
    pre_results = np.zeros((65536, 16), dtype=int)

    # Loop through each file
    for i in range(pre_read_start_voltage, pre_read_stop_voltage, pre_read_step_voltage):
        # Read in the file
        filename = f'{input_pre_path}/data-{i}-{sect}.csv'
        with open(filename, 'r') as f:
            lines = f.readlines()

        # Loop through each line in the file
        for j, line in enumerate(lines):
            # Convert the string to a list of integers
            row = [int(x) for x in line.strip()]

            # Loop through each value in the row
            for k, value in enumerate(row):
                # If the value is 1 and we haven't recorded it yet, record it
                if value == 1 and pre_results[j, k] == 0:
                    pre_results[j, k] = i
                    
    ###########

    post_results = np.zeros((65536, 16), dtype=int)

    # Loop through each file
    for i in range(post_read_start_voltage, post_read_stop_voltage, post_read_step_voltage):
        # Read in the file
        filename = f'{input_post_path}/data-{i}-{sect}.csv'
        with open(filename, 'r') as f:
            lines = f.readlines()

        # Loop through each line in the file
        for j, line in enumerate(lines):
            # Convert the string to a list of integers
            row = [int(x) for x in line.strip()]

            # Loop through each value in the row
            for k, value in enumerate(row):
                # If the value is 1 and we haven't recorded it yet, record it
                if value == 1 and post_results[j, k] == 0:
                    post_results[j, k] = i

    diff = post_results - pre_results
    
    pre_output_file = f'{pre_path}/pre-data-{sect}'
    post_output_file = f'{post_path}/post-data-{sect}'
    diff_output_file = f'{diff_path}/diff-data-{sect}'

    np.savez_compressed(pre_output_file, pre_results)
    np.savez_compressed(post_output_file, post_results)
    np.savez_compressed(diff_output_file, diff)

if __name__ == '__main__':

    #This defines the parser arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-pre", "--pre", dest="pre_dir_path", help="The directory for pre exposure files")
    parser.add_argument("-post", "--post", dest="post_dir_path", help="The directory for post exposure files")
    parser.add_argument("-dest", "--destination", dest="destination", help="The directory where the results will be saved")
    args = parser.parse_args()

    script_dir = os.path.dirname(os.path.abspath(__file__))

    if not args.pre_dir_path:
        print("must provide pre exposure directory using '-pre'")
        sys.exit()
    elif not os.path.exists(args.pre_dir_path):
        print("Can't find pre exposure directory path")
        sys.exit()

    if not args.post_dir_path:
        print("must provide post exposure directory using '-post'")
        sys.exit()
    elif not os.path.exists(args.post_dir_path):
        print("Can't find post exposure directory path")
        sys.exit()

    if args.destination:
        destination_dir = os.path.abspath(args.destination)
        if not os.path.exists(destination_dir):
            print("Making ouput directory")
            os.makedirs(destination_dir)
            pre_dir_path = os.path.join(args.destination, 'pre_data')
            os.makedirs(pre_dir_path)
            post_dir_path = os.path.join(args.destination, 'post_data')
            os.makedirs(post_dir_path)
            diff_dir_path = os.path.join(args.destination, 'diff_data')
            os.makedirs(diff_dir_path)
        else:
            pre_dir_path = os.path.join(args.destination, 'pre_data')
            if not os.path.exists(pre_dir_path):
                os.mkdir(pre_dir_path)
            post_dir_path = os.path.join(args.destination, 'post_data')
            if not os.path.exists(post_dir_path):
                os.mkdir(post_dir_path)
            diff_dir_path = os.path.join(args.destination, 'diff_data')
            if not os.path.exists(diff_dir_path):
                os.mkdir(diff_dir_path)
    else:
        pre_dir_path= os.path.join(script_dir, 'pre_data')
        if not os.path.exists(pre_dir_path):
            os.mkdir(pre_dir_path)
        post_dir_path= os.path.join(script_dir, 'post_data')
        if not os.path.exists(post_dir_path):
            os.mkdir(post_dir_path)
        diff_dir_path= os.path.join(script_dir, 'diff_data')
        if not os.path.exists(diff_dir_path):
            os.mkdir(diff_dir_path)


    sectors = range(0, 67108864, 65536)

    bundled_inputs = []

    for i in sectors:
        bundled_inputs.append([i, args.pre_dir_path, args.post_dir_path, pre_dir_path, post_dir_path, diff_dir_path])

    pool = multiprocessing.Pool(processes=multiprocessing.cpu_count())

    results = []
    with tqdm(total=len(bundled_inputs)) as pbar:
        for result in pool.imap(process_data, bundled_inputs):
            results.append(result)
            pbar.update()


    pool.close()