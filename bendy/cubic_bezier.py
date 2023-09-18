from typing import Iterator

from vecked import Vector2f

from bendy.logging import logger
from bendy.math import inverse_lerp, lerp
from bendy.point import x_is_between_points


class CubicBezier:
    """
    A cubic Bézier curve constructed from four anchor points.
    """

    def __init__(
        self,
        a0: tuple[float, float] | Vector2f,
        a1: tuple[float, float] | Vector2f,
        a2: tuple[float, float] | Vector2f,
        a3: tuple[float, float] | Vector2f,
    ) -> None:
        self.a0 = a0 if isinstance(a0, Vector2f) else Vector2f(a0[0], a0[1])
        self.a1 = a1 if isinstance(a1, Vector2f) else Vector2f(a1[0], a1[1])
        self.a2 = a2 if isinstance(a2, Vector2f) else Vector2f(a2[0], a2[1])
        self.a3 = a3 if isinstance(a3, Vector2f) else Vector2f(a3[0], a3[1])

    def estimate_y(
        self,
        x: float,
        resolution: int = 100,
    ) -> Iterator[float]:
        """
        Yields every estimated y value for `x`.

        `resolutions` describes the resolution of the estimation. Higher values
        lead to greater accuracy but will take longer to calculate.
        """

        logger.debug("Started estimating y for x %f", x)

        if x == self.a0.x:
            yield self.a0.y
            return

        if x == self.a3.x:
            yield self.a3.y
            return

        previous = self.a0

        for point in self.points(resolution + 1, start=1):
            if point.x == x:
                yield point.y

            elif x_is_between_points(x, previous, point):
                xt = inverse_lerp(previous.x, point.x, x)
                yield lerp(previous.y, point.y, xt)

            previous = point

    def lines(self, count: int) -> Iterator[tuple[Vector2f, Vector2f]]:
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
    ) -> Iterator[Vector2f]:
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

    def solve(self, t: float) -> Vector2f:
        """
        Calculates the (x,y) coordinate for the normal value `t`.
        """

        if t < 0.0 or t > 1.0:
            raise ValueError(f"t ({t}) must be >= 0.0 and <= 1.0")

        if t == 0.0:
            return self.a0

        if t == 1.0:
            return self.a3

        return (
            (self.a0 * ((1 - t) * (1 - t) * (1 - t)))
            + (self.a1 * (3 * (1 - t) * (1 - t) * t))
            + (self.a2 * (3 * (1 - t) * t * t))
            + (self.a3 * (t * t * t))
        )
