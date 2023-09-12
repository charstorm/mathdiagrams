"""
This file contains the common utilities related to making mathematical diagrams.
"""

import math
from typing import Callable

import cairo
from cairo import Context

Point = tuple[float, float]
Shape = tuple[float, float]


def d2r(angle: float) -> float:
    """Degree to radian"""
    return angle * math.pi / 180


def polar2xy(angle: float, radius: float = 1.0) -> Point:
    return (radius * math.cos(angle), radius * math.sin(angle))


def parse_hex_color(hexcode: str) -> list[float]:
    "Convert hex code like #fff into values like [1, 1, 1]. Output is in range [0,1]"
    if not hexcode:
        return []
    if hexcode[0] != "#":
        raise ValueError(f"Color {hexcode=} does not start with #")
    hexcode = hexcode[1:]
    limit = 15
    take = 1
    if len(hexcode) in (3, 4):
        pass
    elif len(hexcode) in (6, 8):
        limit = 255
        take = 2
    else:
        raise ValueError(f"Color {hexcode=} does not have proper size")

    result = []
    for start in range(len(hexcode) // take):
        code = hexcode[start * take : (start + 1) * take]
        try:
            value = int(code, 16)
        except ValueError as ex:
            raise ValueError(f"Color {hexcode=} has non-hex chars") from ex
        result.append(value / limit)

    return result


def set_color(ctx: Context, color: str) -> None:
    parsed_color = parse_hex_color(color)
    if not parsed_color:
        return
    if len(parsed_color) == 3:
        ctx.set_source_rgb(*parsed_color)
    elif len(parsed_color) == 4:
        ctx.set_source_rgba(*parsed_color)
    else:
        raise ValueError(f"Improper length for color: {parsed_color}")


def scale_line_width(ctx: Context, scale: float) -> None:
    ctx.set_line_width(ctx.get_line_width() * scale)


def rect_with_border(
    ctx: Context,
    position: Point,
    shape: Shape,
    fill_color: str = "#000",
    border_color: str = "",
    border_width: float = 4,
) -> None:
    """
    Create a rectangle, fill, and apply border.
    """
    x, y = position
    width, height = shape
    # fill the background color
    if fill_color is not None:
        set_color(ctx, fill_color)
        ctx.rectangle(0, 0, width, height)
        ctx.fill()

    if border_color is not None and border_width > 0:
        set_color(ctx, border_color)
        ctx.set_line_width(border_width)
        ctx.rectangle(0, 0, width, height)

    ctx.stroke()


def line(ctx: Context, p1: Point, p2: Point) -> None:
    ctx.move_to(*p1)
    ctx.line_to(*p2)
    ctx.stroke()


def hline(ctx: Context, start: Point, length: float) -> None:
    x0, y0 = start
    end = x0 + length, y0
    line(ctx, start, end)


def vline(ctx: Context, start: Point, length: float) -> None:
    x0, y0 = start
    end = x0, y0 + length
    line(ctx, start, end)


def draw_plus(ctx: Context, position: Point, shape: Shape) -> None:
    x0, y0 = position
    width, height = shape
    hline(ctx, (x0, y0 + height / 2), width)
    vline(ctx, (x0 + width / 2, y0), height)


def multi_line(
    ctx: Context, func: Callable, start: Point, length: float, step: float, count: int
) -> None:
    if func not in (vline, hline):
        raise ValueError("Expects func to be vline or hline")
    x0, y0 = start
    for idx in range(count):
        idx_start = (x0, y0 + idx * step)
        if func == vline:
            idx_start = (x0 + idx * step, y0)
        func(ctx, idx_start, length)


def multi_text(ctx: Context, text_list: list[str], start: Point, shift: Point) -> None:
    x0, y0 = start
    shift_x, shift_y = shift
    for idx, text in enumerate(text_list):
        position = (x0 + shift_x * idx, y0 + shift_y * idx)
        ctx.move_to(*position)
        ctx.show_text(text)
        ctx.stroke()


def get_markers(start: int, end: int, scale: float) -> list[str]:
    return [str(round(val * scale, 3)) for val in range(start, end)]


def print_markers(
    ctx: Context,
    shape: Shape,
    hline_count: int,
    vline_count: int,
    grid_size: float,
    grid_scale: float,
    font_size: int,
    font_face: str,
    font_color: str,
    text_adjust: tuple[float, float, float, float],
) -> None:
    # Setup font config
    if font_size > 0:
        ctx.set_font_size(font_size)

    if font_face:
        ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)

    if font_color:
        set_color(ctx, font_color)

    width, height = shape
    midx, midy = (width / 2, height / 2)
    # Create markers for x and y
    xmarkers1 = get_markers(0, vline_count, grid_scale)
    xmarkers2 = get_markers(1, vline_count, -grid_scale)
    ymarkers1 = get_markers(1, hline_count, grid_scale)
    ymarkers2 = get_markers(1, hline_count, -grid_scale)

    a1, a2, a3, a4 = text_adjust

    multi_text(ctx, xmarkers1, (midx + a1, midy + font_size + a1), (grid_size, 0))
    multi_text(
        ctx,
        xmarkers2,
        (midx - a2 - grid_size - font_size, midy + font_size + a1),
        (-grid_size, 0),
    )
    multi_text(
        ctx, ymarkers1, (midx + a1, midy - grid_size - font_size + a3), (0, -grid_size)
    )
    multi_text(
        ctx, ymarkers2, (midx + a1, midy + grid_size + font_size + a4), (0, grid_size)
    )
    ctx.stroke()


