import cairo

from .natural_context import NaturalContext


class BaseDiagram:
    def __init__(
        self,
        width: float = 400,
        height: float = 400,
        scale: float = 200,
        font_size: float = 16,
        center_x_pct: float = 50,
        center_y_pct: float = 50,
    ) -> None:
        self.width = width
        self.height = height
        self.scale = scale
        self.font_size = font_size
        self.center_x_pct = center_x_pct
        self.center_y_pct = center_y_pct

    def draw(self, ctx: NaturalContext) -> None:
        # must be implemented by the children
        pass

    def run_and_save(self, filename: str) -> None:
        shape = complex(self.width, self.height)
        center_x = self.width * self.center_x_pct / 100
        center_y = self.height * (100 - self.center_y_pct) / 100
        center = complex(center_x, center_y)
        with cairo.SVGSurface(filename, self.width, self.height) as surface:
            cairo_ctx = cairo.Context(surface)
            cairo_ctx.set_font_size(self.font_size)
            ctx = NaturalContext(cairo_ctx, shape, self.scale, center)
            ctx.draw_canvas()

            self.draw(ctx)

            surface.finish()
