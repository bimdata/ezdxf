# Copyright (c) 2018-2022 Manfred Moitzi
# License: MIT License
import pathlib
import ezdxf
from ezdxf import zoom
from ezdxf.lldxf.const import VALID_DXF_LINEWEIGHTS

CWD = pathlib.Path("~/Desktop/Outbox").expanduser()
if not CWD.exists():
    CWD = pathlib.Path(".")

doc = ezdxf.new()
msp = doc.modelspace()
for index, weight in enumerate(VALID_DXF_LINEWEIGHTS):
    y = index
    msp.add_line((0, y), (10, y), dxfattribs={"lineweight": weight})
    msp.add_text(
        f"Lineweight: {weight / 100.0:0.2f}", dxfattribs={"height": 0.18}
    ).set_pos((0, y + 0.3))

zoom.extents(msp, factor=1.2)
doc.saveas(CWD / "valid_lineweights.dxf")
