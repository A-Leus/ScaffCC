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
import qalgos

def compile_and_sim(build_path, sim_path, compiler_path, pass_lib_path, pass_flag, algo, do_sim=False):
  # -s to compile to flat QASM then to QX-SIM input file
  # -p also runs our custom pass
  # -k if want to examine files (12a is before our pass and 12 is the result of our pass)
  # HACK encode spaces as '__' so makefile can input
  cc_flags = '-k -s -p "-load__{}__{}"'.format(pass_lib_path, pass_flag)

  for k,v in algos.items():
    # go to build directory (and create if neccessary)
    build_dir = os.path.join(build_path, algo['name'])

    # delete build directory before recompiling to assure clean
    try:
      subprocess.check_output('rm -r {}'.format(build_dir), shell=True)
    except:
      pass

    with util.cd(build_dir):
      # compile
      print('Compiling {}...'.format(k))
      cc = '{} {} {}'.format(compiler_path, cc_flags, algo['path'])
      result = subprocess.check_output(cc, shell=True)
      #print(result)

      # identify .qc file to run
      qc_file = subprocess.check_output('ls *.qc', shell=True)

    # run script through simulator
    if (do_sim):
      # prepare simulator command
      qc_file = qc_file[:-1] # remove newline character
      qc_file = os.path.join(build_dir, qc_file)
      sim_cmd = '{} {}'.format(sim_path, qc_file)

      # run simulation multiple times
      # hard to say how many is reasonable in probabilistic computing
      # just choose a number!
      if ('runs' in algo):
        runs = algo['runs']
      else:
        runs = 1

      #confidence = 0.95
      vals = []

      print('Running {} sim {} times...'.format(k, runs))

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
      algo['majority'] = best_val
      algo['share'] = share

      print('Finshed. majority value={} market share={}\n'.format(best_val, share))

if __name__ == "__main__":
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

  # get info about algorithms to run
  algos = qalgos.get_algos(args.algos)

  for k,v in algos.items():
    # compile and sim a single program
    compile_and_sim(args.build, args.sim, args.compiler, args.pass_lib, args.pass_flag, v, args.do_sim)

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