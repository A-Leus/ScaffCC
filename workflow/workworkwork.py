'''
  Workflow to evaluate passes on scaffold programs and simulate the results

  1) Compile .scaffold file to LLVM
  2) Run desired pass on LLVM
  3) Optimize LLVM with the rest of the usual workflow and compile to OpenQASM
  4) Simulate OpenQASM on qx-sim
  5) Extract statistics from the run

'''

import os, subprocess, time, argparse, re

# TODO want absolute paths
# set path ScaffCC on system
scaff_dir = '/home/pbb59/cs6120/ScaffCC'

# cmd line arguments
parser = argparse.ArgumentParser(description='Compile quantum programs, optimize, and then simulate')
parser.add_argument('--sim', 
                    default=scaff_dir + '/qx-sim/qx_simulator_linux_x86_64/qx_simulator_1.0.beta_linux_x86_64', 
                    help='Path to quantum simulator')
parser.add_argument('--pass-lib', 
                    default=scaff_dir + '/vector-passes/build/src/libTestPass.so', 
                    help='Path to pass static library')
parser.add_argument('--pass-flag', 
                    default='-test', 
                    help='Flag to run the test')
parser.add_argument('--algos', 
                    default=scaff_dir + '/Algorithms', 
                    help='Path to algorithms')
parser.add_argument('--compiler', 
                    default=scaff_dir + '/scaffold.sh', 
                    help='Path to scaffold compiler')

args = parser.parse_args()

# -s to compile to flat QASM then to QX-SIM input file
# -p also runs our custom pass
# -v if want to examine files (12a is before our pass and 12 is the result of our pass)
cc_flags = '-s -p'


