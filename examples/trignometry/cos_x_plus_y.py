"""
Generate SVGs as part of derivation of cos(x+y) = cos(x)cos(y) - sin(x)sin(y)
"""

from mathdiagrams import NaturalContext, BaseDiagram
from mathdiagrams.utils import d2r, p2z


origin = 0j


class MultiChordDiagram(BaseDiagram):
    """
    Distance of chords: single angle case and double angle case
    """

    def __init__(self):
        super().__init__(width=400, height=400, scale=175)
        self.index = 0

    def draw(self, ctx: NaturalContext) -> None:
        colors = "#f00 #f58 #ff0 #08f #b07 #0af".split()
        ctx.set_color("#666").set_line_width(1)
        # Unit circle
        ctx.circle(origin, 1).stroke()

        # Angles
        x = d2r(82)
        y = d2r(30)

        # Points
        p1 = 1 + 0j
        p2 = p2z(1, x)
        p3 = p2z(1, y)

        # Lines
        ctx.set_color(colors[0]).line(origin, p1)
        ctx.set_color(colors[1]).line(origin, p2)
        chord_start = p1
        if self.index == 1:
            chord_start = p3
            ctx.set_color(colors[3]).line(origin, p3)
        ctx.set_color(colors[2]).line(chord_start, p2)

        # Mark angles
        ctx.set_color("#aaa")
        ctx.mark_angle(origin, 0.1, 0, x, "x")
        if self.index == 1:
            ctx.mark_angle(origin, 0.2, 0, y, "y")

        # Mark Points
        ctx.mark_dot(origin, "O", -0.02 - 0.02j)
        ctx.mark_dot(p1, "A", 0.01 + 0.02j)
        ctx.mark_dot(p2, "B", 0.02j)
        if self.index == 1:
            ctx.mark_dot(p3, "C", 0.02j)


class CosXPlusY(BaseDiagram):
    def __init__(self):
        super().__init__(width=400, height=400, scale=175)

    def draw(self, ctx: NaturalContext) -> None:
        ctx.set_color("#666").set_line_width(1)
        # Unit circle
        ctx.circle(origin, 1).stroke()

        # Angles
        x = d2r(55)
        y = d2r(75)
        z = x + y

        # Points
        p1 = 1 + 0j
        p2 = p2z(1, x)
        p3 = p2z(1, z)
        p4 = p2z(1, -y)

        # Lines
        ctx.set_color("#ca8").line(origin, p1)
        ctx.line(origin, p2)
        ctx.line(origin, p3)
        ctx.line(origin, p4)
        ctx.set_color("#f33").line(p1, p3)
        ctx.set_color("#3b3").line(p2, p4)

        # Mark angles
        ctx.set_color("#aaa")
        ctx.mark_angle(origin, 0.07, 0, x, "x")
        ctx.mark_angle(origin, 0.05, x, z, "y", extend=0.04)
        ctx.mark_angle(origin, 0.05, -y, 0, "-y", extend=0.04, turn=-0.4)
        ctx.set_color("#f33").mark_angle(origin, 0.2, 0, z, "x+y", extend=0.03, turn=0.6)
        ctx.set_color("#3b3").mark_angle(origin, 0.18, -y, x, "x+y", extend=0.03, turn=-0.6)

        ctx.set_color("#aaa")
        ctx.mark_dot(origin, "O", -0.02 - 0.02j)
        ctx.mark_dot(p1, "A", 0.01 + 0.02j)
        ctx.mark_dot(p2, "B", 0.02j)
        ctx.mark_dot(p3, "C", -0.02 + 0.02j)
        ctx.mark_dot(p4, "D", -0.02j)


def main() -> None:
    diag1 = MultiChordDiagram()
    diag1.run_and_save("single_chord.svg")
    diag1.index = 1
    diag1.run_and_save("double_chord.svg")

    diag2 = CosXPlusY()
    diag2.run_and_save("cos_sum_angles.svg")


if __name__ == "__main__":
    main()
