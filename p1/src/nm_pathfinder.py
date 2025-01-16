from brs import find_path_brs


def find_path(source_point, destination_point, mesh, algorithm="brs"):
    """
    searches for a path from ``source_point`` to ``destination_point`` through the ``mesh``

    :param source_point: starting point of the pathfinder
    :type source_point: tuple(int, int)
    :param destination_point: the ultimate goal the pathfinder must reach
    :type destination_point: tuple(int, int)
    :param mesh:
    :type mesh: dict
    :param algorithm: search algorithm to use:
    - 'brs': breadth-first search
    :type algorithm: str
    :return:
        - A path (list of points) from ``source_point`` to ``destination_point`` if exists
        - list of boxes explored by the algorithm
    :rtype: tuple
    """
    # fixme box is (top_left_x, bottom_right_x, top_left_y, bottom_right_y)

    if algorithm == "brs":
        return find_path_brs(source_point, destination_point, mesh)
