"""
File name: Enemy.py
Author: Matthew Allen
Date: 7/12/20

Description:
    This file implements the Enemy class. I envisioned the simulated combat scenario to be one player attacking some number
    of enemies, and expected that I would need to treat enemies significantly differently from the player. However,
    this turned out not to be the case in practice. The Player.py and Enemy.py files could easily be combined into
    one Entity.py (or similar) file and used for both purposes.

"""

class Enemy(object):
    def __init__(self):
        """
        Just a basic constructor.
        """
        self.debuffs = []
        self.buffs = []
        self.damage_modifier = 1
        self.damage_taken = 0
        self.stunned = False

    def tick(self):
        """
        Function to be called once per game tick. This handles all the enemy state variables every tick, and tells every
        buff and debuff to apply its on-tick effect to this enemy.
        :return: None
        """
        self.stunned = False
        self.damage_modifier = 1

        for effect in self.debuffs:
            effect.apply_on_tick(self)
            self._handle_effect_timeout(effect, self.debuffs)

        for effect in self.buffs:
            effect.apply_on_tick(self)
            self._handle_effect_timeout(effect, self.buffs)

        #print("ENEMY\nDAMAGE MOD: {}\nSTUNNED: {}\nDAMAGE TAKEN: {}\n".format(self.damage_modifier, self.stunned, self.damage_taken))

    def apply_ability(self, ability, friendly=False):
        """
        Function to be called whenever an ability is applied to this enemy. This will check if the ability is friendly,
        apply its effects in the appropriate fashion, and deal damage if there is damage to be dealt. Note that this
        (and the equivalent function in Player.py) is the only location where Effect.apply_on_hit() is ever called.

        :param ability: Ability to apply to this enemy.
        :param friendly: Optional flag indicating whether or not this ability is friendly.
        :return: None.
        """
        # Assign some local variables based on the direction that the effects need to go (buffs vs debuffs).
        if friendly:
            self_effects = self.buffs
            ability_effects = ability.get_buffs()
            apply_function = self.apply_buff
        else:
            self_effects = self.debuffs
            ability_effects = ability.get_debuffs()
            apply_function = self.apply_debuff

        # Apply the ability effects appropriately
        for effect in ability_effects:
            apply_function(effect)

        # Anndd check if it's friendly again, subsequently ruining the reasoning for the code above. I should re-write
        # this to make it not check if the target is friendly twice. This function used to be much simpler,
        # and the above code is a remnant from the past.
        if not friendly:
            if ability.counts_as_hit():
                for effect in self_effects:

                    # On-hit effects are triggered here.
                    effect.apply_on_hit(self)
                    self._handle_effect_timeout(effect, self_effects)

            ability.apply_damage_to(self)

    def reset(self):
        """
        Function to reset the internal state of this enemy, and all of its effects.
        :return: None
        """
        self.debuffs = []
        self.buffs = []
        self.damage_modifier = 1
        self.damage_taken = 0
        self.stunned = False

    def _handle_effect_timeout(self, effect, effect_list):
        """
        Function to handle checking if an effect has timed out, and appropriately remove it from a list if it has.
        This could be static, and should honestly be moved into Effect.py or handled otherwise.
        :param effect: Effect to examine.
        :param effect_list: List from which the effect will be removed if it has timed out.
        :return: None
        """
        if effect.is_done():
            effect_list.remove(effect)
            effect.reset()

    def __str__(self):
        """
        to_string() implementation that prints out information about the current state of this enemy.
        :return: String representation of this enemy.
        """
        out = "!ENEMY!\n\n"

        out = "{out}{dashes}CURRENT DEBUFFS:{dashes}".format(out=out, dashes="-"*5)
        if len(self.debuffs) == 0:
            out = "{}\nNone".format(out)
        else:
            for effect in self.debuffs:
                out = "{}\n{}".format(out, effect)

        out = "{out}\n\n{dashes}CURRENT BUFFS:{dashes}".format(out=out, dashes="-"*5)
        if len(self.buffs) == 0:
            out = "{}\nNone".format(out)
        else:
            for effect in self.buffs:
                out = "{}\n{}".format(out, effect)

        out = "{}\n\nDAMAGE MODIFIER: {}\nTOTAL DAMAGE TAKEN: {}\n".format(out, self.damage_modifier, self.damage_taken)

        return out

    def apply_damage(self, damage):
        self.damage_taken += damage * self.damage_modifier

    def apply_buff(self, effect):
        self.buffs.append(effect)

    def apply_debuff(self, effect):
        self.debuffs.append(effect)

    def get_damage_modifier(self):
        return self.damage_modifier

    def set_damage_modifier(self, value):
        self.damage_modifier = value

    def set_stunned(self, state):
        self.stunned = state

    def is_stunned(self):
        return self.stunned