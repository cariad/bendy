from pathlib import Path

from PIL import Image, ImageDraw
from PIL.ImageDraw import ImageDraw as ImageDrawType
from pytest import mark, raises
from vecked import Vector2f

from bendy import CubicBezier


def draw_anchor(
    d: ImageDrawType,
    point: Vector2f,
    color: tuple[int, int, int],
) -> None:
    size = 8

    a = (point.x - (size / 2), point.y - (size / 2))
    b = (point.x + (size / 2), point.y + (size / 2))

    d.ellipse([a, b], fill=color)


def draw_anchor_line(
    d: ImageDrawType,
    a: Vector2f,
    b: Vector2f,
) -> None:
    d.line((a.vector, b.vector), fill=(200, 200, 200), width=1)


def draw_cubic_bezier_curve_at(
    c: CubicBezier,
    draw: ImageDrawType,
    resolution: int,
    width: int,
) -> None:
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
            draw_estimated_point(draw, Vector2f(x, y))


def draw_cubic_bezier_curves(
    cs: list[CubicBezier],
    name: str,
    resolution: int,
) -> None:
    for curve_count in range(1, len(cs) + 1):
        width = 500

        image = Image.new(
            "RGB",
            (width, 500),
            (255, 255, 255),
        )

        draw = ImageDraw.Draw(image)

        for curve_index in range(curve_count):
            c = cs[curve_index]
            draw_cubic_bezier_curve_at(
                c,
                draw,
                resolution,
                width,
            )

        filename = "%s_r%i_%i.png" % (
            name,
            resolution,
            curve_count,
        )

        image.save(Path("docs") / filename)


def draw_curve_segment(
    d: ImageDrawType,
    line: tuple[Vector2f, Vector2f],
) -> None:
    d.line((line[0].vector, line[1].vector), fill=(0, 0, 255), width=2)


def draw_estimated_point(
    d: ImageDrawType,
    point: Vector2f,
) -> None:
    size = 10

    d.line(
        [(point.x, point.y - size), (point.x, point.y + size)],
        fill=(255, 0, 255),
        width=1,
    )

    d.line(
        [(point.x - size, point.y), (point.x + size, point.y)],
        fill=(255, 0, 255),
        width=1,
    )


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


def test_images(cubic_bezier: CubicBezier) -> None:
    draw_cubic_bezier_curves([cubic_bezier], "s", 1)
    draw_cubic_bezier_curves([cubic_bezier], "s", 2)
    draw_cubic_bezier_curves([cubic_bezier], "s", 3)
    draw_cubic_bezier_curves([cubic_bezier], "s", 10)
    draw_cubic_bezier_curves([cubic_bezier], "s", 100)

    a = CubicBezier(
        (150, 50),
        (250, 40),
        (200, 450),
        (300, 400),
    )

    b = a.join(Vector2f(450, 100), Vector2f(250, 200))
    c = b.join_to_start(a)

    draw_cubic_bezier_curves([a, b, c], "figure8", 100)


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
