"""
File name: EffectFactory.py
Author: Matthew Allen
Date: 7/12/20

Description:
    This is meant to take in some JSON data and return an appropriate instance of a subclass of the Effect class.
"""


def load_from_json(json_data):
    """
    Function to instantiate an Effect object and return it based on the type requested in the supplied JSON data.
    :param json_data: Data to read from.
    :return: None
    """

    name = json_data["name"].strip().lower()
    effect = None

    if name == "damage modifier":
        from Environment.Effects import DamageModifierEffect
        effect = DamageModifierEffect()

    elif name == "stun":
        from Environment.Effects import StunEffect
        effect = StunEffect()

    if effect is not None:
        effect.load_from_json(json_data)
        return effect

    # There should probably be an error here or something.
    print("UNABLE TO PARSE EFFECT NAMED {}".format(name.upper()))
    return None