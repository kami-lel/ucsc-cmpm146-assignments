import sys
import logging

sys.path.insert(0, "../")
from planet_wars import issue_order


def attack_weakest_enemy_planet(state):
    # (1) If we currently have a fleet in flight, abort plan.
    if len(state.my_fleets()) >= 1:
        return False

    # (2) Find my strongest planet.
    strongest_planet = max(
        state.my_planets(), key=lambda t: t.num_ships, default=None
    )

    # (3) Find the weakest enemy planet.
    weakest_planet = min(
        state.enemy_planets(), key=lambda t: t.num_ships, default=None
    )

    if not strongest_planet or not weakest_planet:
        # No legal source or destination
        return False
    else:
        # (4) Send half the ships from my strongest planet to the weakest enemy planet.
        return issue_order(
            state,
            strongest_planet.ID,
            weakest_planet.ID,
            strongest_planet.num_ships / 2,
        )


def spread_to_weakest_neutral_planet(state):
    # (1) If we currently have a fleet in flight, just do nothing.
    if len(state.my_fleets()) >= 1:
        return False

    # (2) Find my strongest planet.
    strongest_planet = max(
        state.my_planets(), key=lambda p: p.num_ships, default=None
    )

    # (3) Find the weakest neutral planet.
    weakest_planet = min(
        state.neutral_planets(), key=lambda p: p.num_ships, default=None
    )

    if not strongest_planet or not weakest_planet:
        # No legal source or destination
        return False
    else:
        # (4) Send half the ships from my strongest planet to the weakest enemy planet.
        return issue_order(
            state,
            strongest_planet.ID,
            weakest_planet.ID,
            strongest_planet.num_ships / 2,
        )


def spread_to_close_planets(state):
    quota = 5
    strongest_planet = max(
        state.my_planets(), key=lambda p: p.num_ships, default=None
    )

    invading_planets_id = [
        fleet.destination_planet for fleet in state.my_fleets()
    ]

    # max 5 fleets for invasion
    if not strongest_planet or len(invading_planets_id) >= quota:
        return False

    neutral_planet_stats = []
    for planet in state.neutral_planets():
        if planet.ID in invading_planets_id:
            continue

        planet_dist = state.distance(strongest_planet.ID, planet.ID)
        growth_rate = planet.growth_rate
        ships = planet.num_ships

        stat = (
            (growth_rate * growth_rate)
            - (planet_dist * planet_dist) / 10
            - ships
        )
        opt = (planet, stat)
        neutral_planet_stats.append(opt)

    # sort by stats, best to worst
    planet_stats = sorted(
        neutral_planet_stats, key=lambda x: x[1], reverse=True
    )

    orders = [planet for planet, _ in planet_stats]
    for order, _ in zip(orders, range(quota - len(invading_planets_id))):
        ship_nums = order.num_ships + 1
        issue_order(state, strongest_planet.ID, order.ID, ship_nums)
    return True


def all_out_send_ship(state):
    my_planets = sorted(
        state.my_planets(), key=lambda p: p.num_ships, reverse=True
    )

    not_my_planets = _filter_out_planet_already_being_attacked(
        state, state.not_my_planets()
    )

    coquering = [
        max(
            not_my_planets,
            key=lambda other: state.distance(my.ID, other.ID),
            default=None,
        )
        for my in my_planets
    ]

    for my, ot in zip(my_planets, coquering):
        if not ot:
            continue
        need_to_send = ot.num_ships + 5
        if my.num_ships > need_to_send:

            issue_order(state, my.ID, ot.ID, need_to_send)

    return True


def _filter_out_planet_already_being_attacked(state, planets):
    opt = []
    for p in planets:
        if all(p.ID != f.destination_planet for f in state.my_fleets()):
            opt.append(p)
    return opt


def be_aggressive(state):
    # attack
    my_planets = iter(sorted(state.my_planets(), key=lambda p: p.num_ships))

    enemy_planets = [
        planet
        for planet in state.enemy_planets()
        if not any(
            fleet.destination_planet == planet.ID
            for fleet in state.my_fleets()
        )
    ]
    enemy_planets.sort(key=lambda p: p.num_ships)

    target_planets = iter(enemy_planets)

    try:
        my_planet = next(my_planets)
        target_planet = next(target_planets)
        while True:
            required_ships = (
                target_planet.num_ships
                + state.distance(my_planet.ID, target_planet.ID)
                * target_planet.growth_rate
                + 1
            )

            if my_planet.num_ships > required_ships:
                issue_order(
                    state, my_planet.ID, target_planet.ID, required_ships
                )
                my_planet = next(my_planets)
                target_planet = next(target_planets)
            else:
                my_planet = next(my_planets)

    except StopIteration:
        pass

    # spread
    my_planets = iter(sorted(state.my_planets(), key=lambda p: p.num_ships))

    neutral_planets = [
        planet
        for planet in state.neutral_planets()
        if not any(
            fleet.destination_planet == planet.ID
            for fleet in state.my_fleets()
        )
    ]
    neutral_planets.sort(key=lambda p: p.num_ships)

    target_planets = iter(neutral_planets)

    try:
        my_planet = next(my_planets)
        target_planet = next(target_planets)
        while True:
            required_ships = target_planet.num_ships + 1

            if my_planet.num_ships > required_ships:
                issue_order(
                    state, my_planet.ID, target_planet.ID, required_ships
                )
                my_planet = next(my_planets)
                target_planet = next(target_planets)
            else:
                my_planet = next(my_planets)

    except StopIteration:
        return


