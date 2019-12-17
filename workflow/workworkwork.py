'''
  Workflow to evaluate passes on scaffold programs and simulate the results

  1) Compile .scaffold file to LLVM
  2) Run desired pass on LLVM
  3) Optimize LLVM with the rest of the usual workflow and compile to OpenQASM
  4) Simulate OpenQASM on qx-sim
  5) Extract statistics from the run

'''

import os, subprocess, time, argparse, re

import util

# get scaffCC root directory from an uncommitted file.
# user needs to set this themselves
from env import scaff_dir

# make sure this path exists on the system
assert(os.path.exists(scaff_dir))

# cmd line arguments
parser = argparse.ArgumentParser(description='Compile quantum programs, optimize, and then simulate')
parser.add_argument('--sim', 
                    default=os.path.join(scaff_dir, 'qx-sim/qx_simulator_linux_x86_64/qx_simulator_1.0.beta_linux_x86_64'), 
                    help='Path to quantum simulator')
parser.add_argument('--pass-lib', 
                    default=os.path.join(scaff_dir, 'vector-passes/build/src/libTestPass.so'), 
                    help='Path to pass static library')
parser.add_argument('--pass-flag', 
                    default='-test', 
                    help='Flag to run the test')
parser.add_argument('--algos', 
                    default=os.path.join(scaff_dir, 'Algorithms'), 
                    help='Path to algorithms')
parser.add_argument('--compiler', 
                    default=os.path.join(scaff_dir, 'scaffold.sh'), 
                    help='Path to scaffold compiler')
parser.add_argument('--build', 
                    default=os.path.join(scaff_dir, 'algo-build'), 
                    help='Path to build files in')
parser.add_argument('--do-sim',
                    default=False,
                    action='store_true',
                    help='Whether to run sim or not')

args = parser.parse_args()

# -s to compile to flat QASM then to QX-SIM input file
# -p also runs our custom pass
# -k if want to examine files (12a is before our pass and 12 is the result of our pass)
# HACK encode spaces as '__' so makefile can input
cc_flags = '-k -s -p "-load__{}__{}"'.format(args.pass_lib, args.pass_flag)

algos = {
  'cat'     : { 
    'path': os.path.join(args.algos, 'Cat_State/cat_state.n04.scaffold'),
    'runs': 100,
  },
  # expect multiple values I think, it's eigenvalues? Take ones with a certain partial majority 
  'vqe'     : { 
    'path': os.path.join(args.algos, 'VQE/UCCSD_ansatz_4.scaffold'),
    'runs': 100,
  },
  'ground'  : { 
    'path': os.path.join(args.algos, 'Ground_State_Estimation/ground_state_estimation.h2.scaffold'), 
    'runs': 10,
  },
  'ising'   : { 
    'path': os.path.join(args.algos, 'Ising_Model/ising_model.n10.scaffold'),
    'runs': 100,
  },
  # doesn't really make sense to measure because not meant to produce a single value
  # 'qft'     : { 'path': os.path.join(args.algos, 'QFT/qft.n05.scaffold'), 'runs': 1 },
  'grover'  : { 
    'path': os.path.join(args.algos, 'Square_Root/square_root.n4.scaffold'),
    'runs': 100,
  },

}

# delete build directory before recompiling to assure clean
try:
  subprocess.check_output('rm -r {}'.format(args.build), shell=True)
except:
  pass

for k,v in algos.items():
  # go to build directory (and create if neccessary)
  build_dir = os.path.join(args.build, k)
  with util.cd(build_dir):
    # compile
    cc = '{} {} {}'.format(args.compiler, cc_flags, v['path'])
    result = subprocess.check_output(cc, shell=True)
    print(result)

    # identify .qc file to run
    qc_file = subprocess.check_output('ls *.qc', shell=True)

  # run script through simulator
  if (args.do_sim):
    # prepare simulator command
    qc_file = qc_file[:-1] # remove newline character
    qc_file = os.path.join(build_dir, qc_file)
    sim_cmd = '{} {}'.format(args.sim, qc_file)

    # run simulation multiple times
    # hard to say how many is reasonable in probabilistic computing
    # just choose a number!
    if ('runs' in v):
      runs = v['runs']
    else:
      runs = 1

    confidence = 0.95
    vals = []
    for run in range(runs):
      meas_val = util.qc_sim(sim_cmd)
      #print(meas_val)
      val = util.bits_to_val(meas_val)
      vals.append(val)
      #(mean, stdev, lbnd, ubnd) = util.mean_confidence_interval(vals, confidence)
      #(best_val, share) = util.get_majority(vals)
      #conf_len = ubnd - lbnd
      #print('run={}: val={} - maj={} w/ {} - m={} std={} clen={}'.format(run, val, best_val, share, mean, stdev, conf_len))

    # store results
    (best_val, share) = util.get_majority(vals)
    v['majority'] = best_val
    v['share'] = share

# output results to file
if (args.do_sim):
  with open('results.csv', 'w+') as fd:
    # top row algorithm names
    fd.write('field,')
    for k,v in algos.items():
      fd.write(k + ',')
    fd.write('\n')
    # majority value market share
    fd.write('share,')
    for k,v in algos.items():
      fd.write(str(v['share']) + ',')
    fd.write('\n')
    




  


