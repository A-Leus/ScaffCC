# store information about how to run algorithms

import os

def get_algos(algo_path):
    algos = {
    'cat'     : { 
        'path': os.path.join(algo_path, 'Cat_State/cat_state.n04.scaffold'),
        'runs': 100,
    },
    # expect multiple values I think, it's eigenvalues? Take ones with a certain partial majority 
    'vqe'     : { 
        'path': os.path.join(algo_path, 'VQE/UCCSD_ansatz_4.scaffold'),
        'runs': 100,
    },
    'ground'  : { 
        'path': os.path.join(algo_path, 'Ground_State_Estimation/ground_state_estimation.h2.scaffold'), 
        'runs': 10,
    },
    'ising'   : { 
        'path': os.path.join(algo_path, 'Ising_Model/ising_model.n10.scaffold'),
        'runs': 100,
    },
    # doesn't really make sense to measure because not meant to produce a single value
    # 'qft'     : { 'path': os.path.join(args.algos, 'QFT/qft.n05.scaffold'), 'runs': 1 },
    'grover'  : { 
        'path': os.path.join(algo_path, 'Square_Root/square_root.n4.scaffold'),
        'runs': 100,
    },

    }

    return algos
