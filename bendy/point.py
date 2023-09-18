from vecked import Vector2f


def x_is_between_points(x: float, p0: Vector2f, p1: Vector2f) -> bool:
    return (p0.x < x and p1.x > x) or (p0.x > x and p1.x < x)
