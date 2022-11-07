#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License

from pathlib import Path
import ezdxf
from ezdxf.render import forms

CWD = Path("~/Desktop/Outbox").expanduser()
if not CWD.exists():
    CWD = Path(".")

# ------------------------------------------------------------------------------
# This example shows how to use the ezdxf.forms.extrude method to create a prism
# from a concave base polygon. The added face-normals show if the face-orientation
# follows the usual count-clockwise order to build outside pointing faces.
#
# docs: https://ezdxf.mozman.at/docs/render/forms.html#ezdxf.render.forms.extrude
# ------------------------------------------------------------------------------


def main(filepath):
    doc = ezdxf.new()
    msp = doc.modelspace()

    profile = [(0, 0), (10, 0), (10, 10), (8, 10), (8, 2), (0, 2)]
    concave_prism = forms.extrude(
        profile, [(0, 0, 0), (0, 0, 10)], close=True, caps=True
    )
    concave_prism.render_mesh(msp, dxfattribs={"color": 2})
    concave_prism.render_normals(msp, dxfattribs={"color": 6})

    # tessellate prism into triangles:
    triangle_mesh = concave_prism.mesh_tessellation(3)
    triangle_mesh.translate(20, 0, 0)
    triangle_mesh.render_mesh(msp, dxfattribs={"color": 1})
    triangle_mesh.render_normals(msp, dxfattribs={"color": 6})
    doc.saveas(filepath)


if __name__ == "__main__":
    main(CWD / "concave_prism.dxf")
