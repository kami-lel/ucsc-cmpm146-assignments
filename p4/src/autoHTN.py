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


def declare_methods(data):
    # some recipes are faster than others for the same product even though they might require extra tools
    # sort the recipes so that faster recipes go first

    # your code here
    # hint: call make_method, then declare the method to pyhop using pyhop.declare_methods('foo', m1, m2, ..., mk)

    tasks = {}

    for recipet_name, rule in data["Recipes"].items():

        match = re.fullmatch(r".+ for (.+)", recipet_name)

        if match:
            resource_name = match.group(1)
            method_name = "produce_{}".format(resource_name)

            if method_name not in tasks:
                tasks[method_name] = []

            tasks[method_name].append(make_method(recipet_name, rule))

        else:
            tasks[recipet_name] = [make_method(recipet_name, rule)]

    for task, methods in tasks.items():
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


if __name__ == "__main__":
    rules_filename = "crafting.json"

    with open(rules_filename) as f:
        data = json.load(f)

    state = set_up_state(data, "agent", time=239)  # allot time here
    goals = set_up_goals(data, "agent")

    declare_operators(data)
    declare_methods(data)
    add_heuristic(data, "agent")

    pyhop.print_operators()
    print()
    pyhop.print_methods()

    # Hint: verbose output can take a long time even if the solution is correct;
    # try verbose=1 if it is taking too long

    pyhop.pyhop(state, goals, verbose=3)
    # pyhop.pyhop(state, [('have_enough', 'agent', 'cart', 1),('have_enough', 'agent', 'rail', 20)], verbose=3)
