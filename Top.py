"""
File name: Top.py
Author: Matthew Allen
Date: 7/12/20

Description:
    This is the entry point of the program. It will load and configure the environment and optimizer, then start training.
"""

#Seed every RNG library that we might need immediately for reproducibility.
GLOBAL_RNG_SEED = 0
import random
random.seed(GLOBAL_RNG_SEED)
import numpy as np
np.random.seed(GLOBAL_RNG_SEED)

from Optimization import RotationOptimizer
from Environment import test
import os

def main():
    """
    Main function. This loads and starts the optimizer and environment.
    :return:
    """

    rng = np.random.RandomState(123)
    stdev = 6.0
    returns_per_update = 300
    step_size = 0.01

    # Off-by-one because the auto attack JSON file is in this folder.
    num_abilities = len(list(os.listdir("resources/json_data/abilities/ranged")))-1
    rotation_length = num_abilities


    cfg = {
        "rng": rng,
        "stdev": stdev,
        "returns_per_update": returns_per_update,
        "step_size": step_size,
        "rotation_length": rotation_length,
        "num_abilities": num_abilities
    }

    optimizer = RotationOptimizer(cfg)
    optimizer.initialize()
    optimizer.train()

if __name__ == "__main__":
    main()
    test.run_test()