def apply_grid(
    ctx: Context,
    shape: Shape,
    grid_size: float = 50,
    grid_scale: float = 1,
    axis_color: str = "#323232",
    axis_width: float = 1,
    grid_color: str = "#282828",
    font_size: int = 12,
    font_face: str = "Sans",
    font_color: str = "#424242",
    transform: bool = True,
    markers: bool = True,
    text_adjust: tuple[float, float, float, float] = (4, 2, 8, 4),
) -> Context:
    """
    Draw a graph grid, and transform context.
    """
    width, height = shape
    midx, midy = (width / 2, height / 2)
    # Draw x, y axis
    ctx.set_line_width(axis_width)
    if axis_color is not None:
        set_color(ctx, axis_color)
    draw_plus(ctx, (0, 0), shape)

    if grid_color is not None:
        set_color(ctx, grid_color)

    # Draw horizontal lines
    hline_count = int(height / 2 / grid_size)
    multi_line(ctx, hline, (0, midy + grid_size), width, grid_size, hline_count)
    multi_line(ctx, hline, (0, midy - grid_size), width, -grid_size, hline_count)

    # Draw vertical lines
    vline_count = int(width / 2 / grid_size)
    multi_line(ctx, vline, (midx + grid_size, 0), height, grid_size, vline_count)
    multi_line(ctx, vline, (midx - grid_size, 0), height, -grid_size, vline_count)

    if markers:
        print_markers(
            ctx,
            shape,
            hline_count,
            vline_count,
            grid_size,
            grid_scale,
            font_size,
            font_face,
            font_color,
            text_adjust,
        )

    if transform:
        ctx.translate(midx, midy)
        scale = grid_size / grid_scale
        ctx.scale(scale, -scale)
        ctx.set_line_width(1 / scale)

    return ctx


def circle(ctx: Context, center: Point, radius: float, fill: bool = False) -> None:
    x, y = center
    ctx.arc(x, y, radius, 0, d2r(360))
    if fill:
        ctx.fill()
    else:
        ctx.stroke()


def add_vec(p1: Point, p2: Point, scale: float = 1):
    x = p1[0] + p2[0] * scale
    y = p1[1] + p2[1] * scale
    return (x, y)


def marker(
    ctx: Context,
    position: Point,
    text: str,
    angle: float = 2,
    shift: float = 0.02,
    radius: float = 0.01,
) -> None:
    circle(ctx, position, radius, True)
    text_position = add_vec(position, polar2xy(angle, shift))
    print(text_position, text)
    ctx.move_to(*position)
    ctx.scale(10, 10)
    scale_line_width(ctx, 1 / 100)
    ctx.show_text(text)
    ctx.stroke()
