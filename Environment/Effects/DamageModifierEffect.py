"""
File name: DamageModifierEffect.py
Author: Matthew Allen
Date: 7/12/20

Description:
    This implements an effect which will adjust the damage modifier of its target.
"""

from Environment.Effects import Effect


class DamageModifierEffect(Effect):
    def __init__(self, damage_modifier=None, max_ticks=None, max_hits=None, effect_type=None):
        """
        :param damage_modifier: Damage modifier to be applied to the target when this ability is triggered.
        :param max_ticks: Superclass data.
        :param max_hits: Superclass data.
        :param effect_type: Superclass data.
        """
        super().__init__(max_ticks=max_ticks,
                         max_hits=max_hits,
                         effect_type=effect_type)

        self.damage_modifier = damage_modifier

    def apply_on_hit(self, target):
        """
        Function to be called when any target with this effect is hit by an ability which triggers on-hit effects.
        It is a bit weird to be checking if this effect is an on-hit type effect when we're already inside the on-hit
        function. It is done this way because every available effect on a target has its apply_on_hit() function called
        every time the target is hit, regardless of the type of that effect. This should be done differently.
        :param target: Target to apply effect to.
        :return: None
        """
        if self.type == Effect.ON_HIT_TYPE:
            value = target.get_damage_modifier()
            value *= self.damage_modifier
            target.set_damage_modifier(value)
        self.active_hits += 1

    def apply_on_tick(self, target):
        """
        Function to be called when a tick happens and any target has this effect on it. This suffers from the same design
        problem as apply_on_hit().
        :param target: Target to apply this effect to.
        :return: None
        """
        if self.type == Effect.ON_TICK_TYPE:
            value = target.get_damage_modifier()
            value *= self.damage_modifier
            target.set_damage_modifier(value)
        self.active_ticks += 1

    def load_subclass_from_json(self, json_data):
        """
        Function to load the damage modifier variable from some JSON data.
        :param json_data: data to be read from.
        :return: None
        """
        self.damage_modifier = json_data["damage modifier"]

    def __str__(self):
        """
        to_string() implementation that turns out to be way too much information to be worth looking at.
        I should rewrite this.
        :return: String representing the state of this effect.
        """

        out = "!DAMAGE MODIFIER EFFECT!\nTYPE: {}\nACTIVE TICKS: {}\nACTIVE HITS: {}\nMAX TICKS: {}\nMAX HITS: {}"\
        .format(self.type, self.active_ticks, self.active_hits, self.max_ticks, self.max_hits)
        return out