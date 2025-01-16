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

    return (
        gen_path_from_boxes(boxes_path, source_point, destination_point),
        explored,
    )
