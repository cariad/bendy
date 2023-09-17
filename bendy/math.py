def inverse_lerp(
    a: float,
    b: float,
    v: float,
) -> float:
    """
    Gets the normalised distance of `v` from `a` in the direction of `b`.
    """

    return (v - a) / (b - a)


def lerp(
    a: float,
    b: float,
    t: float,
) -> float:
    """
    Gets the value `t` distance from `a` in the direction of `b`.
    """

    return a + t * (b - a)
