import math
from heapq import heappush, heappop

def find_path(source_point, destination_point, mesh, algorithm="bas"):
    """
    Searches for a path from `source_point` to `destination_point` through the `mesh`
    using the Bidirectional A* algorithm with paths crossing over box content and edges.

    Returns:
        - A path (list of points) from `source_point` to `destination_point` if exists
        - List of boxes explored by the algorithm
    """
    mesh_adj = mesh['adj']
    boxes = mesh['boxes']

    # Initialize data structures for forward and backward searches
    f_explored = set()
    b_explored = set()
    f_costs = {}
    b_costs = {}
    f_came_from = {}
    b_came_from = {}
    f_detail_points = {}
    b_detail_points = {}
    f_frontier = []
    b_frontier = []

    # Find boxes containing source and destination
    src_box = find_box_of_point(source_point, mesh)
    dest_box = find_box_of_point(destination_point, mesh)

    if src_box is None or dest_box is None:
        # Can't find a path if source or destination is not in any box
        print("No Path")
        return ([], [])

    # Initialize forward search
    f_costs[src_box] = 0
    f_came_from[src_box] = None
    f_detail_points[src_box] = source_point
    heappush(f_frontier, (0, src_box))

    # Initialize backward search
    b_costs[dest_box] = 0
    b_came_from[dest_box] = None
    b_detail_points[dest_box] = destination_point
    heappush(b_frontier, (0, dest_box))

    meeting_box = None

    while f_frontier and b_frontier:
        # Expand forward frontier
        _, f_current_box = heappop(f_frontier)
        f_explored.add(f_current_box)

        if f_current_box in b_explored:
            meeting_box = f_current_box
            break

        f_neighbors = mesh_adj.get(f_current_box, [])

        for neighbor in f_neighbors:
            prev_pt = f_detail_points[f_current_box]
            next_pt = find_detail_points(f_current_box, neighbor)
            move_cost = distance(prev_pt, next_pt)
            new_cost = f_costs[f_current_box] + move_cost

            if neighbor in f_costs and new_cost >= f_costs[neighbor]:
                continue

            f_costs[neighbor] = new_cost
            f_came_from[neighbor] = f_current_box
            f_detail_points[neighbor] = next_pt

            priority = new_cost + heuristic(next_pt, destination_point)
            heappush(f_frontier, (priority, neighbor))

        # Expand backward frontier
        _, b_current_box = heappop(b_frontier)
        b_explored.add(b_current_box)

        if b_current_box in f_explored:
            meeting_box = b_current_box
            break

        b_neighbors = mesh_adj.get(b_current_box, [])

        for neighbor in b_neighbors:
            prev_pt = b_detail_points[b_current_box]
            next_pt = find_detail_points(b_current_box, neighbor)
            move_cost = distance(prev_pt, next_pt)
            new_cost = b_costs[b_current_box] + move_cost

            if neighbor in b_costs and new_cost >= b_costs[neighbor]:
                continue

            b_costs[neighbor] = new_cost
            b_came_from[neighbor] = b_current_box
            b_detail_points[neighbor] = next_pt

            priority = new_cost + heuristic(next_pt, source_point)
            heappush(b_frontier, (priority, neighbor))

    # If meeting box is found, reconstruct the path
    if meeting_box is not None:
        path = reconstruct_bidirectional_path(meeting_box, f_came_from, b_came_from,
                                              f_detail_points, b_detail_points)
        explored = list(f_explored.union(b_explored))
        return (path, explored)
    else:
        # No path found
        print("No Path")
        return ([], list(f_explored.union(b_explored)))

def heuristic(current_point, goal_point):
    return distance(current_point, goal_point)

def distance(pt1, pt2):
    x1, y1 = pt1
    x2, y2 = pt2
    return math.hypot(x2 - x1, y2 - y1)

def find_detail_points(current_box, neighbor_box):
    # Use the midpoint of the shared edge between current_box and neighbor_box
    shared_edges = get_shared_edges(current_box, neighbor_box)
    if shared_edges:
        edge = shared_edges[0]
        pt = get_edge_midpoint(edge)
        return pt
    else:
        # If no shared edge, use middle of the neighbor_box
        return find_box_middle(neighbor_box)

def get_shared_edges(box1, box2):
    # Assuming boxes are rectangles defined as (xmin, xmax, ymin, ymax)
    x1min, x1max, y1min, y1max = box1
    x2min, x2max, y2min, y2max = box2

    shared_edges = []

    # Check vertical edges
    if x1max == x2min or x1min == x2max:
        # Boxes touch vertically
        y_overlap_min = max(y1min, y2min)
        y_overlap_max = min(y1max, y2max)
        if y_overlap_min < y_overlap_max:
            x = x1max if x1max == x2min else x1min
            shared_edges.append(((x, y_overlap_min), (x, y_overlap_max)))

    # Check horizontal edges
    if y1max == y2min or y1min == y2max:
        # Boxes touch horizontally
        x_overlap_min = max(x1min, x2min)
        x_overlap_max = min(x1max, x2max)
        if x_overlap_min < x_overlap_max:
            y = y1max if y1max == y2min else y1min
            shared_edges.append(((x_overlap_min, y), (x_overlap_max, y)))

    return shared_edges

def get_edge_midpoint(edge):
    (x1, y1), (x2, y2) = edge
    mid_x = (x1 + x2) / 2
    mid_y = (y1 + y2) / 2
    return (mid_x, mid_y)

def reconstruct_bidirectional_path(meeting_box, f_came_from, b_came_from,
                                   f_detail_points, b_detail_points):

    # Forward path from source to meeting_box
    path_forward = []
    box = meeting_box
    while box:
        pt = f_detail_points[box]
        path_forward.append(pt)
        box = f_came_from.get(box)

    path_forward.reverse()  # From source to meeting_box

    # Backward path from meeting_box to destination
    path_backward = []
    box = meeting_box
    box = b_came_from.get(box)
    while box:
        pt = b_detail_points[box]
        path_backward.append(pt)
        box = b_came_from.get(box)

    # Combine the paths
    path = path_forward + path_backward

    return path

def find_box_of_point(point, mesh):
    """
    Finds the box that contains the given point.
    """
    boxes = mesh['boxes']
    x, y = point

    for box in boxes:
        xmin, xmax, ymin, ymax = box
        if xmin <= x <= xmax and ymin <= y <= ymax:
            return box

    return None  # Return None if not found

def find_box_middle(box):
    xmin, xmax, ymin, ymax = box
    middle_x = (xmin + xmax) / 2
    middle_y = (ymin + ymax) / 2
    return middle_x, middle_y
