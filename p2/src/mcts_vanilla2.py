from mcts_node import MCTSNode
from p2_t3 import Board
from random import choice, randint
from math import sqrt, log
import sys

NUM_NODES = 50  # tree size
EXPLORE_FACTION = 2.0


def traverse_nodes(node, board, state, bot_identity):
    """
    traverse the tree until the end criterion are met.
    find the best expandable node (node with untried action) if it exists,
    or else return a terminal node.

    :param node: A tree node from which the search is traversing.
    :type node: MCTSNode
    :param board: The game setup.
    :type board: Baord
    :param state: The state of the game.
    :type state:
    :param bot_identity: The bot's identity, either 0 or 1.
    :type bot_identity: int
    :return: A node from which the next stage of the search can proceed,
    along with the associated state.
    """
    if node.untried_actions:
        return node, state

    else:
        is_opponent = bool(bot_identity)

        highest_ucb = sys.float_info.min
        best_action = None
        best_node = None

        for action, child_node in node.child_nodes.items():
            child_node_ucb = ucb(child_node, is_opponent)
            if child_node_ucb > highest_ucb:
                best_action = action
                highest_ucb = child_node_ucb
                best_node = child_node

        # recursively traverse
        return traverse_nodes(
            best_node,
            board,
            board.next_state(state, best_action),
            1 - bot_identity,
        )


def expand_leaf(node: MCTSNode, board: Board, state):
    """
    add a new leaf to the tree by creating a new child node for the given node
    (if it is non-terminal).

    :param node: The node for which a child will be added.
    :param board: The game setup.
    :param state: The state of the game.
    :return: The added child node and the state associated with that node.
    """
    # deal with terminal node
    if board.is_ended(state) or not node.untried_actions:
        return node, state

    # randomly select a action from parent node
    action_idx = randint(0, len(node.untried_actions) - 1)
    action = node.untried_actions[action_idx]
    node.untried_actions.pop(action_idx)

    # create new state associated with the new node
    new_state = board.next_state(state, action)
    action_list = board.legal_actions(new_state)

    new_node = MCTSNode(node, action, action_list)

    node.child_nodes[action] = new_node

    return new_node, state


def rollout(board: Board, state):
    """
    given the state of the game, the rollout plays out the remainder randomly.

    :param board: The game setup.
    :param state: The state of the game.
    :return: The terminal game state.
    """
    while not board.is_ended(state):
        possible_actions = board.legal_actions(state)
        action = choice(possible_actions)  # randomly select action
        state = board.next_state(state, action)

    return state


def backpropagate(node: MCTSNode | None, won: bool):
    """
    navigate the tree from a leaf node to the root, updating the win and visit count
    of each node along the path.

    :param node: A leaf node.
    :param won: An indicator of whether the bot won or lost the game.
    """
    while node is not None:
        node.visits += 1
        if won:
            node.wins += 1
        node = node.parent


def ucb(node: MCTSNode, is_opponent: bool):
    """
    calculate the UCB value for the given node from the perspective of the bot.

    :param node: A node.
    :param is_opponent: A boolean indicating whether the last action was performed by the MCTS bot.
    :return: The value of the UCB function for the given node.
    """
    w = node.wins
    n = node.visits
    t = node.parent.visits

    return w / n + EXPLORE_FACTION * sqrt(log(t) / n)


def get_best_action(root_node: MCTSNode):
    """
    select the best action from the root node in the MCTS tree.

    :param root_node: The root node.
    :return: The best action from the root node.
    """

    best_action = None
    max_wins = -1

    for action, child_node in root_node.child_nodes.items():
        if child_node.wins > max_wins:
            best_action = action
            max_wins = child_node.wins

    return best_action


def is_win(board: Board, state, identity_of_bot: int):
    """
    checks if state is a win state for identity_of_bot
    """
    outcome = board.points_values(state)
    assert outcome is not None, "is_win was called on a non-terminal state"
    return outcome[identity_of_bot] == 1


def think(board: Board, current_state):
    """
    perform MCTS by sampling games and calling the appropriate functions
    to construct the game tree.

    :param board: The game setup.
    :param current_state: The current state of the game.
    :return: The action to be taken from the current state.
    """
    bot_identity = board.current_player(current_state)  # 1 or 2
    root_node = MCTSNode(
        parent=None,
        parent_action=None,
        action_list=board.legal_actions(current_state),
    )

    for _ in range(NUM_NODES):
        state = current_state
        node = root_node

        # Do MCTS - This is all you!

        # selection
        node, state = traverse_nodes(node, board, state, bot_identity - 1)

        # expansion
        node, state = expand_leaf(node, board, state)

        # simulation
        terminal_state = rollout(board, state)

        # back-propagation
        backpropagate(node, is_win(board, terminal_state, bot_identity))

    # return an action, typically the most frequently used action (from the root)
    # or the action with the best estimated win rate.
    best_action = get_best_action(root_node)

    print(f"Action chosen: {best_action}")
    return best_action
