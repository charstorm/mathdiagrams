from dataclasses import dataclass
from typing import Self

import cairo
from cairo import Context

from . import utils
from .canvas import CanvasConfig, CanvasConfigInternal, Canvas


@dataclass
class NaturalContextState:
    center: complex
    scale: float
    dot_size: float


@dataclass
class CanvasLimits:
    left_bottom: complex
    right_top: complex


class NaturalContext:
    """
    A context that supports the natural mathematical 4 quadrant context
    """

    def __init__(
        self, ctx: Context, shape: complex, scale: float, center: complex | None = None
    ) -> None:
        self.ctx = ctx
        self.ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        self.scale = scale
        self.shape = shape

        if center is None:
            center = shape / 2
        self.center = center
        self.dot_size = 0.015

        self.limits = CanvasLimits(-center / scale, (shape - center) / scale)
        self.history: list[NaturalContextState] = []

    def convert(self, point: complex) -> tuple[float, float]:
        z = point.conjugate() * self.scale + self.center
        return z.real, z.imag

    def move_to(self, point: complex) -> Self:
        self.ctx.move_to(*self.convert(point))
        return self

    def line_to(self, point: complex) -> Self:
        self.ctx.line_to(*self.convert(point))
        return self

    def set_color(self, color: str) -> Self:
        utils.set_color(self.ctx, color)
        return self

    def set_line_width(self, width: float) -> Self:
        self.ctx.set_line_width(width)
        return self

    def stroke(self) -> Self:
        self.ctx.stroke()
        return self

    def fill(self) -> Self:
        self.ctx.fill()
        return self

    def line(self, p1: complex, p2: complex) -> Self:
        self.move_to(p1)
        self.line_to(p2)
        self.stroke()
        return self

    def arc(self, center: complex, radius: float, angle1: float, angle2: float) -> Self:
        x, y = self.convert(center)
        radius = radius * self.scale
        self.ctx.arc(x, y, radius, -angle2, -angle1)
        return self

    def circle(self, center: complex, radius: float) -> Self:
        self.arc(center, radius, 0, utils.d2r(360))
        return self

    def draw_canvas(self, config: CanvasConfig = CanvasConfig()) -> Self:
        config_internal = CanvasConfigInternal(self.scale, self.shape, self.center)
        canvas = Canvas(config, config_internal)
        canvas.draw(self.ctx)
        return self

    def text(
        self,
        position: complex,
        text: str,
        h_align: str = "left",
        v_align: str = "bottom",
    ) -> Self:
        ext = self.ctx.text_extents(text)
        scale = self.scale
        if h_align == "left":
            pass  # default
        elif h_align in ("mid", "middle", "center"):
            position += complex(-ext.width / 2 / scale, 0)
        elif h_align == "right":
            position += complex(-ext.width / scale, 0)
        else:
            raise ValueError(f"Unknown {h_align=}")

        if v_align == "bottom":
            pass  # default
        elif v_align in ("mid", "middle", "center"):
            position += complex(0, -ext.height / 2 / scale)
        elif v_align == "top":
            position += complex(0, -ext.height / scale)
        else:
            raise ValueError(f"Unknown {v_align=}")

        self.move_to(position)
        self.ctx.show_text(text)
        self.ctx.stroke()
        return self

    def mark_dot(self, position: complex, text: str = "", shift: complex = 0j) -> Self:
        self.circle(position, self.dot_size).fill()
        position += shift
        if text:
            h_align = "left" if shift.real >= 0 else "right"
            v_align = "bottom" if shift.imag >= 0 else "top"
            self.text(position, text, h_align=h_align, v_align=v_align)
        return self

    def mark_angle(
        self,
        center: complex,
        radius: float,
        angle1: float,
        angle2: float,
        text: str,
        extend: float = 0.01,
        turn: float = 0,
    ) -> Self:
        self.arc(center, radius, angle1, angle2)
        self.stroke()
        angle_avg = (angle1 + angle2) / 2
        shift = utils.p2z(radius + extend, angle_avg + turn)
        self.text(center + shift, text)
        return self
