"""
File name: test.py
Author: Matthew Allen
Date: 7/12/20

Description:
    This is basically my playground. I use this file to test all the new Environment code that I write. Please excuse the mess.
"""

from Environment import CombatSimulator
from Environment.Game import Player, Enemy
from Environment.Abilities import Ability
import json
import numpy as np
import os
import time

def load_ability(base_path, effect_name):
    full_path = os.path.join(base_path, effect_name)
    if os.path.exists(full_path):
        ability_json = json.load(open(full_path,'r'))
        return ability_json

    print("UNABLE TO LOAD ABILITY {} FROM {}".format(effect_name, base_path))
    return None

def load_abilities():
    base_path = os.path.join("resources","json_data","abilities","ranged")

    ability_names = ["CorruptionShot.json",  "NeedleStrike.json", "BindingShot.json", "SnapShot.json", "RapidFire.json",
                     "DeathsSwiftness.json", "PiercingShot.json"]

    #ability_names = ["CorruptionShot.json",  "BindingShot.json", "SnapShot.json", "PiercingShot.json", "RapidFire.json"]

    #ability_names = ["DeathsSwiftness.json"]

    abilities = []
    for name in ability_names:
        ability = load_ability(base_path, name)
        abilities.append(ability)
    return abilities

def run_test():
    target = Enemy()
    player = Player(3)
    player.load_all_abilities("ranged")
    #player.load_abilities_from_json(load_abilities())

    simulator = CombatSimulator(player, target)
    # dmg = 0
    # num_iters = 100
    # num_ticks = 1000
    # for i in range(num_iters):
    #     dmg += simulator.simulate(num_ticks)
    # print(dmg  / (num_ticks*num_iters))
    iters = 100
    iter_length = 1000//2

    attempts = []
    for i in range(iters):
        dmg = simulator.simulate(iter_length)
        attempts.append(dmg / iter_length)

    print(np.mean(attempts), np.std(attempts), np.min(attempts), np.max(attempts))


    # for i in range(250):
    #     print("\n{stars}TICK {tick}{stars}".format(stars="*"*20, tick=i))
    #     simulator.tick()
