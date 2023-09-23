from typing import Any, Iterable, Iterator

from vecked import Region2f, Vector2f

from bendy.cubic_bezier import CubicBezier
from bendy.logging import logger


class CompositeCubicBezier:
    """
    Composite cubic Bézier curve

    """

    def __init__(self, initial: CubicBezier) -> None:
        self._curves: list[CubicBezier] = [initial]

    def __len__(self) -> int:
        return len(self._curves)

    def append(self, a2: Vector2f, a3: Vector2f) -> CubicBezier:
        new_curve = self.tail.join(a2, a3)
        self._curves.append(new_curve)
        return new_curve

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
        axis: bool = True,
        count: int | None = None,
        estimate_y: Iterable[float] | None = None,
        resolution: int = 100,
        title: str | None = None,
    ) -> None:
        try:
            from PIL.ImageDraw import ImageDraw
        except ImportError:  # pragma: no cover
            msg = "Install `bendy[draw]` to enable drawing."  # pragma: no cover
            logger.error(msg)  # pragma: no cover
            raise  # pragma: no cover

        if not isinstance(image_draw, ImageDraw):
            raise TypeError("image_draw is not PIL.ImageDraw")

        curve_bounds = self.bounds.accommodate(Vector2f(0, 0))

        if title:
            image_draw.text(
                (Vector2f(20, pixel_bounds.top - 30)).vector,
                title,
                fill="black",
            )

        if axis:
            CubicBezier.draw_axis(
                image_draw,
                curve_bounds,
                pixel_bounds,
                self.min,
                self.max,
            )

        count = len(self._curves) if count is None else count

        for index in range(count):
            self._curves[index].draw(
                image_draw,
                pixel_bounds,
                curve_bounds=curve_bounds,
                estimate_y=estimate_y,
                resolution=resolution,
            )

    def estimate_y(
        self,
        x: float,
        resolution: int = 100,
    ) -> Iterator[float]:
        for curve in self._curves:
            estimations = curve.estimate_y(
                x,
                resolution=resolution,
            )

            for y in estimations:
                yield y

    @property
    def head(self) -> CubicBezier:
        return self._curves[0]

    def loop(self) -> None:
        c = self.tail.join_to_start(self.head)
        self._curves.append(c)

    @property
    def max(self) -> Vector2f:
        return Vector2f(
            max(c.max.x for c in self._curves),
            max(c.max.y for c in self._curves),
        )

    @property
    def min(self) -> Vector2f:
        return Vector2f(
            min(c.min.x for c in self._curves),
            min(c.min.y for c in self._curves),
        )

    @property
    def tail(self) -> CubicBezier:
        return self._curves[len(self._curves) - 1]
