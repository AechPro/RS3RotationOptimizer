"""
File name: StunEffect.py
Author: Matthew Allen
Date: 7/12/20

Description:
    A subclass of Effect which applies the stunned debuff to its target every tick. I will leave the functions in this
    undocumented. Please refer to DamageModifierEffect.py and Effect.py for a detailed description of every function.
"""

from Environment.Effects import Effect


class StunEffect(Effect):
    def __init__(self, max_ticks=None, max_hits=None, effect_type=None):
        super().__init__(max_ticks=max_ticks,
                         max_hits=max_hits,
                         effect_type=effect_type)

    def apply_on_hit(self, target):
        pass

    def apply_on_tick(self, target):
        target.set_stunned(True)
        self.active_ticks += 1

    def load_subclass_from_json(self, json_data):
        pass

    def __str__(self):
        out = "!STUN EFFECT!\nTYPE: {}\nACTIVE TICKS: {}\nACTIVE HITS: {}\nMAX TICKS: {}\nMAX HITS: {}"\
        .format(self.type, self.active_ticks, self.active_hits, self.max_ticks, self.max_hits)
        return out
