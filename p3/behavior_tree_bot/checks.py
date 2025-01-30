import logging


def if_neutral_planet_available(state):
    return any(state.neutral_planets())


def have_largest_fleet(state):
    return sum(planet.num_ships for planet in state.my_planets()) + sum(
        fleet.num_ships for fleet in state.my_fleets()
    ) > sum(planet.num_ships for planet in state.enemy_planets()) + sum(
        fleet.num_ships for fleet in state.enemy_fleets()
    )


def if_initial_expansion(state):
    # assume initail expansion when there are a lot of neutral planets
    neutral_planets_cnt = len(state.neutral_planets())
    total_planets_cnt = (
        neutral_planets_cnt
        + len(state.my_planets())
        + len(state.enemy_planets())
    )

    netural_planet_perc = neutral_planets_cnt / total_planets_cnt

    return netural_planet_perc > 0.8


def if_we_are_overwheming(state):
    our_ship_cnt = sum(planet.num_ships for planet in state.my_planets())
    opp_ship_cnt = sum(planet.num_ships for planet in state.enemy_planets())

    our_planet_cnt = len(state.my_planets())
    opp_planet_cnt = len(state.enemy_planets())

    result = (
        our_ship_cnt / max(opp_ship_cnt, 1) > 6
        and our_planet_cnt / max(opp_planet_cnt, 1) > 3
    )
    return result


def if_spread(state):
    # assume initail expansion when there are a lot of neutral planets
    neutral_planets_cnt = len(state.neutral_planets())
    total_planets_cnt = (
        neutral_planets_cnt
        + len(state.my_planets())
        + len(state.enemy_planets())
    )

    netural_planet_perc = neutral_planets_cnt / total_planets_cnt

    return netural_planet_perc > 0.5


def if_defensive(state):
    our_ship_cnt = sum(planet.num_ships for planet in state.my_planets())
    opp_ship_cnt = sum(planet.num_ships for planet in state.enemy_planets())

    our_planet_cnt = len(state.my_planets())
    opp_planet_cnt = len(state.enemy_planets())

    result = (
        our_ship_cnt / max(opp_ship_cnt, 1) < 0.8
        or our_planet_cnt / max(opp_planet_cnt, 1) < 0.8
    )
    return result
