#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License

from pathlib import Path
import ezdxf
from ezdxf.math import Vec2
from ezdxf.math.triangulation import mapbox_earcut_2d
from ezdxf.render import forms, hatching

CWD = Path("~/Desktop/Outbox").expanduser()
if not CWD.exists():
    CWD = Path(".")


def triangle_hatching(filename: str):
    doc = ezdxf.new()
    msp = doc.modelspace()
    polygon = list(
        forms.gear(16, top_width=1, bottom_width=3, height=2, outside_radius=10)
    )
    hole = list(forms.circle(16, radius=4))
    msp.add_lwpolyline(polygon, close=True)
    msp.add_lwpolyline(hole, close=True)

    baseline = hatching.HatchBaseLine(
        Vec2(), direction=Vec2(1, 1), offset=Vec2(-1, 1)
    )
    for triangle in mapbox_earcut_2d(polygon, holes=[hole]):
        for line in hatching.hatch_triangle(baseline, triangle):
            msp.add_line(line.start, line.end)
    doc.saveas(CWD / filename)


def polygon_hatching(filename: str):
    doc = ezdxf.new()
    msp = doc.modelspace()
    polygon = Vec2.list(
        forms.gear(16, top_width=1, bottom_width=3, height=2, outside_radius=10)
    )
    hole = Vec2.list(forms.circle(16, radius=4))
    msp.add_lwpolyline(polygon, close=True)
    msp.add_lwpolyline(hole, close=True)
    baseline = hatching.HatchBaseLine(
        Vec2(), direction=Vec2(1, 1), offset=Vec2(-1, 1)
    )
    for line in hatching.hatch_polygons(baseline, [polygon, hole]):
        msp.add_line(line.start, line.end)
    doc.saveas(CWD / filename)


if __name__ == "__main__":
    triangle_hatching("triangle_hatching.dxf")
    polygon_hatching("polygon_hatching.dxf")
