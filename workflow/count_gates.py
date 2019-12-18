# run workflow script to count the number of gates

import os, subprocess, time, argparse, re

import qalgos

from workworkwork import compile_and_sim

if __name__ == "__main__":
  # get scaffCC root directory from an uncommitted file.
  # user needs to set this themselves
  from env import scaff_dir

  # make sure this path exists on the system
  assert(os.path.exists(scaff_dir))

  # cmd line arguments
  parser = argparse.ArgumentParser(description='Count the number of gates in the compiled program')
  parser.add_argument('--pass-lib', 
                      default=os.path.join(scaff_dir, 'build/Release+Asserts/lib/Scaffold.so'), 
                      help='Path to pass static library')
  parser.add_argument('--pass-flag', 
                      default='-GateCount', 
                      help='Flag to run the pass')
  parser.add_argument('--algos', 
                      default=os.path.join(scaff_dir, 'Algorithms'), 
                      help='Path to algorithms')
  parser.add_argument('--compiler', 
                      default=os.path.join(scaff_dir, 'scaffold.sh'), 
                      help='Path to scaffold compiler')
  parser.add_argument('--build', 
                      default=os.path.join(scaff_dir, 'algo-build'), 
                      help='Path to build files in')

  args = parser.parse_args()

  # get info about algorithms to run
  algos = qalgos.get_algos(args.algos)

  for k,v in algos.items():
    # compile and sim a single program
    compile_result = compile_and_sim(args.build, '', args.compiler, args.pass_lib, args.pass_flag, v, False)

    # do regex to find total gate count
    count_regex = re.compile('total_gates = (\d+)')
    match = count_regex.search(compile_result)
    assert(match)
    gates = match.group(1)
    print ('Gate: ' + gates)

  # regex