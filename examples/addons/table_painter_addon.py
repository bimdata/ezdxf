# Copyright (c) 2010-2022, Manfred Moitzi
# License: MIT License
from __future__ import annotations
from typing import TYPE_CHECKING
import pathlib
import ezdxf
from ezdxf.enums import TextEntityAlignment, MTextEntityAlignment
from ezdxf.addons import TablePainter

if TYPE_CHECKING:
    from ezdxf.document import Drawing
    from ezdxf.layouts import BlockLayout
CWD = pathlib.Path("~/Desktop/Outbox").expanduser()
if not CWD.exists():
    CWD = pathlib.Path(".")


# ------------------------------------------------------------------------------
# This add-ons shows how to draw tables by the TablePainter add-on. It's important to
# understand that this table rendering is build up only by DXF primitives which
# are supported by DXF R12.
#
# Features:
# - Text Cell: multiline text build up by TEXT entities (not MTEXT!)
# - Block Cell: block references with attributes
# - cells can span over multiples columns and/or rows
# - individual borderlines styles with render priority
# - background filling by SOLID entities
#
# Limitations:
# - uses the MText add-on to create multiline text out of TEXT entities
# - no automatically text wrapping at border cells
# - no clipping at cell borders
#
# The creation of ACAD_TABLE entities is not supported by ezdxf and probably
# will never be because of the complexity and a lack of usable documentation !
# ------------------------------------------------------------------------------


def get_mat_symbol(doc: Drawing) -> BlockLayout:
    symbol = doc.blocks.new("matsymbol")
    p1 = 0.5
    p2 = 0.25
    points = [
        (p1, p2),
        (p2, p1),
        (-p2, p1),
        (-p1, p2),
        (-p1, -p2),
        (-p2, -p1),
        (p2, -p1),
        (p1, -p2),
    ]

    # should run with DXF R12, do not use add_lwpolyline()
    symbol.add_polyline2d(
        points,
        close=True,
        dxfattribs={
            "color": 2,
        },
    )

    symbol.add_attdef(
        tag="num",
        text="0",
        dxfattribs={
            "height": 0.7,
            "color": 1,
        },
    ).set_align_enum(TextEntityAlignment.MIDDLE)
    return symbol


def table_tutorial():
    doc = ezdxf.new("R2000")  # required for lineweight support
    doc.header["$LWDISPLAY"] = 1  # show lineweights
    doc.styles.add("HEAD", font="OpenSans-ExtraBold.ttf")
    doc.styles.add("CELL", font="OpenSans-Regular.ttf")

    table = TablePainter(
        insert=(0, 0), nrows=4, ncols=4, cell_width=6.0, cell_height=2.0
    )
    table.new_cell_style(
        "head",
        text_style="HEAD",
        text_color=ezdxf.colors.BLUE,
        char_height=0.7,
        bg_color=ezdxf.colors.LIGHT_GRAY,
        align=MTextEntityAlignment.MIDDLE_CENTER,
    )
    # reset default cell style
    default_style = table.get_cell_style("default")
    default_style.text_style = "CELL"
    default_style.char_height = 0.5
    default_style.align = MTextEntityAlignment.BOTTOM_LEFT

    # set header cells
    for col in range(4):
        table.text_cell(0, col, f"Head[{col}]", style="head")

    # set content cell
    for row in range(1, 4):
        for col in range(4):
            # cell style is "default"
            table.text_cell(row, col, f"Cell[{row}, {col}]")

    # draw a red frame around the header
    red_frame = table.new_cell_style("red-frame")
    red_borderline = table.new_border_style(color=ezdxf.colors.RED, lineweight=35)
    # set the red borderline style for all cell borders
    red_frame.set_border_style(red_borderline)
    # create the frame object
    table.frame(0, 0, 4, style="red-frame")
    # render the table, shifting the left-bottom of the table to the origin:
    table.render(doc.modelspace(), insert=(0, table.table_height))

    th = table.table_height
    tw = table.table_width
    doc.set_modelspace_vport(height=th * 1.5, center=(tw/2, th/2))
    filepath = CWD / "table_tutorial.dxf"
    doc.saveas(filepath)


