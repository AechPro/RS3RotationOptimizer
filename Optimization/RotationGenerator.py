"""
File name: RotationGenerator.py
Author: Matthew Allen
Date: 7/12/20

Description:
    This file implements a rotation generating object which will be used to generate rotations that we want to test during
    the optimization process.
"""

import numpy as np

class RotationGenerator(object):
    def __init__(self, cfg):
        self.cfg = cfg
        self.num_abilities = cfg["num_abilities"]
        self.rotation_length = min(self.num_abilities, cfg["rotation_length"])

    def generate_rotation(self):
        """
        Function to generate a rotation from scratch. This will produce one random valid rotation containing no duplicates.
        :return: The generated rotation.
        """

        rng = self.cfg["rng"]
        available_numbers = [i for i in range(self.num_abilities)]
        rotation = []

        while len(rotation) < self.rotation_length:
            idx = rng.randint(0, len(available_numbers))
            rotation.append(available_numbers.pop(idx))

        return rotation

    def perturb_rotation(self, rotation):
        """
        Function to randomly perturb an existing rotation. This is not guaranteed to produce a rotation containing no
        duplicates.
        :param rotation: Rotation to perturb.
        :return: The perturbed rotation, and the vector of Gaussian noise used to perturb it.
        """
        rng = self.cfg["rng"]
        std = self.cfg["stdev"]
        noise = rng.randn(self.rotation_length) * std

        perturbed = np.add(rotation, noise)
        perturbation = self.force_valid_rotation(perturbed)

        return perturbation, noise

    def force_valid_rotation(self, rotation):
        """
        Function to force a rotation to be valid. This is basically just used to round floats into ints and clamp every
        value into the acceptable range.
        :param rotation: Rotation to validate.
        :return: Valid rotation.
        """
        rounded = np.round(rotation)  # 0 decimal places by default
        clamped = np.clip(rounded, a_min=0, a_max=self.num_abilities-1)
        int_rotation = [int(arg) for arg in clamped]

        return int_rotation