import os, subprocess, time, argparse, re

# https://stackoverflow.com/questions/431684/how-do-i-change-directory-cd-in-python
class cd:
    """Context manager for changing the current working directory"""
    def __init__(self, newPath):
        self.newPath = os.path.expanduser(newPath)

    def __enter__(self):
        self.savedPath = os.getcwd()

        try:
            os.chdir(self.newPath)
        except OSError:
            # make the directory and then chdir
            os.makedirs(self.newPath)
            os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)


def qc_sim(sim_cmd):
    sim_result = subprocess.check_output(sim_cmd, shell=True)
    print(sim_result)

    # parse sim result to determine output
    # require some x% confidence after y runs

    # get the measurement info string from sim output
    meas_regex = re.compile("measurement register\s*:\s*([0-9\|\s]+)")
    meas_match = meas_regex.search(sim_result)
    assert(meas_match)

    # extract the bits from the string
    meas_regex = re.compile("\d")
    meas_match = meas_match.group(1)

    # accrue bits
    bits = []
    for bit in meas_regex.finditer(meas_match):
      bit_val = int(bit.group(0))
      bits.append(bit_val)

    return bits

# convert bit array to an integer value
def bits_to_val(bit_array):
    val = 0
    for i in range(len(bit_array)):
        val += bit_array[i] << i
    return val

def get_majority(vals):
    # create sparse histogram
    bins = {}
    for i in range(len(vals)):
        val = vals[i]
        if val in bins:
            bins[val] += 1
        else:
            bins[val] = 1

    # then figure out majority
    best_val = 0
    best_count = 0
    for k,v in bins.items():
        if (v > best_count):
            best_val = k
            best_count = v

    return (best_val, float(best_count) / float(len(vals)))


# https://stackoverflow.com/questions/15033511/compute-a-confidence-interval-from-sample-data
# given data=[], and confidence value
# ret (mean, stdev, confidence interval as two values)
def mean_confidence_interval(data, confidence=0.95):
    import numpy as np
    import scipy.stats

    a = 1.0 * np.array(data)
    n = len(a)
    m, se = np.mean(a), scipy.stats.sem(a)
    h = se * scipy.stats.t.ppf((1 + confidence) / 2., n-1)
    return m, se, m-h, m+h