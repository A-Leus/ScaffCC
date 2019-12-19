# store information about how to run algorithms

import os

def get_algos(algo_path):
    algos = {
    'cat'     : { 
        'name': 'cat',
        'path': os.path.join(algo_path, 'Cat_State/cat_state.n04.scaffold'),
        'runs': 100,
        'vlen': 5,
    },
    # expect multiple values I think, it's eigenvalues? Take ones with a certain partial majority 
    # 'vqe'     : { 
    #     'name': 'vqe',
    #     'path': os.path.join(algo_path, 'VQE/UCCSD_ansatz_4.scaffold'),
    #     'runs': 100,
    #     'vlen': 5,
    # },
    # 'ground'  : { 
    #     'name': 'ground',
    #     'path': os.path.join(algo_path, 'Ground_State_Estimation/ground_state_estimation.h2.scaffold'), 
    #     'runs': 10,
    #     'vlen': 3,
    # },
    # 'ising'   : { 
    #     'name': 'ising',
    #     'path': os.path.join(algo_path, 'Ising_Model/ising_model.n10.scaffold'),
    #     'runs': 100,
    #     'vlen': 2,
    # },
    # # doesn't really make sense to measure because not meant to produce a single value
    # # 'qft'     : { 'path': os.path.join(args.algos, 'QFT/qft.n05.scaffold'), 'runs': 1 },
    # 'grover'  : { 
    #     'name': 'grover',
    #     'path': os.path.join(algo_path, 'Square_Root/square_root.n4.scaffold'),
    #     'runs': 100,
    #     'vlen': 1,
    # },

    }

    return algos
