import cairo
import numpy as np

from cairo import Context
from dataclasses import dataclass

from .utils import set_color

Point = tuple[float, float]
PointWithMarker = tuple[Point, float]
XYTicks = tuple[list[PointWithMarker], list[PointWithMarker]]


@dataclass
class CanvasConfig:
    background_color: str = "#111"
    grid_step: float = 0.2
    axis_color: str = "#323232"
    grid_color: str = "#222"
    font_size: int = 12
    font_face: str = "Sans"
    font_color: str = "#444"
    text_margin: float = 2


@dataclass
class CanvasConfigInternal:
    scale: float
    shape: complex
    center: complex


def split_complex(num: complex) -> tuple[float, float]:
    return num.real, num.imag


class Canvas:
    def __init__(self, config: CanvasConfig, config_internal: CanvasConfigInternal) -> None:
        self.config = config
        self.config_internal = config_internal

        self.width, self.height = split_complex(config_internal.shape)
        self.scale = config_internal.scale
        self.x0, self.y0 = split_complex(config_internal.center)

    def draw_backgroud(self, ctx: Context) -> None:
        set_color(ctx, self.config.background_color)
        ctx.rectangle(0, 0, self.width, self.height)
        ctx.fill()

    def draw_main_axis_pairs(self, ctx: Context) -> None:
        set_color(ctx, self.config.axis_color)
        # x-axis
        ctx.move_to(0, self.y0)
        ctx.line_to(self.width, self.y0)
        ctx.stroke()
        # y-axis
        ctx.move_to(self.x0, 0)
        ctx.line_to(self.x0, self.height)
        ctx.stroke()

    def draw_grid_lines(self, ctx: Context) -> XYTicks:
        set_color(ctx, self.config.grid_color)
        grid_step = self.config.grid_step
        step = grid_step * self.scale

        xticks = []
        yticks = []

        # towards the right
        for idx, x in enumerate(np.arange(self.x0 + step, self.width, step)):
            xticks.append(((x, self.y0), (idx + 1) * grid_step))
        # towards the left
        for idx, x in enumerate(np.arange(self.x0 - step, 0, -step)):
            xticks.append(((x, self.y0), -(idx + 1) * grid_step))
        # draw verticals
        for (x, _y), _ in xticks:
            ctx.move_to(x, 0)
            ctx.line_to(x, self.height)
            ctx.stroke()

        # towards the top
        for idx, y in enumerate(np.arange(self.y0 - step, 0, -step)):
            yticks.append(((self.x0, y), (idx + 1) * grid_step))
        # towards the bottom
        for idx, y in enumerate(np.arange(self.y0 + step, self.height, step)):
            yticks.append(((self.x0, y), -(idx + 1) * grid_step))
        # draw horizontals
        for (_x, y), _ in yticks:
            ctx.move_to(0, y)
            ctx.line_to(self.width, y)
            ctx.stroke()

        return xticks, yticks

    def draw_markers(self, ctx: Context, xyticks: XYTicks) -> None:
        ctx.set_font_size(self.config.font_size)
        ctx.select_font_face(
            self.config.font_face, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL
        )
        set_color(ctx, self.config.font_color)
        margin = self.config.text_margin

        assert len(xyticks) == 2

        for idx, ticks in enumerate(xyticks):
            for (x, y), val in ticks:
                text = str(round(val, 6)).rstrip("0").rstrip(".")
                ext = ctx.text_extents(text)
                if idx == 0:  # xticks
                    y += margin + ext.height
                    if x > self.x0:
                        x += margin
                    else:
                        x -= margin + ext.width
                else:  # yticks
                    x -= margin + ext.width
                    if y < self.y0:
                        y -= margin
                    else:
                        y += margin + ext.height
                ctx.move_to(x, y)
                ctx.show_text(text)
                ctx.stroke()

    def draw(self, ctx: Context):
        ctx.save()
        ctx.set_line_width(1)
        self.draw_backgroud(ctx)
        self.draw_main_axis_pairs(ctx)
        ticks = self.draw_grid_lines(ctx)
        self.draw_markers(ctx, ticks)
