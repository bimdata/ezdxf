# Copyright (c) 2010-2022, Manfred Moitzi
# License: MIT License
import pathlib
import ezdxf
from ezdxf.render import Spline
from ezdxf.math import Vec3, Matrix44

CWD = pathlib.Path("~/Desktop/Outbox").expanduser()
if not CWD.exists():
    CWD = pathlib.Path(".")

# ------------------------------------------------------------------------------
# This example shows how to create SPLINE entities.
#
# tutorial: https://ezdxf.mozman.at/docs/tutorials/spline.html
# ------------------------------------------------------------------------------


def draw(msp, points):
    for point in points:
        msp.add_circle(radius=0.1, center=point, dxfattribs={"color": 1})


def main():
    next_frame = Matrix44.translate(0, 5, 0)
    right_frame = Matrix44.translate(10, 0, 0)
    spline_points = Vec3.list([(1.0, 1.0), (2.5, 3.0), (4.5, 2.0), (6.5, 4.0)])

    doc = ezdxf.new("R2000")
    msp = doc.modelspace()

    # draw the fit points itself:
    draw(msp, spline_points)

    # curve with definition points as fit points
    Spline(spline_points).render_as_fit_points(
        msp, method="distance", dxfattribs={"color": 2}
    )
    Spline(spline_points).render_as_fit_points(
        msp, method="uniform", dxfattribs={"color": 3}
    )
    # method = distance ^ 1/2
    Spline(spline_points).render_as_fit_points(
        msp, method="centripetal", dxfattribs={"color": 4}
    )
    # method = distance ^ 1/3
    Spline(spline_points).render_as_fit_points(
        msp, method="centripetal", dxfattribs={"color": 6}
    )

    msp.add_spline(fit_points=spline_points, dxfattribs={"color": 1})
    msp.add_text(
        "Spline.render_as_fit_points() differs from AutoCAD fit point rendering",
        dxfattribs={"height": 0.1},
    ).set_placement(spline_points[0])

    # open uniform b-spline
    spline_points = list(next_frame.transform_vertices(spline_points))
    draw(msp, spline_points)
    msp.add_text(
        "Spline.render_open_bspline() matches AutoCAD",
        dxfattribs={"height": 0.1},
    ).set_placement(spline_points[0])
    Spline(spline_points).render_open_bspline(
        msp, degree=3, dxfattribs={"color": 3}
    )  # B-spline defined by control points, open uniform knots
    msp.add_open_spline(
        control_points=spline_points, degree=3, dxfattribs={"color": 4}
    )

    rbspline_points = list(right_frame.transform_vertices(spline_points))

    # uniform b-spline
    spline_points = list(next_frame.transform_vertices(spline_points))
    draw(msp, spline_points)
    msp.add_text(
        "Spline.render_uniform_bspline() matches AutoCAD",
        dxfattribs={"height": 0.1},
    ).set_placement(spline_points[0])
    Spline(spline_points).render_uniform_bspline(
        msp, degree=3, dxfattribs={"color": 3}
    )  # B-spline defined by control points, uniform knots
    spline = msp.add_spline(dxfattribs={"color": 4})
    spline.set_uniform(
        control_points=spline_points, degree=3
    )  # has no factory method

    # rational open uniform b-spline
    spline_points = rbspline_points
    weights = [1, 50, 50, 1]
    draw(msp, spline_points)
    Spline(spline_points).render_open_rbspline(
        msp, weights=weights, degree=3, dxfattribs={"color": 3}
    )  # Rational B-spline defined by control points, open uniform knots
    msp.add_rational_spline(
        control_points=spline_points,
        weights=weights,
        degree=3,
        dxfattribs={"color": 4},
    )
    msp.add_text(
        "Spline.render_open_rbspline() matches AutoCAD",
        dxfattribs={"height": 0.1},
    ).set_placement(spline_points[0])

    filename = CWD / "spline.dxf"
    doc.saveas(filename)
    print(f"drawing {filename} created.")


if __name__ == "__main__":
    main()
