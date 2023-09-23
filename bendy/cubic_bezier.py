from __future__ import annotations

from typing import Any, Iterable, Iterator

from vecked import Region2f, Vector2f

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

    def __str__(self) -> str:
        return "(%s, %s, %s, %s)" % (self.a0, self.a1, self.a2, self.a3)

    @property
    def bounds(self) -> Region2f:
        return Region2f(
            self.min,
            self.max - self.min,
        )

    def draw(
        self,
        image_draw: Any,
        pixel_bounds: Region2f,
        curve_bounds: Region2f | None = None,
        resolution: int = 100,
        estimate_y: Iterable[float] | None = None,
    ) -> None:
        try:
            from PIL.ImageDraw import ImageDraw
        except ImportError:  # pragma: no cover
            msg = "Install `bendy[draw]` to enable drawing."  # pragma: no cover
            logger.error(msg)  # pragma: no cover
            raise  # pragma: no cover

        if not isinstance(image_draw, ImageDraw):
            raise TypeError("image_draw is not PIL.ImageDraw")

        curve_bounds = curve_bounds or self.bounds

        def draw_anchor(p: Vector2f) -> None:
            p = curve_bounds.interpolate(p, pixel_bounds)
            size = 8

            a = (p.x - (size / 2), p.y - (size / 2))
            b = (p.x + (size / 2), p.y + (size / 2))

            image_draw.ellipse([a, b], fill=(255, 0, 0))

        def draw_anchor_line(a: Vector2f, b: Vector2f) -> None:
            draw_line(a, b, (200, 200, 200))

        def draw_estimated_point(p: Vector2f) -> None:
            p = curve_bounds.interpolate(p, pixel_bounds)
            size = 10

            image_draw.line(
                [(p.x, p.y - size), (p.x, p.y + size)],
                fill=(255, 0, 255),
                width=1,
            )

            image_draw.line(
                [(p.x - size, p.y), (p.x + size, p.y)],
                fill=(255, 0, 255),
                width=1,
            )

        def draw_line(
            a: Vector2f,
            b: Vector2f,
            fill: tuple[int, int, int],
            width: int = 1,
        ) -> None:
            image_draw.line(
                (
                    curve_bounds.interpolate(a, pixel_bounds).vector,
                    curve_bounds.interpolate(b, pixel_bounds).vector,
                ),
                fill=fill,
                width=width,
            )

        draw_anchor(self.a0)
        draw_anchor(self.a1)
        draw_anchor(self.a2)
        draw_anchor(self.a3)

        draw_anchor_line(self.a0, self.a1)
        draw_anchor_line(self.a2, self.a3)

        for line in self.lines(resolution):
            draw_line(
                line[0],
                line[1],
                (0, 0, 255),
                width=2,
            )

        if estimate_y:
            for x in estimate_y:
                for y in self.estimate_y(x, resolution=resolution):
                    draw_estimated_point(Vector2f(x, y))

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

        if x == self.a3.x:
            yield self.a3.y

        previous = self.a0

        for point in self.points(resolution + 1, start=1):
            if point.x == x:
                yield point.y

            elif x_is_between_points(x, previous, point):
                xt = inverse_lerp(previous.x, point.x, x)
                yield lerp(previous.y, point.y, xt)

            previous = point

    def join(self, a2: Vector2f, a3: Vector2f) -> CubicBezier:
        """
        Creates a new cubic Bézier curve at the end of this one.
        """

        return CubicBezier(
            self.a3,
            self.a2.reflect_across(self.a3).vector,
            a2,
            a3,
        )

    def join_to_start(self, other: CubicBezier) -> CubicBezier:
        """
        Creates a new cubic Bézier curve that connects the end of this curve to
        the start of another.
        """

        return CubicBezier(
            self.a3,
            self.a2.reflect_across(self.a3).vector,
            other.a1.reflect_across(other.a0).vector,
            other.a0,
        )

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

    @property
    def max(self) -> Vector2f:
        return Vector2f(
            max(self.a0.x, self.a1.x, self.a2.x, self.a3.x),
            max(self.a0.y, self.a1.y, self.a2.y, self.a3.y),
        )

    @property
    def min(self) -> Vector2f:
        return Vector2f(
            min(self.a0.x, self.a1.x, self.a2.x, self.a3.x),
            min(self.a0.y, self.a1.y, self.a2.y, self.a3.y),
        )

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
