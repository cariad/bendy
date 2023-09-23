from math import ceil, floor
from pathlib import Path

from PIL import Image, ImageDraw
from pytest import mark, raises
from vecked import Region2f, Vector2f

from bendy import CubicBezier


def draw_cubic_bezier_curve(
    curve: CubicBezier,
    name: str,
    resolution: int,
    axis: bool = False,
    est_y: bool = True,
) -> None:
    margin = 50
    width = 500

    position = Vector2f(margin, margin)
    size = Vector2f(width, width) - position - position

    # Flip upside-down so (0, 0) is at the bottom.
    region = Region2f(position, size).upside_down()

    image = Image.new(
        "RGB",
        (width, width),
        (255, 255, 255),
    )

    draw = ImageDraw.Draw(image)

    estimate_y_range = (
        range(
            floor(curve.min.x),
            ceil(curve.max.x) + 1,
            25,
        )
        if est_y
        else None
    )

    curve.draw(
        draw,
        region,
        axis=axis,
        estimate_y=estimate_y_range,
        resolution=resolution,
    )

    filename = "%s_r%i.png" % (
        name,
        resolution,
    )

    image.save(Path("docs") / filename)


def test_draw(cubic_bezier: CubicBezier) -> None:
    draw_cubic_bezier_curve(cubic_bezier, "s", 1)
    draw_cubic_bezier_curve(cubic_bezier, "s", 2)
    draw_cubic_bezier_curve(cubic_bezier, "s", 3)
    draw_cubic_bezier_curve(cubic_bezier, "s", 10)
    draw_cubic_bezier_curve(cubic_bezier, "s", 100)
    draw_cubic_bezier_curve(cubic_bezier, "s-plain", 100, est_y=False)
    draw_cubic_bezier_curve(cubic_bezier, "s-axis", 100, axis=True)


def test_draw__not_draw(cubic_bezier: CubicBezier) -> None:
    with raises(TypeError) as ex:
        cubic_bezier.draw(
            "pizza",
            Region2f(Vector2f(0, 0), Vector2f(1, 1)),
        )

    assert str(ex.value) == "image_draw is not PIL.ImageDraw"


def test_draw_axis__not_draw() -> None:
    with raises(TypeError) as ex:
        CubicBezier.draw_axis(
            "pizza",
            Region2f(Vector2f(0, 0), Vector2f(1, 1)),
            Region2f(Vector2f(0, 0), Vector2f(1, 1)),
            Vector2f(0, 0),
            Vector2f(0, 0),
        )

    assert str(ex.value) == "image_draw is not PIL.ImageDraw"


@mark.parametrize(
    "x, expect",
    [
        (100, [100]),
    ],
)
def test_estimate_y(
    cubic_bezier: CubicBezier,
    x: float,
    expect: list[float],
) -> None:
    estimates = cubic_bezier.estimate_y(x)
    assert list(estimates) == expect


def test_lines__range(cubic_bezier: CubicBezier) -> None:
    with raises(ValueError) as ex:
        list(cubic_bezier.lines(0))

    assert str(ex.value) == "count (0) must be >= 1"


def test_points__range(cubic_bezier: CubicBezier) -> None:
    with raises(ValueError) as ex:
        list(cubic_bezier.points(0))

    assert str(ex.value) == "count (0) must be >= 1"


def test_points(cubic_bezier: CubicBezier) -> None:
    points = cubic_bezier.points(5)

    assert list(points) == [
        (100, 100),
        (203.125, 132.8125),
        (250, 250),
        (296.875, 367.1875),
        (400, 400),
    ]


def test_points__start(cubic_bezier: CubicBezier) -> None:
    points = cubic_bezier.points(5, start=2)

    assert list(points) == [
        (250, 250),
        (296.875, 367.1875),
        (400, 400),
    ]


@mark.parametrize(
    "t, expect",
    [
        (0.0, Vector2f(100, 100)),
        (0.5, Vector2f(250, 250)),
        (1.0, Vector2f(400, 400)),
    ],
)
def test_solve(cubic_bezier: CubicBezier, t: float, expect: Vector2f) -> None:
    assert cubic_bezier.solve(t) == expect


def test_solve__range(cubic_bezier: CubicBezier) -> None:
    with raises(ValueError) as ex:
        cubic_bezier.solve(-1)

    assert str(ex.value) == "t (-1) must be >= 0.0 and <= 1.0"


def test_str(cubic_bezier: CubicBezier) -> None:
    assert str(cubic_bezier) == "((100, 100), (300, 50), (200, 450), (400, 400))"
