from utils import *


def find_path_brs(source_point, destination_point, mesh):
    mesh_adj = mesh[ADJ]

    explored = {}  # all boxes explored so far: from
    frontier = []

    # find box containing src & dest point
    src_box = find_box_of_point(source_point, mesh)
    dest_box = find_box_of_point(destination_point, mesh)

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
