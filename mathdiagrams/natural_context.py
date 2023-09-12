from dataclasses import dataclass
from typing import Self

from cairo import Context

from . import utils
from .canvas import CanvasConfig, CanvasConfigInternal, Canvas


@dataclass
class NaturalContextState:
    center: complex
    scale: float


@dataclass
class CanvasLimits:
    left_bottom: complex
    right_top: complex


class NaturalContext:
    """
    A context that supports the natural mathematical 4 quadrant context
    """

    def __init__(
        self, ctx: Context, scale: float, shape: complex, center: complex | None = None
    ) -> None:
        self.ctx = ctx
        self.scale = scale
        self.shape = shape

        if center is None:
            center = shape / 2
        self.center = center

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
        self.ctx.arc(x, y, radius, angle1, angle2)
        return self

    def circle(self, center: complex, radius: float) -> Self:
        self.arc(center, radius, 0, utils.d2r(360))
        return self

    def draw_canvas(self, config: CanvasConfig = CanvasConfig()) -> Self:
        config_internal = CanvasConfigInternal(self.scale, self.shape, self.center)
        canvas = Canvas(config, config_internal)
        canvas.draw(self.ctx)
        return self
