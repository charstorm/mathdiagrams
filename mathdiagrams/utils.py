import math
import numpy as np
from cairo import Context


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


def d2r(angle: float) -> float:
    """Degree to radian"""
    return angle * math.pi / 180


def p2z(r: float, theta: float) -> complex:
    """Polar to complex"""
    return r * np.exp(1j * theta)


def dot_product(v1: complex, v2: complex) -> float:
    return v1.real * v2.real + v1.imag * v2.imag


def drop_perpendicular(p1: complex, p2: complex, p3: complex) -> complex:
    """
    Drop a perpendicular from p3 to line formed by p1 and p2. Return the meeting point.
    """
    # Shift co-ordinates to p1.
    sp2 = p2 - p1
    sp3 = p3 - p1

    # Find the unit vector along sp2
    u = sp2 / abs(sp2)

    # Project external point (sp3) onto the unit vector
    proj = dot_product(sp3, u)

    # Find the meeting point
    meet = proj * u

    # Shift the point back
    ret = p1 + meet

    return ret
