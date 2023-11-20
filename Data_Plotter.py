import ROOT
import numpy as np
import time
import argparse
import os

## This script runs over data which is initialy processed using scripts like "Multi_Data_Processer.py".
## If you haven't already processed the data in such a manner, please do so first.
## The input data path should contain 3 folders, "pre_data", "post_data", and "diff_data".

## Script is called like: python3 Data_Plotter.py -p /path/to/processed_files -o /path/to/output_folder/output.root

## This can be used to remove underflow and overflow bins from being plotted, which often cleans up the data.
filter_val = False

## If filter_val == True, then place underflow and overflow bin values to be ignored here
## Anything above the overflow, or below the underflow will be ignored, including the value given:
pre_exposure_underflow_value = 4000
pre_exposure_overflow_value = 6500

post_exposure_underflow_value = 2000
post_exposure_overflow_value = 6500

#You can include entire sectors to be skipped over here (in case of "Type 1 errors"")
bad_sectors = []

def conditional_compare(pre,post,filter):

    return_pre = []
    return_post = []
    return_diff = []

    if len(pre) != len(post):
        print("Error, arrays are different sizes which shouldn't happen.")
        sys.exit()

    

    if (!filter): 
        for i in range(len(pre)):
            return_pre.append(pre[i])
            return_post.append(post[i])
            return_diff.append(post[i]-pre[i])

    #If removing
    if (filter):
        for i in range(len(pre)):
            if pre[i] >= pre_exposure_overflow_value: 
                continue
            elif pre[i] <= pre_exposure_underflow_value: 
                continue
            elif post[i] <= post_exposure_underflow_value:
                continue
            elif post[i] >= post_exposure_overflow_value:
                continue
            else:
                return_pre.append(pre[i])
                return_post.append(post[i])
                return_diff.append(post[i]-pre[i])

    if (len(return_pre) != len(return_post)) or (len(return_post) != len(return_diff)):
        print("Array lengths arent the same")

    return return_pre, return_post, return_diff

#Define parser arguments
parser = argparse.ArgumentParser()
parser.add_argument("-p", "--path", dest="dir_path", help="The directory for processed data")
parser.add_argument("-o", "--output", dest="output", help="The output file")
args = parser.parse_args()

if not args.dir_path:
    print("must provide data directory using '-p' or '--path'")
    sys.exit()

script_dir = os.path.dirname(os.path.abspath(__file__))

data_dir_path = os.path.join(script_dir, args.dir_path)

pre_file_dir = f'{data_dir_path}/pre_data/'
post_file_dir = f'{data_dir_path}/post_data/'
diff_file_dir = f'{data_dir_path}/diff_data/'

# Create a ROOT canvas for the histogram
c = ROOT.TCanvas("c", "c", 800, 600)

pre_hist = ROOT.TH1I("Pre_hist", "Value Counts", 100, -1000, 9000)
post_hist = ROOT.TH1I("Post_hist", "Value Counts", 100, -1000, 9000)
diff_hist = ROOT.TH1I("Diff_hist", "Value Counts", 200, -10000, 10000)

for sect in range(0, 67108864, 65536):

    if sect in bad_sectors:
        continue

    # Check start time
    start_time = time.time()

    # Load the .npz file
    with np.load(f'{pre_file_dir}pre-data-{sect}.npz') as data:
        # Get the 2D array of values
        values = data['arr_0']
        # Reshape the array into a 1D array
        pre_results = values.flatten()

    # Load the .npz file
    with np.load(f'{post_file_dir}post-data-{sect}.npz') as data:
        # Get the 2D array of values
        values = data['arr_0']
        # Reshape the array into a 1D array
        post_results = values.flatten()

    # diff = post_results - pre_results 
    processed_pre, processed_post, processed_diff  = conditional_compare(pre_results, post_results, filter_val)

    for i in processed_pre:
        pre_hist.Fill(i)

    for i in processed_post:
        post_hist.Fill(i)

    for i in processed_diff:
        diff_hist.Fill(i)

    # Print estimated remaining time
    print(f'finished {int(sect/65536)+1} out of {int(67108864/65536)}')
    elapsed_time = time.time() - start_time
    time_remaining = elapsed_time * ( int(67108864/65536) - (int(sect/65536)+1) )
    print(f'Estimated time remaining: {time_remaining//3600:.0f}hrs {(time_remaining%3600)/60:.0f}mins')

# Set the color of the histograms
pre_hist.SetLineColor(ROOT.kBlue)
post_hist.SetLineColor(ROOT.kRed)
diff_hist.SetLineColor(ROOT.kBlack)

# Draw the histogram on the canvas and display it
pre_hist.Draw()
pre_hist.GetXaxis().SetTitle('Voltage (mV)')
c.Draw()

# Draw the second histogram on the same canvas
post_hist.Draw("same")
post_hist.GetXaxis().SetTitle('Voltage (mV)')
c.Draw()

legend = ROOT.TLegend(0.7, 0.6, .99, .7)
legend.AddEntry(pre_hist,'Pre Exposure')
legend.AddEntry(post_hist, 'Post Exposure')
legend.Draw()

# Save the histograms to a ROOT file
out_file = ROOT.TFile(f"{args.output}", "RECREATE")
pre_hist.Write()
post_hist.Write()
c.Write()

c1 = ROOT.TCanvas("c_diff", "c_diff", 800, 600)
diff_hist.Draw()
diff_hist.GetXaxis().SetTitle('#DeltaV (mV)')
c1.Draw()

diff_hist.Write()
c1.Write()

out_file.Close()

