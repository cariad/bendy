from functools import reduce

Point = tuple[float, float]

ORIGIN: Point = (0.0, 0.0)


def add_points(*points: Point) -> Point:
    def add(a: Point, b: Point) -> Point:
        return (
            a[0] + b[0],
            a[1] + b[1],
        )

    return reduce(add, points, ORIGIN)


def multiply_point(p: Point, m: float) -> Point:
    return (
        p[0] * m,
        p[1] * m,
    )


def x_is_between_points(x: float, p0: Point, p1: Point) -> bool:
    return (p0[0] < x and p1[0] > x) or (p0[0] > x and p1[0] < x)
