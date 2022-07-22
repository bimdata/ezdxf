# Copyright (c) 2022, Manfred Moitzi
# License: MIT License

from __future__ import annotations
from typing import Iterable, Iterator, List, Tuple, Sequence
from ezdxf.math import Vec2, UVec, Vec3


__all__ = [
    "mapbox_earcut_2d",
    "mapbox_earcut_3d",
]


def simple_polygon_triangulation(
    face: Iterable[Vec3],
) -> List[Sequence[Vec3]]:
    """Simple triangulation of convex polygons.

    This function creates regular triangles by adding a center-vertex in the
    middle of the polygon, but works only for convex shapes.

    .. versionadded:: 0.18

    """
    face_: List[Vec3] = list(face)
    assert len(face_) > 2
    if not face_[0].isclose(face_[-1]):
        face_.append(face_[0])
    center = Vec3.sum(face_[:-1]) / (len(face_) - 1)
    return [(v1, v2, center) for v1, v2 in zip(face_, face_[1:])]


def mapbox_earcut_2d(
    exterior: Iterable[UVec], holes: Iterable[Iterable[UVec]] = None
) -> List[Sequence[Vec2]]:
    """Mapbox triangulation algorithm with hole support for 2D polygons.

    Args:
        exterior: exterior polygon as iterable of :class:`Vec2` objects
        holes: iterable of holes as iterable of :class:`Vec2` objects, a hole
            with single point represents a Steiner point.

    Returns:
        yields the result as 3-tuples of :class:`Vec2` objects

    """
    from ._mapbox_earcut import earcut

    points: Sequence[Vec2] = Vec2.list(exterior)
    if len(points) == 0:
        return []
    holes_: Sequence[Sequence[Vec2]] = []
    if holes:
        holes_ = [Vec2.list(hole) for hole in holes]
    return earcut(points, holes_)


def mapbox_earcut_3d(
    exterior: Iterable[UVec], holes: Iterable[Iterable[UVec]] = None
) -> Iterator[Tuple[Vec3, Vec3, Vec3]]:
    """Mapbox triangulation algorithm with hole support for flat
    3D polygons.

    Raise:
        TypeError: invalid input data type
        ZeroDivisionError: normal vector calculation failed

    .. versionadded:: 0.18

    """
    from ._mapbox_earcut import earcut

    from ezdxf.math import safe_normal_vector, OCS

    polygon = list(exterior)
    if len(polygon) == 0:
        return

    if not isinstance(polygon[0], Vec3):
        raise TypeError("Vec3() as input type required")
    if polygon[0].isclose(polygon[-1]):
        polygon.pop()
    count = len(polygon)
    if count < 3:
        return
    if count == 3:
        yield polygon[0], polygon[1], polygon[2]
        return

    ocs = OCS(safe_normal_vector(polygon))
    elevation = ocs.from_wcs(polygon[0]).z  # type: ignore
    exterior_ocs = tuple(ocs.points_from_wcs(polygon))
    holes_ocs: Sequence[Sequence[Vec3]] = []
    if holes:
        holes_ocs = [tuple(ocs.points_from_wcs(hole)) for hole in holes]

    for triangle in earcut(exterior_ocs, holes_ocs):
        yield tuple(  # type: ignore
            ocs.points_to_wcs(Vec3(v.x, v.y, elevation) for v in triangle)
        )
