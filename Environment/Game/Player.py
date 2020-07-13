"""
File name: Player.py
Author: Matthew Allen
Date: 7/12/20

Description:
    This file implements a Player object. This is extremely similar to Enemy.py, and the two should be merged in the
    future. I will leave the shared functions between the two undocumented, refer to the equivalent function in
    Enemy.py if you need to.

"""

from Environment.Abilities import Ability
import json
import os

class Player(object):
    def __init__(self, attack_delay):
        """
        Basic constructor.
        :param attack_delay: The delay (in ticks) between each attack that a player can make. This is effectively the
                             attack speed of a weapon.
        """

        self.adrenaline = 0
        self.abilities = []
        self.current_ability_idx = 0
        self.damage_modifier = 1
        self.stunned = False
        self.debuffs = []
        self.buffs = []
        self.attack_delay = attack_delay
        self.rotation = []

        # Note that we store the auto attack as its own variable. This is because it has a cooldown of 0, and is the default
        # action to be taken at every tick if nothing else is available. When re-arranging rotations, we do not want the
        # position of the auto attack to change.
        self.auto_attack = None

    def tick(self):
        self.stunned = False
        self.damage_modifier = 1
        for effect in self.debuffs:
            effect.apply_on_tick(self)
            self._handle_effect_timeout(effect, self.debuffs)

        for effect in self.buffs:
            effect.apply_on_tick(self)
            self._handle_effect_timeout(effect, self.buffs)

        for ability in self.abilities:
            ability.tick_timers()

        # Handle auto attacks separately from all other abilities.
        self.auto_attack.tick_timers()

        #print("PLAYER\nDAMAGE MOD: {}\n".format(self.damage_modifier))

    def get_next_ability(self):
        """
        Function to cycle through this player's rotation bar until an ability is found to be available. If no abilities
        are available to be cast immediately, the auto attack is returned.
        :return: The next ability to cast.
        """
        ability = self.auto_attack

        # Note here that we're not actually indexing our abilities directly, we have a list of integers called self.rotation
        # and we use the entries in that list to pull out an ability. This allows us to easily modify the rotation being
        # used by this player by simply changing the values in self.rotation instead of re-ordering our ability list.
        for idx in self.rotation:
            ab = self.abilities[idx]
            if ab.can_cast(self.adrenaline):
                ability = ab
                break

        #print('CASTING',ability.name)
        return ability

    def apply_ability(self, ability, friendly=False):
        if friendly:
            self_effects = self.buffs
            ability_effects = ability.get_buffs()
            apply_function = self.apply_buff
            self.apply_cast_costs(ability)

        else:
            self_effects = self.debuffs
            ability_effects = ability.get_debuffs()
            apply_function = self.apply_debuff

        for effect in ability_effects:
            apply_function(effect)

        if not friendly:
            if ability.counts_as_hit():
                for effect in self_effects:
                    effect.apply_on_hit(self)
                    self._handle_effect_timeout(effect, self_effects)

            ability.apply_damage_to(self)

    def reset(self):
        self.adrenaline = 0
        self.current_ability_idx = 0
        self.damage_modifier = 1
        self.stunned = False
        self.debuffs = []
        self.buffs = []

        for ability in self.abilities:
            ability.reset()

        self.auto_attack.reset()

    def _handle_effect_timeout(self, effect, effect_list):
        if effect.is_done():
            effect_list.remove(effect)
            effect.reset()

    def load_all_abilities(self, ability_folder="ranged"):
        """
        Helper function to load all this player's abilities from a bunch of json files stored in the base_path folder.
        This expects the resources/json_data/abilties/ranged folder to exist and contain a bunch of JSON files describing
        abilities.
        :param ability_folder: The name of the folder inside the base path to load abilities from. Eventually, there will
                               be more than just the ranged abilities folder inside the base path.
        :return: None
        """

        base_path = os.path.join("resources", "json_data", "abilities", ability_folder)
        aa = None
        abilities = []

        # Load all JSON files located in the requested path.
        for ability_name in os.listdir(base_path):
            if '.json' not in ability_name:
                continue

            full_path = os.path.join(base_path, ability_name)
            json_data = json.load(open(full_path, 'r'))

            # Save the auto-attack for later. We will load this separately.
            if "AutoAttack" in ability_name:
                aa = json_data
                continue

            abilities.append(json_data)

        #Load the auto-attack and assign it to our local variable.
        ability = Ability()
        ability.load_from_json(aa)
        ability.cast_time_ticks += self.attack_delay
        self.auto_attack = ability

        #Load all the other abilities into objects.
        self.load_abilities_from_json(abilities)

    def load_abilities_from_json(self, ability_jsons):
        """
        Function to load this player's list of abilities from a list containing one or more JSON data objects. These are
        dicts in Python.
        :param ability_jsons: List containing one or more JSON dictionaries.
        :return: None
        """

        self.abilities = []

        #Load a new ability from each JSON dictionary.
        for ability_json in ability_jsons:
            ability = Ability()
            ability.load_from_json(ability_json)
            ability.cast_time_ticks += self.attack_delay
            self.abilities.append(ability)
            #print("Loaded ability {}".format(ability))

        # This is here to pre-organize a rotation so I can test it on its own after the optimizer has found something.
        # During optimization, the order of the player's rotation at this stage doesn't matter, so the rotation can be
        # put in any order we like.
        self.preload_rotation()
        #self.rotation = [i for i in range(len(self.abilities))]

    def preload_rotation(self):
        rotation = ['Needle Strike', 'Piercing Shot', 'Snap Shot', 'Fragmentation Shot', 'Binding Shot', 'Bombardment', 'Tight Bindings', "Death's Swiftness", 'Corruption Shot']
        indexed_rotation = []
        print("LOADED ROTATION",end=' [')
        for name in rotation:
            for i in range(len(self.abilities)):
                if self.abilities[i].name == name:
                    indexed_rotation.append(i)
                    print(self.abilities[i].name, end=' ')
        print("]")
        self.rotation = indexed_rotation

    def set_damage_modifier(self, value):
        self.damage_modifier = value

    def set_stunned(self, state):
        self.stunned = state

    def is_stunned(self):
        return self.stunned

    def get_current_damage_modifier(self):
        return self.damage_modifier

    def get_damage_modifier(self):
        return self.damage_modifier

    def apply_buff(self, effect):
        self.buffs.append(effect)

    def apply_debuff(self, effect):
        self.debuffs.append(effect)

    def apply_cast_costs(self, ability):
        self.adrenaline -= ability.adrenaline_cost
        self.adrenaline += ability.adrenaline_increase
        self.adrenaline = max(min(self.adrenaline, 100), 0)

    def get_current_adrenaline(self):
        return self.adrenaline
