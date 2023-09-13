from logging import DEBUG

from pytest import fixture

from bendy.cubic_bezier import CubicBezier
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
