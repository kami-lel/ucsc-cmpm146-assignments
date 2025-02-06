import sys
import argparse
import pyhop
import json
import re


def check_enough(state, ID, item, num):
    if getattr(state, item)[ID] >= num:
        return []
    return False


def produce_enough(state, ID, item, num):
    return [("produce", ID, item), ("have_enough", ID, item, num)]


pyhop.declare_methods("have_enough", check_enough, produce_enough)


def produce(state, ID, item):
    return [("produce_{}".format(item), ID)]


pyhop.declare_methods("produce", produce)


def make_method(name, rule):
    requires = rule.get("Requires", {})
    consumes = rule.get("Consumes", {})
    requires_and_consumes = {**requires, **consumes}

    def method(state, ID):
        # list of have_enough
        opt = [
            ("have_enough", ID, item, amount)
            for item, amount in requires_and_consumes.items()
        ]
        # op_ method
        op = ("op_{}".format(name), ID)
        opt.append(op)
        return opt

    method.__name__ = name
    return method


def _get_tech_for_sort(method_entry):
    name, _ = method_entry
    if "iron" in name:
        return 3
    elif "stone" in name:
        return 2
    elif "wooden" in name:
        return 1
    else:
        return 0


def declare_methods(data, is_debug=False):
    # some recipes are faster than others for the same product even though they might require extra tools
    # sort the recipes so that faster recipes go first

    # your code here
    # hint: call make_method, then declare the method to pyhop using pyhop.declare_methods('foo', m1, m2, ..., mk)

    tasks = {}

    for recipet_name, rule in data["Recipes"].items():

        match = (
            re.fullmatch(r".+ for (.+)", recipet_name)
            or re.fullmatch(r"craft (.+) at bench", recipet_name)
            or re.fullmatch(r"craft (.+)", recipet_name)
        )

        if match:
            resource_name = match.group(1)
            task_name = "produce_{}".format(resource_name)

            if task_name not in tasks:
                tasks[task_name] = []

            methods = recipet_name, make_method(recipet_name, rule)
            tasks[task_name].append(methods)

        else:
            tasks[recipet_name] = [
                (recipet_name, make_method(recipet_name, rule))
            ]

    # order methods based on technology
    for task, method_entries in tasks.items():
        ordered_entries = sorted(method_entries, key=_get_tech_for_sort)
        tasks[task] = ordered_entries

    if is_debug:
        print("tasks:")
        for task, method_entries in tasks.items():
            print(task)
            for entry in method_entries:
                name, met = entry
                print("\t", name, "\t", repr(met("", "")))

    for task, method_entries in tasks.items():
        methods = [method for name, method in method_entries]
        pyhop.declare_methods(task, *methods)


def make_operator(rule):
    name, content = rule
    produces = content["Produces"]
    requires = content.get("Requires", {})
    consumes = content.get("Consumes", {})
    time = content["Time"]

    requires_and_consumes = {**requires, **consumes}

    def operator(state, ID):
        if state.time[ID] >= time and all(
            getattr(state, key)[ID] >= value
            for key, value in requires_and_consumes.items()
        ):
            for item, amount in produces.items():
                getattr(state, item)[ID] += amount

            for item, amount in consumes.items():
                getattr(state, item)[ID] -= amount

            state.time[ID] -= time
            return state
        return False

    operator.__name__ = "op_{}".format(name)
    return operator


def declare_operators(data):
    # your code here
    # hint: call make_operator, then declare the operator to pyhop using pyhop.declare_operators(o1, o2, ..., ok)

    ops = [make_operator(rule) for rule in data["Recipes"].items()]
    pyhop.declare_operators(*ops)


def add_heuristic(data, ID):
    # prune search branch if heuristic() returns True
    # do not change parameters to heuristic(), but can add more heuristic functions with the same parameters:
    # e.g. def heuristic2(...); pyhop.add_check(heuristic2)
    def heuristic(state, curr_task, tasks, plan, depth, calling_stack):
        # TODO
        # your code here
        return False  # if True, prune this branch

    pyhop.add_check(heuristic)


def set_up_state(data, ID, time=0):
    state = pyhop.State("state")
    state.time = {ID: time}

    for item in data["Items"]:
        setattr(state, item, {ID: 0})

    for item in data["Tools"]:
        setattr(state, item, {ID: 0})

    for item, num in data["Initial"].items():
        setattr(state, item, {ID: num})

    return state


def set_up_goals(data, ID):
    goals = []
    for item, num in data["Goal"].items():
        goals.append(("have_enough", ID, item, num))

    return goals


def test_case_a(state, verbose):
    state.time["agent"] = 1
    state.plank["agent"] = 1
    pyhop.pyhop(state, [("have_enough", "agent", "plank", 1)], verbose=verbose)


def test_case_b(state, verbose):
    state.time["agent"] = 300
    state.plank["agent"] = 0
    pyhop.pyhop(state, [("have_enough", "agent", "plank", 1)], verbose=verbose)


def test_case_c(state, verbose):
    state.time["agent"] = 10
    state.plank["agent"] = 3
    state.stick["agent"] = 2
    pyhop.pyhop(
        state, [("have_enough", "agent", "wooden_pickaxe", 1)], verbose=verbose
    )


def test_case_d(state, verbose):
    state.time["agent"] = 100
    pyhop.pyhop(
        state, [("have_enough", "agent", "iron_pickaxe", 1)], verbose=verbose
    )


def test_case_e(state, verbose):
    state.time["agent"] = 175
    pyhop.pyhop(
        state,
        [
            ("have_enough", "agent", "cart", 1),
            ("have_enough", "agent", "rail", 10),
        ],
        verbose=verbose,
    )


def test_case_f(state, verbose):
    state.time["agent"] = 250
    pyhop.pyhop(
        state,
        [
            ("have_enough", "agent", "cart", 1),
            ("have_enough", "agent", "rail", 20),
        ],
        verbose=verbose,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--test",
        choices=["a", "b", "c", "d", "e", "f"],
        help="Specify which test case to run.",
    )
    parser.add_argument(
        "-d",
        "--debug",
        action="store_true",
    )

    parser.add_argument(
        "-v",
        "--verbosity",
        action="count",
        default=0,
        help="Increase output verbosity",
    )
    parser.add_argument(
        "-r",
        "--recursion",
        type=int,
        default=-1,
        help="Set the recursion limit (-1 for no change)",
    )

    args = parser.parse_args()
    if args.recursion > 1:
        sys.setrecursionlimit(args.recursion)

    rules_filename = "crafting.json"
    with open(rules_filename) as f:
        data = json.load(f)

    state = set_up_state(data, "agent", time=239)
    goals = set_up_goals(data, "agent")

    declare_operators(data)
    declare_methods(data, args.debug)
    add_heuristic(data, "agent")

    if args.debug:
        pyhop.print_operators()
        print()
        pyhop.print_methods()

    else:
        # Call the appropriate test case based on user input
        if args.test == "a":
            test_case_a(state, args.verbosity)
        elif args.test == "b":
            test_case_b(state, args.verbosity)
        elif args.test == "c":
            test_case_c(state, args.verbosity)
        elif args.test == "d":
            test_case_d(state, args.verbosity)
        elif args.test == "e":
            test_case_e(state, args.verbosity)
        elif args.test == "f":
            test_case_f(state, args.verbosity)
        else:
            pyhop.pyhop(state, goals, args.verbosity)
