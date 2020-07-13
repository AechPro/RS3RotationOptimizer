"""
File name: CombatSimulator.py
Author: Matthew Allen
Date: 7/12/20

Description:
    This is the core of the simulator. It manipulates a player and the target a player is attacking, triggers every game tick,
    handles the casting of abilities, and allows the user to simulate the game for any number of ticks.
"""


class CombatSimulator(object):
    def __init__(self, player, target):
        """
        Basic constructor.
        :param player: The player to be used in the simulation.
        :param target: The target that the player will be attacking.
        """

        self.player = player
        self.target = target
        self.current_ability = player.get_next_ability()

    def simulate(self, num_ticks):
        """
        Function to simulate combat for some number of ticks.
        :param num_ticks: Number of ticks to run the simulation for.
        :return: The cumulative damage taken by the target during this simulation.
        """
        #print()

        # Reset everything.
        self.target.reset()
        self.player.reset()
        self.current_ability = self.player.get_next_ability()

        # Simulate.
        for i in range(num_ticks):
            self.tick()

        # Return.
        return self.target.damage_taken

    def tick(self):
        self.target.tick()
        self.player.tick()
        self.handle_current_ability()

    def handle_current_ability(self):
        """
        Function to handle the current ability being cast.
        :return: None
        """

        # Assign the current ability locally.
        ability = self.current_ability

        # If the cast is done, we will apply damage, buffs, and debuffs. The ability is then put on cooldown and
        # the next ability is selectd.
        if ability.cast_complete():
            ability.compute_damage_this_tick()
            ability.apply_damage_modifier(self.player.get_current_damage_modifier())

            if self.target.is_stunned():
                #print("APPLYING STUN MOD {} TO {}".format(ability.get_stun_damage_modifier(), ability))
                ability.apply_damage_modifier(ability.get_stun_damage_modifier())

            self.player.apply_ability(ability, friendly=True)
            self.target.apply_ability(ability, friendly=False)

            ability.start_cooldown()
            self.current_ability = self.player.get_next_ability()

        # If the ability can be cast, we'll begin casting it.
        elif ability.can_cast(self.player.get_current_adrenaline()):

            #print("CHANNELING", ability)
            self.current_ability = ability
            ability.start_casting()

        # else:
        #     print("ABILITY {} UNABLE TO CAST".format(ability))
        #     print(ability.can_cast(self.player.adrenaline))
        #     print(ability.cast_timer, ability.cast_time_ticks, ability.cooldown_ticks, ability.cooldown_timer)


        #print(self.target)