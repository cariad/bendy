from math import ceil, floor
from pathlib import Path

from PIL import Image, ImageDraw
from vecked import Region2f, Vector2f

from bendy import CompositeCubicBezier


def draw_composite(
    composite: CompositeCubicBezier,
    name: str,
    resolution: int,
    axis: bool = False,
) -> None:
    margin = 50
    width = 500

    position = Vector2f(margin, margin)
    size = Vector2f(width, width) - position - position

    # Flip upside-down so (0, 0) is at the bottom.
    region = Region2f(position, size).upside_down()

    for count in range(1, len(composite) + 1):
        image = Image.new(
            "RGB",
            (width, width),
            (255, 255, 255),
        )

        draw = ImageDraw.Draw(image)

        composite.draw(
            draw,
            region,
            axis=axis,
            count=count,
            estimate_y=range(floor(composite.min.x), ceil(composite.max.x) + 1, 25),
            resolution=resolution,
        )

        filename = "%s_r%i_%i.png" % (
            name,
            resolution,
            count,
        )

        image.save(Path("docs") / filename)


def test_draw(figure_8: CompositeCubicBezier) -> None:
    draw_composite(figure_8, "figure8", 100)
    draw_composite(figure_8, "figure8-axis", 100, axis=True)


def test_estimate_y(figure_8: CompositeCubicBezier) -> None:
    result = figure_8.estimate_y(135)
    assert list(result) == [
        219.83032439156645,
        53.44235033259424,
    ]
