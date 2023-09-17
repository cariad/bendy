from typing import Iterable

from bendy.logging import logger
from bendy.math import inverse_lerp, lerp
from bendy.point import Point, add_points, multiply_point, x_is_between_points


class CubicBezier:
    """
    A cubic Bézier curve constructed from four anchor points.
    """

    def __init__(
        self,
        a0: Point,
        a1: Point,
        a2: Point,
        a3: Point,
    ) -> None:
        self.a0 = a0
        self.a1 = a1
        self.a2 = a2
        self.a3 = a3

    def estimate_y(
        self,
        x: float,
        resolution: int = 100,
    ) -> Iterable[float]:
        """
        Yields every estimated y value for `x`.

        `resolutions` describes the resolution of the estimation. Higher values
        lead to greater accuracy but will take longer to calculate.
        """

        logger.debug("Started estimating y for x %f", x)

        if x == self.a0[0]:
            yield self.a0[1]
            return

        if x == self.a3[0]:
            yield self.a3[1]
            return

        previous = self.a0

        for point in self.points(resolution + 1, start=1):
            if point[0] == x:
                yield point[1]

            elif x_is_between_points(x, previous, point):
                xt = inverse_lerp(previous[0], point[0], x)
                yield lerp(previous[1], point[1], xt)

            previous = point

    def lines(self, count: int) -> Iterable[tuple[Point, Point]]:
        """
        Calculates a set of lines that describe the curve.

        `count` describes the number of lines to calculate. More lines lead
        to more accuracy.
        """

        if count < 1:
            raise ValueError(f"count ({count}) must be >= 1")

        prev_end = self.a0

        for point in self.points(count + 1, start=1):
            yield prev_end, point
            prev_end = point

    def points(
        self,
        count: int,
        start: int = 0,
    ) -> Iterable[Point]:
        """
        Calculates a set of points that describe the curve.

        `count` describes the number of points to calculate. More points lead
        to more accuracy.

        `start` describes the point index to start calculating from.
        """

        if count < 1:
            raise ValueError(f"count ({count}) must be >= 1")

        for i in range(start, count):
            yield self.solve(i / (count - 1))

    def solve(self, t: float) -> Point:
        """
        Calculates the (x,y) coordinate for the normal value `t`.
        """

        if t < 0.0 or t > 1.0:
            raise ValueError(f"t ({t}) must be >= 0.0 and <= 1.0")

        if t == 0.0:
            return self.a0

        if t == 1.0:
            return self.a3

        return add_points(
            multiply_point(self.a0, (1 - t) * (1 - t) * (1 - t)),
            multiply_point(self.a1, 3 * (1 - t) * (1 - t) * t),
            multiply_point(self.a2, 3 * (1 - t) * t * t),
            multiply_point(self.a3, t * t * t),
        )
