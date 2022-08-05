#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License

from pathlib import Path
import ezdxf
from ezdxf.render import forms
from ezdxf.acis import api as acis

DIR = Path("~/Desktop/Outbox").expanduser()
if not DIR.exists():
    DIR = Path(".")

VERSION = "R2018"
DEBUG = False
doc = ezdxf.new(VERSION)
msp = doc.modelspace()

sphere = forms.sphere()
sphere.translate(10, 0, 0)
# create the ACIS body entity from the uv-sphere mesh (polyhedron)
body = acis.body_from_mesh(sphere)
# create the DXF 3DSOLID entity
solid3d = msp.add_3dsolid()
acis.export_dxf(solid3d, [body])

doc.set_modelspace_vport(5, center=(10, 0))
doc.saveas(DIR / f"acis_uv_sphere_{VERSION}.dxf")
if solid3d.has_binary_data:
    with open(DIR / f"acis_uv_sphere_{VERSION}.sab.txt", "wt") as fp:
        fp.writelines("\n".join(acis.dump_sab_as_text(solid3d.sab)))
else:
    with open(DIR / f"acis_uv_sphere_{VERSION}.sat.txt", "wt") as fp:
        fp.writelines("\n".join(solid3d.sat))
