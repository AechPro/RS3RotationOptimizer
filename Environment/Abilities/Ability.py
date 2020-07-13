"""
File name: Ability.py
Author: Matthew Allen
Date: 7/12/20

Description:
    Class describing an arbitrary ability. This class is responsible for handling everything that an ability can do.
    This includes applying buffs to the caster, debuffs to the target, handling adrenaline thresholds, cooldowns, cast times,
    etc. This was initially meant to be a superclass which could be extended by subclass abilities, but I decided to implement
    each ability as a JSON file which gets loaded into this class. This could be written more effectively.
"""

import numpy as np
from Environment.Effects import EffectFactory

class Ability(object):
    def __init__(self, buffs=None, debuffs=None,
                 damage_range=None, name=None,
                 cooldown_ticks=0, adrenaline_cost=0,
                 adrenaline_increase=8, adrenaline_threshold=0,
                 cast_time_ticks=0, max_targets=1,
                 stun_damage_modifier=1, applies_hit=True):
        """
        The constructor takes every argument necessary to fully build an ability equivalent to one described in any of the
        JSON files. This is never actually used in practice, because I wrote a JSON file for each ability. However, in future,
        this may be useful to have.

        :param buffs: An array of Effect objects to be applied to the caster when this ability is cast.
        :param debuffs: An array of Effect objects to be applied to the target when this ability is cast.
        :param damage_range: Either an array containing 2 numbers, or a single number, describing the damage range of
                             this ability.
        :param name: The name of this ability.
        :param cooldown_ticks: The number of ticks this ability must cool down before it can be used again.
        :param adrenaline_cost: The adrenaline that this ability will consume when cast.
        :param adrenaline_increase: The adrenaline that this ability will provide when cast.
        :param adrenaline_threshold: The adrenaline threshold that must be met before this ability can be cast.
        :param cast_time_ticks: The number of ticks this ability must wait before its damage is applied after it is cast.
        :param max_targets: The maximum number of targets this ability can apply to in a single cast (CURRENTLY NOT IMPLEMENTED)
        :param stun_damage_modifier: A scalar damage multiplier to be applied to this ability's damage if the target is
                                     stunned when this ability is cast.
        :param applies_hit: A flag to determine whether this ability should trigger on-hit effects on the entity it is cast on.
        """

        self.name = name
        self.buffs = buffs
        self.debuffs = debuffs
        self.damage_range = damage_range
        self.cooldown_ticks = cooldown_ticks
        self.adrenaline_cost = adrenaline_cost
        self.adrenaline_increase = adrenaline_increase
        self.cast_time_ticks = cast_time_ticks
        self.max_targets = max_targets
        self.adrenaline_threshold = adrenaline_threshold
        self.stun_damage_modifier = stun_damage_modifier
        self.applies_hit = applies_hit

        self.cast_timer = 1
        self.cooldown_timer = self.cooldown_ticks
        self.damage_this_tick = 0
        self.ignores_damage_mod = True
        self.casting = False

        self.average_damage = 0
        self.num_casts = 0

    def apply_damage_to(self, target):
        """
        Function to apply this ability's damage to a target, and update this ability's internal average damage tracker.
        :param target: Target to apply damage to. Must implement the apply_damage(scalar) function.
        :return: None.
        """
        target.apply_damage(self.damage_this_tick)
        self.average_damage += self.damage_this_tick
        self.num_casts += 1

    def compute_damage_this_tick(self):
        """
        Function to compute the damage that this ability will do when it is next applied.
        :return: None
        """

        if type(self.damage_range) not in (float, int):
            # I am assuming that Runescape uses uniform sampling, but I have no idea.
            self.damage_this_tick = np.random.uniform(*self.damage_range)
        else:
            self.damage_this_tick = self.damage_range

    def apply_damage_modifier(self, modifier):
        """
        Function to apply a damage modifier to the damage that this ability will do when it is next cast.
        :param modifier: Scalar to be multiplied by this ability's damage.
        :return: None
        """
        if not self.ignores_damage_mod:
            self.damage_this_tick *= modifier

    def tick_timers(self):
        """
        Function to tick either the cooldown timer or the casting timer. This is to be called once per tick of the simulator.
        :return: None
        """

        if self.cooldown_timer < self.cooldown_ticks:
            self.cooldown_timer += 1
            return

        if self.cast_timer < self.cast_time_ticks:
            self.cast_timer += 1
            return

    def can_cast(self, adrenaline):
        """
        Function to return a flag indicating whether or not this ability can currently be cast. This will be false if this
        ability is currently on cooldown, or if the adrenaline of the caster does not meet this ability's adrenaline
        threshold.
        :param adrenaline: Int between 0 and 100 to compare with this ability's adrenaline threshold.
        :return: None
        """
        adrenaline_threshold_met = adrenaline >= self.adrenaline_threshold
        off_cooldown = self.cooldown_timer >= self.cooldown_ticks

        return off_cooldown and adrenaline_threshold_met and not self.casting

    def start_casting(self):
        """
        Function to tell this ability to start casting. Really, this whole class should be implemented as a state machine.
        I just didn't realize it would need to be that way until I had already finished implementing it this way.
        :return: None
        """
        self.cast_timer = 1
        self.casting = True

    def cast_complete(self):
        """
        Function to return a flag indicating whether or not this ability has completed its cast time.
        :return: None
        """
        return self.cast_timer >= self.cast_time_ticks and self.casting

    def start_cooldown(self):
        """
        Function to begin the cooldown timer for this ability.
        :return: None
        """
        self.cooldown_timer = 0
        self.cast_timer = 1
        self.casting = False

    def reset(self):
        """
        Function to reset an ability and all of its effects. This is used when resetting the simulator after one combat
        session.
        :return: None.
        """
        #print("RESETTING",self.name,"AFTER",self.num_casts,"CASTS")

        # Reset our internal state.
        self.casting = False
        self.cast_timer = 1
        self.cooldown_timer = self.cooldown_ticks

        # Reset all our buffs and debuffs.
        for effect in self.buffs:
            effect.reset()
        for effect in self.debuffs:
            effect.reset()


        # This is some debug code that can be uncommented to report the average damage of this ability since the last
        # time the reset() function was called.
        if self.num_casts != 0:
            self.average_damage /= self.num_casts
            #print("{} average damage: {:.4f}".format(self.name, self.average_damage))

        self.average_damage = 0
        self.num_casts = 0

    def load_from_json(self, json_data):
        """
        Function to load an ability from a JSON file. This is used to set all the internal variables of this ability
        based on some provided JSON data.
        :param json_data: JSON data to read from.
        :return: None
        """

        # Reset our list of buffs and debuffs.
        self.buffs = []
        self.debuffs = []

        # Load all effects.
        for effect_data in json_data["buffs"]:
            effect = EffectFactory.load_from_json(effect_data)
            if effect is not None:
                self.buffs.append(effect)

        for effect_data in json_data["debuffs"]:
            effect = EffectFactory.load_from_json(effect_data)
            if effect is not None:
                self.debuffs.append(effect)

        # Set our internal variables to match the JSON file.
        self.stun_damage_modifier = json_data["stun damage modifier"]
        self.damage_range = json_data["damage range"]
        self.cooldown_ticks = json_data["cooldown ticks"]
        self.adrenaline_cost = json_data["adrenaline cost"]
        self.adrenaline_increase = json_data["adrenaline increase"]
        self.adrenaline_threshold = json_data["adrenaline threshold"]
        self.cast_time_ticks = json_data["cast time ticks"]
        self.max_targets = json_data["max targets"]
        self.name = json_data["name"]
        self.ignores_damage_mod = json_data["ignores damage mod"]
        self.applies_hit = json_data["applies hit"]

        # Set ourselves up to be ready to case.
        self.cast_timer = 0
        self.cooldown_timer = self.cooldown_ticks

    def get_stun_damage_modifier(self):
        return self.stun_damage_modifier

    def counts_as_hit(self):
        return self.applies_hit

    def get_buffs(self):
        return self.buffs

    def get_debuffs(self):
        return self.debuffs

    def __str__(self):
        return self.name