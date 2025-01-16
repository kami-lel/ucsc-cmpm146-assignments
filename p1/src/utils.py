__all__ = [
    "BOXES",
    "ADJ",
    "find_box_of_point",
    "gen_path_from_boxes",
    "find_box_middle",
]


BOXES = "boxes"
ADJ = "adj"


def find_box_of_point(point, mesh):
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


def gen_path_from_boxes(boxes, src_pt=None, dest_pt=None):
    if src_pt is None:
        src_pt = find_box_middle(boxes[0])
    if dest_pt is None:
        dest_pt = find_box_middle(boxes[-1])

    paths = []
    # FIXME only use middle point rn
    for box in boxes:
        tlx, brx, tly, bry = box
        middle_x = (tlx + brx) // 2
        middle_y = (tly + bry) // 2
        pt = (middle_x, middle_y)
        paths.append(pt)
    return paths


def find_box_middle(box):
    tlx, brx, tly, bry = box
    middle_x = (tlx + brx) // 2
    middle_y = (tly + bry) // 2
    return middle_x, middle_y
