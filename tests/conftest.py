from logging import DEBUG

from pytest import fixture
from vecked import Vector2f

from bendy import CompositeCubicBezier, CubicBezier
from bendy.logging import logger

logger.setLevel(DEBUG)


@fixture
def cubic_bezier() -> CubicBezier:
    return CubicBezier(
        (100, 100),
        (300, 50),
        (200, 450),
        (400, 400),
    )


@fixture
def figure_8() -> CompositeCubicBezier:
    figure_8 = CompositeCubicBezier(
        CubicBezier(
            (150, 50),
            (250, 40),
            (200, 450),
            (300, 400),
        )
    )

    figure_8.append(Vector2f(450, 100), Vector2f(250, 200))
    figure_8.loop()

    return figure_8
