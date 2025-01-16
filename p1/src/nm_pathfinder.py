BOXES = "boxes"
ADJ = "adj"


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
        return _find_path_brs(source_point, destination_point, mesh)


def _find_box_of_point(point, mesh):
    """
    :param point:
    :type point: tuple(int, int)
    :param mesh:
    :type mesh: dict
    :return: box
    :rtype: tuple(int, int, int, int)
    """
    boxes = mesh[BOXES]
    x, y = point

    for box in boxes:
        tlx, brx, tly, bry = box
        if tlx <= x <= brx and tly <= y <= bry:
            return box

    raise ValueError("can't find point in mesh")


def _find_path_brs(source_point, destination_point, mesh):
    mesh_adj = mesh[ADJ]

    explored = {}  # all boxes explored so far: from
    frontier = []

    # find box containing src & dest point
    src_box = _find_box_of_point(source_point, mesh)
    dest_box = _find_box_of_point(destination_point, mesh)

    explored[src_box] = None  # special case for src box
    # add src into frontier
    frontier.append(src_box)

    while frontier:  # continue if frontier is not empty
        current_box = frontier.pop()
        neighbors = mesh_adj[current_box]
        for nei_box in neighbors:
            if nei_box in explored:
                continue  # skip exolored boxes

            explored[nei_box] = current_box
            frontier.append(nei_box)

        # early exit if found destination
        if dest_box in explored:
            break

    # generate path
    boxes_path = []
    _box = dest_box
    while _box:
        boxes_path.append(_box)
        _box = explored[_box]

    boxes_path.reverse()

    return _generate_points_path_from_box_path(boxes_path), explored


def _generate_points_path_from_box_path(boxes):
    paths = []
    # FIXME only use middle point rn
    for box in boxes:
        tlx, brx, tly, bry = box
        middle_x = (tlx + brx) // 2
        middle_y = (tly + bry) // 2
        pt = (middle_x, middle_y)
        paths.append(pt)
    return paths


def _find_box_middle(box):
    """
    calculate and return the middle point of the given box

    :param box: tuple containing top-left x, bottom-right x, top-left y,
                bottom-right y coordinates of the box
    :type box: tuple
    :return: middle point (x, y) of the box
    :rtype: tuple
    """

    tlx, brx, tly, bry = box
    middle_x = (tlx + brx) // 2
    middle_y = (tly + bry) // 2
    return middle_x, middle_y
