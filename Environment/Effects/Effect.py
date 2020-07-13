"""
File name: Effect.py
Author: Matthew Allen
Date: 7/12/20

Description:
    This is the superclass for all Effects that can be applied by an Ability object. Effects are things like buffs,
    debuffs, DOTs, HOTs, damage modifiers, active prayers, etc. The scope of the effects that I have actually implemented
    is very limited. This class may not be able to support many of the effects in the game, but I will not know what those
    are until I actually encounter them when trying to implement an ability.
"""


class Effect(object):
    ON_HIT_TYPE = "on_hit"
    ON_TICK_TYPE = "on_tick"

    def __init__(self, max_ticks=None, max_hits=None, effect_type=None):
        """
        Basic constructor for an Effect object.
        :param max_ticks: The maximum number of ticks that this effect will last for if it is an on-tick type effect.
        :param max_hits: The maximum number of hits that this effect will last for if it is an on-hit type effect.
        :param effect_type: A string indicating the type of effect that this is.
        """

        self.type = Effect.parse_str_from_type(effect_type)
        self.max_ticks = max_ticks
        self.max_hits = max_hits
        self.active_ticks = 0
        self.active_hits = 0

    def is_done(self):
        """
        Function to return a flag indicating whether or not this effect has timed out.
        :return: The appropriate timeout flag.
        """
        if self.type == Effect.ON_TICK_TYPE:
            return self.active_ticks >= self.max_ticks

        if self.type == Effect.ON_HIT_TYPE:
            return self.active_hits >= self.max_hits

    def reset(self):
        """
        Function to reset this effect. This is called whenever an ability is reset.
        :return: None
        """
        self.active_ticks = 0
        self.active_hits = 0

    def load_from_json(self, json_data):
        """
        Function to load this effect from JSON data.
        :param json_data: data to be read from.
        :return: None
        """

        # Load our variables from this JSON data.
        self.type = Effect.parse_str_from_type(json_data["type"])
        if "max ticks" in json_data.keys():
            self.max_ticks = json_data["max ticks"]

        if "max hits" in json_data.keys():
            self.max_hits = json_data["max hits"]

        # Tell whatever is implementing us to load itself from this JSON data.
        self.load_subclass_from_json(json_data)

    def __str__(self):
        """
        to_string() implementation that is way too full of information to be worth looking at. I should rewrite this.
        :return: String representation of this object.
        """
        out = "!BASIC EFFECT!\nTYPE: {}\nACTIVE TICKS: {}\nACTIVE HITS: {}\nMAX TICKS: {}\nMAX HITS: {}"\
        .format(self.type, self.active_ticks, self.active_hits, self.max_ticks, self.max_hits)
        return out

    @staticmethod
    def parse_str_from_type(effect_type):
        """
        Basic parsing function to look at a string and convert it to either the on-hit effect type or on-tick effect type.
        :param effect_type: String to be converted.
        :return: Appropriate effect type.
        """

        # Default to the on-tick effect. This should probably throw an error instead of letting the user get away with
        # providing an invalid type identifier.
        if effect_type is None:
            return Effect.ON_TICK_TYPE

        # Parse on-hit type identifiers. There's probably a better way to do this, I just don't know anything about regex
        # or string processing.
        t = effect_type.lower().strip()
        if t in ("hit", "on hit", "on_hit", "onhit"):
            return Effect.ON_HIT_TYPE

        #Default case again.
        return Effect.ON_TICK_TYPE

    def load_subclass_from_json(self, json_data):
        raise NotImplementedError

    def apply_on_hit(self, target):
        raise NotImplementedError

    def apply_on_tick(self, target):
        raise NotImplementedError