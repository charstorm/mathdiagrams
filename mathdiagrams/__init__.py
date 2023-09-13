import cairo

from .natural_context import NaturalContext


class BaseDiagram:
    def __init__(
        self,
        width: float = 400,
        height: float = 400,
        scale: float = 200,
        font_size: float = 16,
    ) -> None:
        self.width = width
        self.height = height
        self.scale = scale
        self.font_size = font_size

    def draw(self, ctx: NaturalContext) -> None:
        # must be implemented by the children
        pass

    def run_and_save(self, filename: str) -> None:
        shape = complex(self.width, self.height)
        with cairo.SVGSurface(filename, self.width, self.height) as surface:
            cairo_ctx = cairo.Context(surface)
            cairo_ctx.set_font_size(self.font_size)
            ctx = NaturalContext(cairo_ctx, shape, self.scale)
            ctx.draw_canvas()

            self.draw(ctx)

            surface.finish()
