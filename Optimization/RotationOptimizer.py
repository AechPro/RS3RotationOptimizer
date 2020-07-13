"""
File name: RotationOptimizer.py
Author: Matthew Allen
Date: 7/12/20

Description:
    This file implements the optimizer to be used when optimizing a rotation. There are two optimization algorithms
    currently implemented. One of them approximates the gradient of DPT as a function of the rotation parameters, then
    follows that naively using SGD. The other optimizer is a simple genetic algorithm which randomly perturbs the
    highest-scoring rotation at every update, gradually decreasing the size of the perturbations as it improves.
"""

from Optimization import RotationGenerator, RotationEvaluator

import numpy as np
import time


class RotationOptimizer(object):
    def __init__(self, cfg):
        self.cfg = cfg
        self.evaluator = None
        self.generator = None

        self.best_rotation = None
        self.best_dps = -np.inf

        self.current_rotation = None

    def initialize(self):
        self.evaluator = RotationEvaluator()
        self.generator = RotationGenerator(self.cfg)
        self.evaluator.initialize()

        self.current_rotation = self.generator.generate_rotation()

    def train(self):
        """
        The main training loop. This will take one training step and report data about what happened during that step.
        :return:
        """

        # Basically infinity.
        num_epochs = 100000000

        for epoch in range(num_epochs):

            t1 = time.time()
            rewards = self.epoch()
            epoch_time = time.time()-t1

            stats = self.compute_arr_stats(rewards)
            print("\nEpoch: {}"
                  "\nEpoch Time: {}"
                  "\nRewards Mean: {}"
                  "\nRewards Std : {}"
                  "\nRewards Min: {}"
                  "\nRewards Max: {}"
                  "\nBest DPS: {}"
                  "\nBest Rotation: {}"
                  "\nNoise Stdev: {}"
                  "\n".
                  format(epoch,
                         epoch_time,
                         stats[0],
                         stats[1],
                         stats[2],
                         stats[3],
                         self.best_dps,
                         self.best_rotation,
                         self.cfg["stdev"]))

    def epoch(self):
        """
        Function to perform one epoch of training. This is currently set up to use the genetic algorithm outlined above,
        but by commenting out some of the existing code and uncommenting other code this can be turned into the gradient
        approximator outlined above.

        :return: A list containing the DPT of each random perturbation that was tried this epoch.
        """


        generator = self.generator
        evaluator = self.evaluator
        num = self.cfg["returns_per_update"]
        current_rotation = self.current_rotation
        rewards = []
        epsilons = []

        best_this_epoch = -np.inf
        best_rot_this_epoch = None

        # Perturb the current rotation, evaluate it, keep track of the best one so far, and keep going.
        for i in range(num):
            rotation, noise = generator.perturb_rotation(current_rotation)
            reward = evaluator.evaluate_rotation(rotation)
            if reward >= best_this_epoch:
                best_this_epoch = reward
                best_rot_this_epoch = rotation
            rewards.append(reward)
            #epsilons.append(noise)

        # If the best rotation this epoch is better than the best rotation we've ever seen, record that and anneal the
        # size of our noise.
        if best_this_epoch > self.best_dps:
            self.cfg["stdev"] *= 0.85
            self.best_dps = best_this_epoch
            self.current_rotation = best_rot_this_epoch

            # This translates the rotation vector into a list of strings containing the ability names of the
            # current best rotation.
            abilities = self.evaluator.combat_sim.player.abilities
            self.best_rotation = [abilities[arg].name for arg in self.current_rotation]

        # Uncomment this stuff (and epsilons.append(noise) above) to swap to the gradient approximation method.
        # You'll also need to comment out line 107 above.
        # self.current_rotation = self.compute_update(rewards, epsilons)
        #
        # current_reward = evaluator.evaluate_rotation(self.current_rotation)
        # if current_reward > self.best_dps:
        #     self.best_dps = current_reward
        #     abilities = self.evaluator.combat_sim.player.abilities
        #     self.best_rotation = [abilities[arg].name for arg in self.current_rotation]

        return rewards

    def compute_update(self, rewards, epsilons):
        """
        Function to approximate a gradient and follow it.
        :param rewards: DPT of each rotation tried this epoch.
        :param epsilons: Noise vectors used to generate each rotation from this epoch.
        :return: The updated rotation.
        """
        rews = self.standardize(rewards)

        gradient = np.dot(rews, epsilons) / len(rews)

        # Gradient ascent.
        new_rotation = np.add(self.current_rotation, self.cfg["step_size"]*gradient)
        validated_rotation = self.generator.force_valid_rotation(new_rotation)

        return validated_rotation

    def standardize(self, arr):
        if np.std(arr) == 0:
            return arr

        return np.divide(np.subtract(arr, np.mean(arr)), np.std(arr))

    def compute_arr_stats(self, arr):
        return np.mean(arr), np.std(arr), np.min(arr), np.max(arr)