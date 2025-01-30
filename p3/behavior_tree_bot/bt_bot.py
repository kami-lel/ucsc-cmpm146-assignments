#!/usr/bin/env python
#

"""
// There is already a basic strategy in place here. You can use it as a
// starting point, or you can throw it out entirely and replace it with your
// own.
"""
import inspect
import logging
import os
import sys
import traceback

logging.basicConfig(
    filename=__file__[:-3] + ".log", filemode="w", level=logging.DEBUG
)
currentdir = os.path.dirname(
    os.path.abspath(inspect.getfile(inspect.currentframe()))
)
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

from behavior_tree_bot.behaviors import (
    attack_weakest_enemy_planet,
    spread_to_weakest_neutral_planet,
    be_aggressive,
    spread_to_close_planets,
    all_out_send_ship,
    be_spready,
    be_defensive,
    be_productive,
)
from behavior_tree_bot.bt_nodes import (
    Action,
    Check,
    Selector,
    Sequence,
)
from behavior_tree_bot.checks import (
    if_initial_expansion,
    have_largest_fleet,
    if_neutral_planet_available,
    if_we_are_overwheming,
    if_spread,
    if_defensive,
)
from planet_wars import PlanetWars, finish_turn


# You have to improve this tree or create an entire new one that is capable
# of winning against all the 5 opponent bots
def setup_behavior_tree():

    # Top-down construction of behavior tree
    root = Selector(name="High Level Ordering of Strategies")

    # avoid conflict, expand into closest planets
    initial_expansion = Sequence(name="Initial Expansion Strategy")
    initial_expansion.child_nodes = [
        Check(if_initial_expansion),
        Action(be_aggressive),
    ]

    # all out attack
    all_out = Sequence(name="All Out Attack")
    all_out.child_nodes = [
        Check(if_we_are_overwheming),
        Action(all_out_send_ship),
    ]

    offensive_plan = Sequence(name="Offensive Strategy")
    largest_fleet_check = Check(have_largest_fleet)
    attack = Action(attack_weakest_enemy_planet)
    offensive_plan.child_nodes = [largest_fleet_check, attack]

    spread_plan = Sequence(name="Spread Plan")
    spread_plan.child_nodes = [Check(if_spread), Action(be_spready)]

    def_plan = Sequence(name="Defensive Plan")
    def_plan.child_nodes = [Check(if_defensive), Action(be_defensive)]

    # spread_sequence = Sequence(name="Spread Strategy")
    # neutral_planet_check = Check(if_neutral_planet_available)
    # spread_action = Action(spread_to_weakest_neutral_planet)
    # spread_sequence.child_nodes = [neutral_planet_check, spread_action]

    root.child_nodes = [
        initial_expansion,
        all_out,
        offensive_plan,
        spread_plan,
        # spread_sequence,
        # attack.copy(),
        Action(be_productive),
    ]

    logging.info("\n" + root.tree_to_string())
    return root


# You don't need to change this function
def do_turn(state):
    behavior_tree.execute(planet_wars)


if __name__ == "__main__":
    logging.basicConfig(
        filename=__file__[:-3] + ".log", filemode="w", level=logging.DEBUG
    )

    behavior_tree = setup_behavior_tree()
    # print(behavior_tree.tree_to_string())  # always print tree
    try:
        map_data = ""
        while True:
            current_line = input()
            if len(current_line) >= 2 and current_line.startswith("go"):
                planet_wars = PlanetWars(map_data)
                do_turn(planet_wars)
                finish_turn()
                map_data = ""
            else:
                map_data += current_line + "\n"

    except KeyboardInterrupt:
        print("ctrl-c, leaving ...")
    except Exception:
        traceback.print_exc(file=sys.stdout)
        logging.exception("Error in bot.")
