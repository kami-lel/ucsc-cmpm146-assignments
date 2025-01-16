__all__ = ["BOXES", "ADJ", "find_box_of_point"]


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
