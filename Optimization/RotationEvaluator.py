"""
File name: RotationEvaluator.py
Author: Matthew Allen
Date: 7/12/20

Description:
    This file implements an evaluator which is used to evaluate a rotation in the simulation and report the DPT produced
    by that rotation.
"""

from Environment import CombatSimulator
from Environment.Game import Enemy, Player


class RotationEvaluator(object):
    def __init__(self):
        self.ability_list = None
        self.combat_sim = None

    def initialize(self):
        player = Player(3)
        enemy = Enemy()

        player.load_all_abilities("ranged")

        sim = CombatSimulator(player, enemy)
        self.combat_sim = sim

    def evaluate_rotation(self, rotation):
        """
        Function to evaluate a rotation in the simulation. These hyper-parameters will eventually be handled by the config
        object.
        :param rotation: A list of ability indices representing the rotation to be tested.
        :return: The average damage-per-tick (DPT) that this rotation produced.
        """

        # Duplicates can occur in these randomly generated rotations, so we will first prune all duplicates, keeping only
        # the earliest occurrence of each ability index.
        pruned_rotation = []
        for arg in rotation:
            if arg not in pruned_rotation:
                pruned_rotation.append(arg)

        # Set the player's rotation and run the simulation.
        self.combat_sim.player.rotation = pruned_rotation
        iters = 10
        iter_length = 1000//2
        dpt = 0

        for i in range(iters):
            dpt += self.combat_sim.simulate(iter_length)

        dpt /= (iters*iter_length)
        return dpt