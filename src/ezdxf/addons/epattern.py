#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License
from __future__ import annotations
from typing import TextIO
import os
import io

import ezdxf
from ezdxf.document import Drawing
from ezdxf.lldxf.tagwriter import TagWriter, AbstractTagWriter

__all__ = ["export_file", "export_stream"]

# This add-on was created to solve this problem: https://github.com/mozman/ezdxf/discussions/789
# But it turned out that this add-on is not needed at all, the files generated by Gerber
# Technology do not follow the ASTM-D6673-10 standard.
#
# This add-on creates non-DXF files to accommodate Gerber Technology's software, but I
# hate creating invalid DXF files, so this add-on will not be merged into the master
# branch nor further maintained.
#
# Use at your own risk!


def export_file(doc: Drawing, filename: str | os.PathLike) -> None:
    fp = io.open(filename, mode="wt", encoding="ascii", errors="dxfreplace")
    export_stream(doc, fp)


def export_stream(doc: Drawing, stream: TextIO) -> None:
    if doc.dxfversion != ezdxf.const.DXF12:
        raise ezdxf.DXFVersionError("only DXF R12 format is supported")
    tagwriter = TagWriter(stream, write_handles=False, dxfversion=ezdxf.const.DXF12)
    _export_sections(doc, tagwriter)


def _export_sections(doc: Drawing, tagwriter: AbstractTagWriter) -> None:
    # export empty header section
    tagwriter.write_str(
        "999\ninvalid DXF file created for usage by Gerber Technology software\n"
    )
    tagwriter.write_str("  0\nSECTION\n  2\nHEADER\n")
    tagwriter.write_tag2(0, "ENDSEC")
    # export block definitions
    _export_blocks(doc, tagwriter)
    # export modelspace content
    tagwriter.write_str("  0\nSECTION\n  2\nENTITIES\n")
    doc.modelspace().entity_space.export_dxf(tagwriter)
    tagwriter.write_tag2(0, "ENDSEC")
    tagwriter.write_tag2(0, "EOF")


def _export_blocks(doc: Drawing, tagwriter: AbstractTagWriter) -> None:
    tagwriter.write_str("  0\nSECTION\n  2\nBLOCKS\n")
    for block_record in doc.block_records:
        if block_record.is_block_layout:
            block_record.export_block_definition(tagwriter)
    tagwriter.write_tag2(0, "ENDSEC")