def be_defensive(state):
    # sprea
    my_planets = iter(sorted(state.my_planets(), key=lambda p: p.num_ships))

    neutral_planets = [
        planet
        for planet in state.neutral_planets()
        if not any(
            fleet.destination_planet == planet.ID
            for fleet in state.my_fleets()
        )
    ]
    neutral_planets.sort(key=lambda p: p.num_ships)

    target_planets = iter(neutral_planets)

    try:
        my_planet = next(my_planets)
        target_planet = next(target_planets)
        while True:
            required_ships = target_planet.num_ships + 1

            if my_planet.num_ships > required_ships:
                issue_order(
                    state, my_planet.ID, target_planet.ID, required_ships
                )
                my_planet = next(my_planets)
                target_planet = next(target_planets)
            else:
                my_planet = next(my_planets)

    except StopIteration:
        pass

    # defend
    my_planets = [planet for planet in state.my_planets()]
    if not my_planets:
        return

    def strength(p):
        return (
            p.num_ships
            + sum(
                fleet.num_ships
                for fleet in state.my_fleets()
                if fleet.destination_planet == p.ID
            )
            - sum(
                fleet.num_ships
                for fleet in state.enemy_fleets()
                if fleet.destination_planet == p.ID
            )
        )

    avg = sum(strength(planet) for planet in my_planets) / len(my_planets)

    weak_planets = [planet for planet in my_planets if strength(planet) < avg]
    strong_planets = [
        planet for planet in my_planets if strength(planet) > avg
    ]

    if (not weak_planets) or (not strong_planets):
        return

    weak_planets = iter(sorted(weak_planets, key=strength))
    strong_planets = iter(sorted(strong_planets, key=strength, reverse=True))

    try:
        weak_planet = next(weak_planets)
        strong_planet = next(strong_planets)
        while True:
            need = int(avg - strength(weak_planet))
            have = int(strength(strong_planet) - avg)

            if have >= need > 0:
                issue_order(state, strong_planet.ID, weak_planet.ID, need)
                weak_planet = next(weak_planets)
            elif have > 0:
                issue_order(state, strong_planet.ID, weak_planet.ID, have)
                strong_planet = next(strong_planets)
            else:
                strong_planet = next(strong_planets)

    except StopIteration:
        return True


def be_productive(state):
    my_planets = iter(
        sorted(state.my_planets(), key=lambda p: p.num_ships, reverse=True)
    )

    target_planets = [
        planet
        for planet in state.not_my_planets()
        if not any(
            fleet.destination_planet == planet.ID
            for fleet in state.my_fleets()
        )
    ]
    target_planets = iter(
        sorted(target_planets, key=lambda p: p.num_ships, reverse=True)
    )

    try:
        my_planet = next(my_planets)
        target_planet = next(target_planets)
        while True:
            if target_planet.owner == 0:
                required_ships = target_planet.num_ships + 1
            else:
                required_ships = (
                    target_planet.num_ships
                    + state.distance(my_planet.ID, target_planet.ID)
                    * target_planet.growth_rate
                    + 1
                )

            if my_planet.num_ships > required_ships:
                issue_order(
                    state, my_planet.ID, target_planet.ID, required_ships
                )
                my_planet = next(my_planets)
                target_planet = next(target_planets)
            else:
                target_planet = next(target_planets)

    except StopIteration:
        return True


def be_spready(state):
    my_planets = iter(sorted(state.my_planets(), key=lambda p: p.num_ships))

    neutral_planets = [
        planet
        for planet in state.neutral_planets()
        if not any(
            fleet.destination_planet == planet.ID
            for fleet in state.my_fleets()
        )
    ]
    neutral_planets.sort(key=lambda p: p.num_ships)

    target_planets = iter(neutral_planets)

    try:
        my_planet = next(my_planets)
        target_planet = next(target_planets)
        while True:
            required_ships = target_planet.num_ships + 1

            if my_planet.num_ships > required_ships:
                issue_order(
                    state, my_planet.ID, target_planet.ID, required_ships
                )
                my_planet = next(my_planets)
                target_planet = next(target_planets)
            else:
                my_planet = next(my_planets)

    except StopIteration:
        pass

    my_planets = iter(sorted(state.my_planets(), key=lambda p: p.num_ships))

    enemy_planets = [
        planet
        for planet in state.enemy_planets()
        if not any(
            fleet.destination_planet == planet.ID
            for fleet in state.my_fleets()
        )
    ]
    enemy_planets.sort(key=lambda p: p.num_ships)

    target_planets = iter(enemy_planets)

    try:
        my_planet = next(my_planets)
        target_planet = next(target_planets)
        while True:
            required_ships = (
                target_planet.num_ships
                + state.distance(my_planet.ID, target_planet.ID)
                * target_planet.growth_rate
                + 1
            )

            if my_planet.num_ships > required_ships:
                issue_order(
                    state, my_planet.ID, target_planet.ID, required_ships
                )
                my_planet = next(my_planets)
                target_planet = next(target_planets)
            else:
                my_planet = next(my_planets)

    except StopIteration:
        return True
