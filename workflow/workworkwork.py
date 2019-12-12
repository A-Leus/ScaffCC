'''
  Workflow to evaluate passes on scaffold programs and simulate the results

  1) Compile .scaffold file to LLVM
  2) Run desired pass on LLVM
  3) Optimize LLVM with the rest of the usual workflow and compile to OpenQASM
  4) Simulate OpenQASM on qx-sim
  5) Extract statistics from the run

'''

import os, subprocess, time, argparse, re

from util import cd

# TODO want absolute paths
# set path ScaffCC on system
scaff_dir = '/home/pbb59/cs6120/ScaffCC'

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
# -v if want to examine files (12a is before our pass and 12 is the result of our pass)
# HACK encode spaces as '__' so makefile can input
cc_flags = '-s -p "-load__{}__{}"'.format(args.pass_lib, args.pass_flag)

algos = {
  'cat' : { 'path': os.path.join(args.algos, 'Cat_State/cat_state.n04.scaffold') }
}

for k,v in algos.items():
  # go to build directory (and create if neccessary)
  build_dir = os.path.join(args.build, k)
  with cd(build_dir):
    # compile
    cc = '{} {} {}'.format(args.compiler, cc_flags, v['path'])
    result = subprocess.check_output(cc, shell=True)
    print(result)

    # identify .qc file to run
    qc_file = subprocess.check_output('ls *.qc', shell=True)

  # run script through simulator
  if (args.do_sim):
    qc_file = qc_file[:-1] # remove newline character
    qc_file = os.path.join(build_dir, qc_file)
    sim = '{} {}'.format(args.sim, qc_file)
    sim_result = subprocess.check_output(sim, shell=True)
    print(sim_result)


  