def main():
    doc = ezdxf.new("R12")
    msp = doc.modelspace()

    table = TablePainter(insert=(0, 0), nrows=20, ncols=10)
    # create a new styles
    ctext = table.new_cell_style(
        name="ctext",
        text_color=7,
        char_height=0.5,
        align=MTextEntityAlignment.MIDDLE_CENTER,
    )
    # modify border settings
    border = table.new_border_style(color=6, linetype="DOT", priority=51)
    ctext.set_border_style(border, right=False)

    table.new_cell_style(
        name="vtext",
        text_color=3,
        char_height=0.3,
        align=MTextEntityAlignment.MIDDLE_CENTER,
        rotation=90,  # vertical written
        bg_color=8,
    )
    # set column width, first column has index 0
    table.set_col_width(1, 7)

    # set row height, first row has index 0
    table.set_row_height(1, 7)

    # create a text cell with the default style
    cell1 = table.text_cell(0, 0, "Zeile1\nZeile2", style="ctext")

    # cell spans over 2 rows and 2 cols
    cell1.span = (2, 2)

    table.text_cell(4, 0, "VERTICAL\nTEXT", style="vtext", span=(4, 1))

    # create frames
    table.frame(0, 0, 10, 2, "framestyle")

    # the style can be defined later because it is referenced by the name
    x_border = table.new_border_style(color=4)
    y_border = table.new_border_style(color=17)
    table.new_cell_style(
        name="framestyle",
        left=x_border,
        right=x_border,
        top=y_border,
        bottom=y_border,
    )
    mat_symbol = get_mat_symbol(doc)

    table.new_cell_style(
        name="matsym",
        align=MTextEntityAlignment.MIDDLE_CENTER,
        scale_x=0.6,
        scale_y=0.6,
    )

    # 1st TablePainter rendering
    # Render the table to a layout: the modelspace, a paperspace layout or a
    # block definition.
    table.render(msp, insert=(40, 20))

    # It's not necessary to copy a table for multiple renderings but changes to the
    # table do not affect previous renderings.
    table.new_cell_style(
        name="57deg",
        text_color=2,
        char_height=0.5,
        rotation=57,
        align=MTextEntityAlignment.MIDDLE_CENTER,
        bg_color=123,
    )

    table.text_cell(
        6, 3, "line one\nline two\nand line three", span=(3, 3), style="57deg"
    )

    # 2nd TablePainter rendering
    # create an anonymous block
    block = doc.blocks.new_anonymous_block()
    # Render the table into the block layout at insert location (0, 0):
    table.render(block, insert=(0, 0))
    # add a block reference to the modelspace at location (80, 20)
    msp.add_blockref(block.name, insert=(80, 20))

    # Stacked text: letters are stacked top-to-bottom, but not rotated
    table.new_cell_style(
        name="stacked",
        text_color=6,
        char_height=0.25,
        align=MTextEntityAlignment.MIDDLE_CENTER,
        stacked=True,
    )
    table.text_cell(6, 3, "STACKED FIELD", span=(7, 1), style="stacked")

    for pos in [3, 4, 5, 6]:
        table.block_cell(
            pos, 1, mat_symbol, attribs={"num": pos}, style="matsym"
        )

    # 3rd TablePainter rendering
    # Render table to a layout: the modelspace, a paperspace layout or a block
    # definition.
    table.render(msp, insert=(0, 0))
    doc.set_modelspace_vport(height=70, center=(50, 0))

    filepath = CWD / "table_example2.dxf"
    doc.saveas(filepath)

    print(f"drawing '{filepath}' created.")


if __name__ == "__main__":
    table_tutorial()
    main()
