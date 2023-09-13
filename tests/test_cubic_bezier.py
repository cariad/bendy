from pathlib import Path

from PIL import Image, ImageDraw
from PIL.ImageDraw import ImageDraw as ImageDrawType
from pytest import mark, raises

from bendy import CubicBezier, Point


def draw_anchor(
    d: ImageDrawType,
    point: Point,
    color: tuple[int, int, int],
) -> None:
    size = 8

    a = (point[0] - (size / 2), point[1] - (size / 2))
    b = (point[0] + (size / 2), point[1] + (size / 2))

    d.ellipse([a, b], fill=color)


def draw_anchor_line(
    d: ImageDrawType,
    a: Point,
    b: Point,
) -> None:
    d.line((a, b), fill=(200, 200, 200), width=1)


def draw_cubic_bezier(c: CubicBezier, name: str, resolution: int) -> None:
    width = 500

    image = Image.new(
        "RGB",
        (width, 500),
        (255, 255, 255),
    )

    draw = ImageDraw.Draw(image)

    draw_anchor(draw, c.a0, (255, 0, 0))
    draw_anchor(draw, c.a1, (255, 0, 0))
    draw_anchor(draw, c.a2, (255, 0, 0))
    draw_anchor(draw, c.a3, (255, 0, 0))

    draw_anchor_line(draw, c.a0, c.a1)
    draw_anchor_line(draw, c.a2, c.a3)

    for line in c.lines(resolution):
        draw_curve_segment(draw, line)

    for x in range(0, width, 25):
        for y in c.estimate_y(x, resolution):
            draw_estimated_point(draw, (x, y))

    filename = "%s_r%i.png" % (name, resolution)

    image.save(Path("docs") / filename)


def draw_curve_segment(
    d: ImageDrawType,
    line: tuple[Point, Point],
) -> None:
    d.line(line, fill=(0, 0, 255), width=2)


def draw_estimated_point(
    d: ImageDrawType,
    point: Point,
) -> None:
    size = 10

    d.line(
        [(point[0], point[1] - size), (point[0], point[1] + size)],
        fill=(255, 0, 255),
        width=1,
    )

    d.line(
        [(point[0] - size, point[1]), (point[0] + size, point[1])],
        fill=(255, 0, 255),
        width=1,
    )


def test_images(cubic_bezier: CubicBezier) -> None:
    draw_cubic_bezier(cubic_bezier, "s", 1)
    draw_cubic_bezier(cubic_bezier, "s", 2)
    draw_cubic_bezier(cubic_bezier, "s", 3)
    draw_cubic_bezier(cubic_bezier, "s", 10)
    draw_cubic_bezier(cubic_bezier, "s", 100)


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
        (0.0, (100, 100)),
        (0.5, (250, 250)),
        (1.0, (400, 400)),
    ],
)
def test_solve(cubic_bezier: CubicBezier, t: float, expect: Point) -> None:
    assert cubic_bezier.solve(t) == expect


def test_solve__range(cubic_bezier: CubicBezier) -> None:
    with raises(ValueError) as ex:
        cubic_bezier.solve(-1)

    assert str(ex.value) == "t (-1) must be >= 0.0 and <= 1.0"
