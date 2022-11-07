# Copyright (c) 2018-2022 Manfred Moitzi
# License: MIT License
import pathlib
import ezdxf
from ezdxf.addons import odafc

CWD = pathlib.Path("~/Desktop/Outbox").expanduser()
if not CWD.exists():
    CWD = pathlib.Path(".")

# ------------------------------------------------------------------------------
# This example shows how to use external references.
# ------------------------------------------------------------------------------

# AutoCAD does not resolve XREFS in DXF R12 Format :-(,
ref_doc = ezdxf.new("R2013")
ref_doc.modelspace().add_circle(
    center=(5, 5), radius=2.5, dxfattribs={"layer": "CIRCLE"}
)
ref_doc.header["$INSBASE"] = (5, 5, 0)  # set insertion point
ref_doc.header["$INSUNITS"] = 6  # set document units to meter
ref_doc.saveas(CWD / "xref.dxf")

# AutoCAD can reference DXF files (>DXF12), but is unwilling to resolve the
# DXF files created by ezdxf, which opened for itself is a total valid DXF
# document.
# The much more friendly BricsCAD has no problem to resolve the DXF xref.

# Export the DXF document as DWG file by the odafc addon, for more information
# see the docs: https://ezdxf.mozman.at/docs/addons/odafc.html
# At least this DWG file is accepted by AutoCAD.

dwg = CWD / "xref.dwg"
try:
    odafc.export_dwg(ref_doc, str(dwg), replace=True)
except odafc.ODAFCError as e:
    print(str(e))

# Add XREFS to host document
host_doc = ezdxf.new("R2013")
host_doc.header["$INSUNITS"] = 6  # set document units to meter
host_doc.add_xref_def(filename="xref.dxf", name="dxf_xref")
host_doc.add_xref_def(filename="xref.dwg", name="dwg_xref")
host_doc.modelspace().add_blockref(name="dxf_xref", insert=(0, 0))
host_doc.modelspace().add_blockref(name="dwg_xref", insert=(10, 0))
host_doc.set_modelspace_vport(height=10, center=(5, 0))
host_doc.saveas(CWD / "host.dxf")
