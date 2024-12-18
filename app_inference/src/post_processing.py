def line_intersection(line1, bbox):
    x1, y1, x2, y2 = bbox
    line_x1, line_y1, line_x2, line_y2 = line1

    denominator = ((line_x2 - line_x1) * (y2 - y1)) - ((line_y2 - line_y1) * (x2 - x1))
    if denominator == 0:
        return False

    t_numerator = ((x1 - line_x1) * (y2 - y1)) + ((line_y1 - y1) * (x2 - x1))
    u_numerator = ((x1 - line_x1) * (line_y2 - line_y1)) + ((line_y1 - y1) * (line_x2 - line_x1))

    t = t_numerator / denominator
    u = u_numerator / denominator
    if 0 <= t <= 1 and 0 <= u <= 1:
        return True

    return False
