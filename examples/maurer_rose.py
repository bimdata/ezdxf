# Copyright (c) 2019-2022, Manfred Moitzi
# License: MIT License
from typing import Iterable, Tuple
import pathlib
import math
import ezdxf
from ezdxf import zoom

CWD = pathlib.Path("~/Desktop/Outbox").expanduser()
if not CWD.exists():
    CWD = pathlib.Path(".")

# ------------------------------------------------------------------------------
# draw a maurer rose with LWPOLYLINE entities
# https://en.wikipedia.org/wiki/Maurer_rose
# ------------------------------------------------------------------------------

N = 6  # The rose has n petals if N is odd, and 2N petals if N is even.
D = 71  # delta angle in degrees
STEP360 = math.tau / 360


def maurer_rose(n: int, d: int, radius: float) -> Iterable[Tuple[float, float]]:
    i: float = 0.0
    while i < math.tau:
        k = i * d
        r = radius * math.sin(n * k)
        x = r * math.cos(k)
        y = r * math.sin(k)
        yield x, y
        i += STEP360


def main(filename: str, n: int, d: int) -> None:
    doc = ezdxf.new()
    doc.layers.add("PETALS", color=1)
    doc.layers.add("NET", color=5)
    msp = doc.modelspace()

    msp.add_lwpolyline(
        maurer_rose(n, 1, 250), close=True, dxfattribs={"layer": "PETALS"}
    )
    msp.add_lwpolyline(
        maurer_rose(n, d, 250), close=True, dxfattribs={"layer": "NET"}
    )

    zoom.extents(msp)
    doc.saveas(filename)


if __name__ == "__main__":
    main(str(CWD / "maurer_rose.dxf"), N, D)
