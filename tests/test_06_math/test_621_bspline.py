# Copyright (c) 2012-2021 Manfred Moitzi
# License: MIT License
import pytest
from ezdxf.math import Vec3, BSpline, close_vectors
from ezdxf.math.bspline import normalize_knots, subdivide_params, linspace

DEFPOINTS = [
    (0.0, 0.0, 0.0),
    (10.0, 20.0, 20.0),
    (30.0, 10.0, 25.0),
    (40.0, 10.0, 25.0),
    (50.0, 0.0, 30.0),
]

PARAMS = list(linspace(0, 1, 21))


def test_is_clamped(weired_spline1):
    spline = BSpline(DEFPOINTS, order=3)
    assert spline.is_clamped is True
    assert weired_spline1.is_clamped is False


@pytest.mark.parametrize(
    "knots",
    [
        [0.0, 0.0, 0.0, 0.0, 0.5, 1.0, 1.0, 1.0, 1.0],
        [2.0, 2.0, 2.0, 2.0, 3.0, 6.0, 6.0, 6.0, 6.0],
    ],
)
def test_is_a_clamped_bspline(knots):
    s = BSpline(
        control_points=DEFPOINTS,
        knots=knots,
        order=4,
    )
    assert s.is_clamped is True


@pytest.mark.parametrize(
    "knots",
    [
        [0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0],
        [0.0, 0.0, 2.0, 3.0, 4.0, 5.0, 6.0, 8.0, 8.0],
        [0.0, 0.0, 0.0, 3.0, 4.0, 5.0, 8.0, 8.0, 8.0],
        [0.0, 0.0, 0.0, 0.0, 0.5, 1.0, 1.0, 1.0, 1.0000001],
        [0.0, 0.0, 0.0, 0.0000001, 0.5, 1.0, 1.0, 1.0, 1.0],
    ],
    ids=[
        "no repetitive knot values",
        "2 repetitive knot values",
        "3 repetitive knot values",
        "inaccuracy at the end",
        "inaccuracy at the start",
    ],
)
def test_is_not_a_clamped_bspline(knots):
    """To be a clamped B-spline 4 repetitive knot values at the start and at
    the end of the knot vector are required.
    """
    s = BSpline(
        control_points=DEFPOINTS,
        knots=knots,
        order=4,
    )
    assert s.is_clamped is False


def test_normalize_knots():
    assert normalize_knots([0, 0.25, 0.5, 0.75, 1.0]) == [
        0,
        0.25,
        0.5,
        0.75,
        1.0,
    ]
    assert normalize_knots([0, 1, 2, 3, 4]) == [0, 0.25, 0.5, 0.75, 1.0]
    assert normalize_knots([2, 3, 4, 5, 6]) == [0, 0.25, 0.5, 0.75, 1.0]


def test_normalize_knots_if_needed():
    s = BSpline(
        control_points=DEFPOINTS,
        knots=[2, 2, 2, 2, 3, 6, 6, 6, 6],
        order=4,
    )
    k = s.knots()
    assert k[0] == 0.0


def test_bspline_insert_knot():
    bspline = BSpline(
        [
            (0, 0),
            (10, 20),
            (30, 10),
            (40, 10),
            (50, 0),
            (60, 20),
            (70, 50),
            (80, 70),
        ]
    )
    t = bspline.max_t / 2
    assert len(bspline.control_points) == 8
    bspline2 = bspline.insert_knot(t)
    assert len(bspline2.control_points) == 9


def test_transform_interface():
    from ezdxf.math import Matrix44

    spline = BSpline(control_points=[(1, 0, 0), (3, 3, 0), (6, 0, 1)], order=3)
    new_spline = spline.transform(Matrix44.translate(1, 2, 3))
    assert new_spline.control_points[0] == (2, 2, 3)


def test_bezier_decomposition():
    bspline = BSpline.from_fit_points(
        [
            (0, 0),
            (10, 20),
            (30, 10),
            (40, 10),
            (50, 0),
            (60, 20),
            (70, 50),
            (80, 70),
        ]
    )
    bezier_segments = list(bspline.bezier_decomposition())
    assert len(bezier_segments) == 5
    # results visually checked to be correct
    assert close_vectors(
        bezier_segments[0],
        [
            (0.0, 0.0, 0.0),
            (2.02070813064438, 39.58989657555839, 0.0),
            (14.645958536022286, 10.410103424441612, 0.0),
            (30.0, 10.0, 0.0),
        ],
    )
    assert close_vectors(
        bezier_segments[-1],
        [
            (60.0, 20.0, 0.0),
            (66.33216513897267, 43.20202388489432, 0.0),
            (69.54617236126121, 50.37880459351478, 0.0),
            (80.0, 70.0, 0.0),
        ],
    )


def test_cubic_bezier_approximation():
    bspline = BSpline.from_fit_points(
        [
            (0, 0),
            (10, 20),
            (30, 10),
            (40, 10),
            (50, 0),
            (60, 20),
            (70, 50),
            (80, 70),
        ]
    )
    bezier_segments = list(bspline.cubic_bezier_approximation(level=3))
    assert len(bezier_segments) == 28
    bezier_segments = list(bspline.cubic_bezier_approximation(segments=40))
    assert len(bezier_segments) == 40
    # The interpolation is based on cubic_bezier_interpolation()
    # and therefore the interpolation result is not topic of this test.


def test_subdivide_params():
    assert list(subdivide_params([0.0, 1.0])) == [0.0, 0.5, 1.0]
    assert list(subdivide_params([0.0, 0.5, 1.0])) == [
        0.0,
        0.25,
        0.5,
        0.75,
        1.0,
    ]


@pytest.fixture
def weired_spline1():
    # test spline from: 'CADKitSamples\Tamiya TT-01.dxf'
    control_points = [
        (-52.08772752271847, 158.6939842216689, 0.0),
        (-52.08681215879965, 158.5299954819766, 0.0),
        (-52.10118023714384, 158.453369560292, 0.0),
        (-52.15481567142786, 158.3191250853181, 0.0),
        (-52.19398877522381, 158.2621809388646, 0.0),
        (-52.28596439525645, 158.1780834350967, 0.0),
        (-52.33953844794299, 158.1503467960972, 0.0),
        (-52.44810872122953, 158.1300340044323, 0.0),
        (-52.50421992306838, 158.1373171840982, 0.0),
        (-52.6075289246734, 158.1865954546344, 0.0),
        (-52.65514787710273, 158.2285032895921, 0.0),
        (-52.73668761545541, 158.3403743627349, 0.0),
        (-52.77007322118961, 158.4091709021843, 0.0),
        (-52.82282063670695, 158.5633574927312, 0.0),
        (-52.84192253131899, 158.6479284406054, 0.0),
        (-52.86740213628708, 158.8193660227095, 0.0),
        (-52.87386770841857, 158.9069288997418, 0.0),
        (-52.87483030423064, 159.0684635170357, 0.0),
        (-52.86932199691667, 159.1438624785262, 0.0),
        (-52.84560704446005, 159.2697570380293, 0.0),
        (-52.82725914916205, 159.3212520891559, 0.0),
        (-52.75022655463125, 159.4318434990425, 0.0),
        (-52.6670694478151, 159.4452110783386, 0.0),
        (-52.51141458339235, 159.3709884860868, 0.0),
        (-52.45531159130934, 159.3310594465107, 0.0),
        (-52.34571913237574, 159.2278392570542, 0.0),
        (-52.29163139562603, 159.1638425241462, 0.0),
        (-52.19834244727945, 159.0217561474263, 0.0),
        (-52.15835994602539, 158.9423430023927, 0.0),
        (-52.10315233959036, 158.778742732499, 0.0),
        (-52.08772752271847, 158.6939842216689, 0.0),
        (-52.08681215879965, 158.5299954819766, 0.0),
    ]
    knots = [
        -0.0624999999999976,
        -0.0624999999999976,
        0.0,
        0.0,
        0.0624999999999998,
        0.0624999999999998,
        0.1249999999999997,
        0.1249999999999997,
        0.1874999999999996,
        0.1874999999999996,
        0.2499999999999994,
        0.2499999999999994,
        0.3124999999999992,
        0.3124999999999992,
        0.3749999999999991,
        0.3749999999999991,
        0.4374999999999989,
        0.4374999999999989,
        0.4999999999999988,
        0.4999999999999988,
        0.5624999999999987,
        0.5624999999999987,
        0.6249999999999984,
        0.6249999999999984,
        0.7500000000000099,
        0.7500000000000099,
        0.8125000000000074,
        0.8125000000000074,
        0.875000000000005,
        0.875000000000005,
        0.9375000000000024,
        0.9375000000000024,
        1.0,
        1.0,
        1.0625,
        1.0625,
    ]
    return BSpline(control_points, order=4, knots=knots)


def test_weired_closed_spline(weired_spline1):
    # knots are normalized
    assert weired_spline1.knots()[0] == 0
    assert weired_spline1.max_t == 1.0

    first = weired_spline1.point(0)
    last = weired_spline1.point(weired_spline1.max_t)
    assert (
        first.isclose(last, abs_tol=1e-9) is False
    ), "The loaded SPLINE is not a correct closed B-spline."
    for t, p in [
        (0.0, Vec3(-52.08772752271847, 158.6939842216689, 0.0)),
        (0.1, Vec3(-52.11342028962843, 158.42762802551263, 0.0)),
        (0.2, Vec3(-52.32946275107123, 158.16060743164581, 0.0)),
        (0.3, Vec3(-52.61574269538248, 158.1996048336622, 0.0)),
        (0.4, Vec3(-52.81140581379403, 158.5333668544585, 0.0)),
        (0.5, Vec3(-52.87434900632459, 158.9876962083887, 0.0)),
        (0.6, Vec3(-52.81611529394961, 159.33426729288806, 0.0)),
        (0.7, Vec3(-52.62299843370519, 159.41789638441713, 0.0)),
        (0.8, Vec3(-52.335530988257595, 159.21191342347686, 0.0)),
        (0.9, Vec3(-52.11567764442737, 158.81115356150667, 0.0)),
        (1.0, Vec3(-52.13358634818519, 158.3800216821037, 0.0)),
    ]:
        assert weired_spline1.point(t).isclose(p)


def test_bezier_decomposition_issue(weired_spline1):
    assert weired_spline1.is_rational is False
    assert weired_spline1.is_clamped is False
    with pytest.raises(TypeError):
        list(weired_spline1.bezier_decomposition())


# visually checked:
EXPECTED_FLATTENING = [
    Vec3(0.0, 0.0, 0.0),
    Vec3(0.1875, 1.5717773437500002, 0.0),
    Vec3(0.28125, 2.1450805664062504, 0.0),
    Vec3(0.375, 2.5898437500000004, 0.0),
    Vec3(0.46874999999999994, 2.9159545898437504, 0.0),
    Vec3(0.5625, 3.1333007812500004, 0.0),
    Vec3(0.6562499999999999, 3.251770019531251, 0.0),
    Vec3(0.7031249999999999, 3.277015686035157, 0.0),
    Vec3(0.7499999999999999, 3.281250000000001, 0.0),
    Vec3(0.8437499999999999, 3.231628417968751, 0.0),
    Vec3(0.9374999999999999, 3.1127929687500013, 0.0),
    Vec3(1.0312499999999998, 2.9346313476562513, 0.0),
    Vec3(1.1249999999999998, 2.7070312500000013, 0.0),
    Vec3(1.3124999999999998, 2.1430664062500013, 0.0),
    Vec3(1.4999999999999998, 1.5000000000000018, 0.0),
    Vec3(1.6874999999999998, 0.8569335937500013, 0.0),
    Vec3(1.8749999999999996, 0.29296875000000133, 0.0),
    Vec3(1.9687499999999996, 0.06536865234375133, 0.0),
    Vec3(2.0624999999999996, -0.11279296874999867, 0.0),
    Vec3(2.1562499999999996, -0.2316284179687489, 0.0),
    Vec3(2.2499999999999996, -0.2812499999999989, 0.0),
    Vec3(2.296875, -0.27701568603515514, 0.0),
    Vec3(2.34375, -0.2517700195312489, 0.0),
    Vec3(2.4375, -0.13330078124999956, 0.0),
    Vec3(2.53125, 0.08404541015625044, 0.0),
    Vec3(2.625, 0.41015625000000044, 0.0),
    Vec3(2.71875, 0.8549194335937504, 0.0),
    Vec3(2.8125, 1.4282226562500002, 0.0),
    Vec3(3.0, 3.0, 0.0),
]


def test_flattening():
    fitpoints = [(0, 0), (1, 3), (2, 0), (3, 3)]
    bspline = BSpline.from_fit_points(fitpoints)
    assert list(bspline.flattening(0.01, segments=4)) == EXPECTED_FLATTENING


POINTS_ORDER_4 = [
    Vec3(0.0, 0.0, 0.0),
    Vec3(2.9975, 5.277500000000001, 5.49125),
    Vec3(5.980000000000002, 9.220000000000002, 10.030000000000005),
    Vec3(8.932499999999997, 11.9925, 13.713749999999997),
    Vec3(11.840000000000003, 13.760000000000002, 16.64),
    Vec3(14.6875, 14.6875, 18.90625),
    Vec3(17.459999999999997, 14.939999999999998, 20.61),
    Vec3(20.1425, 14.682500000000001, 21.84875),
    Vec3(22.72, 14.079999999999998, 22.719999999999995),
    Vec3(25.177500000000002, 13.297500000000003, 23.321250000000006),
    Vec3(27.5, 12.5, 23.75),
    Vec3(29.682500000000005, 11.8125, 24.09375),
    Vec3(31.759999999999994, 11.2, 24.399999999999995),
    Vec3(33.7775, 10.587499999999999, 24.70625),
    Vec3(35.779999999999994, 9.9, 25.05),
    Vec3(37.8125, 9.0625, 25.46875),
    Vec3(39.92, 7.999999999999999, 26.0),
    Vec3(42.147499999999994, 6.637500000000001, 26.68125),
    Vec3(44.540000000000006, 4.8999999999999995, 27.550000000000004),
    Vec3(47.1425, 2.712500000000002, 28.643749999999997),
    Vec3(50.0, 0.0, 30.0),
]

DERIVATIVES_ORDER_4 = [
    [Vec3(0.0, 0.0, 0.0), Vec3(60.0, 120.0, 120.0), Vec3(0.0, -600.0, -420.0)],
    [
        Vec3(2.9975, 5.277500000000001, 5.49125),
        Vec3(59.85, 91.65, 99.975),
        Vec3(-5.9999999999999964, -534.0000000000001, -381.0000000000001),
    ],
    [
        Vec3(5.980000000000002, 9.220000000000002, 10.030000000000005),
        Vec3(59.400000000000006, 66.6, 81.9),
        Vec3(-11.999999999999964, -468.0, -342.0),
    ],
    [
        Vec3(8.932499999999997, 11.9925, 13.713749999999997),
        Vec3(58.64999999999999, 44.849999999999994, 65.77499999999999),
        Vec3(-18.0, -402.0, -303.0),
    ],
    [
        Vec3(11.840000000000003, 13.760000000000002, 16.64),
        Vec3(57.6, 26.4, 51.6),
        Vec3(-24.0, -336.0, -264.0),
    ],
    [
        Vec3(14.6875, 14.6875, 18.90625),
        Vec3(56.25, 11.25, 39.375),
        Vec3(-30.0, -270.0, -225.0),
    ],
    [
        Vec3(17.459999999999997, 14.939999999999998, 20.61),
        Vec3(54.599999999999994, -0.5999999999999943, 29.1),
        Vec3(-36.0, -204.0, -186.0),
    ],
    [
        Vec3(20.1425, 14.682500000000001, 21.84875),
        Vec3(52.65, -9.150000000000002, 20.775000000000002),
        Vec3(-42.00000000000003, -138.0, -147.0),
    ],
    [
        Vec3(22.72, 14.079999999999998, 22.719999999999995),
        Vec3(50.39999999999999, -14.399999999999999, 14.399999999999999),
        Vec3(-47.99999999999997, -71.99999999999997, -107.99999999999999),
    ],
    [
        Vec3(25.177500000000002, 13.297500000000003, 23.321250000000006),
        Vec3(47.85, -16.35, 9.975000000000001),
        Vec3(-54.00000000000006, -5.999999999999993, -69.0),
    ],
    [Vec3(27.5, 12.5, 23.75), Vec3(45.0, -15.0, 7.5), Vec3(-60.0, 60.0, -30.0)],
    [
        Vec3(29.682500000000005, 11.8125, 24.09375),
        Vec3(42.45000000000001, -12.75, 6.374999999999999),
        Vec3(-41.99999999999997, 29.99999999999998, -14.999999999999972),
    ],
    [
        Vec3(31.759999999999994, 11.2, 24.399999999999995),
        Vec3(40.79999999999999, -12.0, 6.000000000000001),
        Vec3(-24.0, 1.7763568394002505e-14, 0.0),
    ],
    [
        Vec3(33.7775, 10.587499999999999, 24.70625),
        Vec3(40.050000000000004, -12.749999999999996, 6.375),
        Vec3(-5.999999999999943, -30.000000000000014, 15.000000000000028),
    ],
    [
        Vec3(35.779999999999994, 9.9, 25.05),
        Vec3(40.2, -14.999999999999998, 7.499999999999993),
        Vec3(11.999999999999943, -59.99999999999998, 29.999999999999943),
    ],
    [
        Vec3(37.8125, 9.0625, 25.46875),
        Vec3(41.25, -18.75, 9.375),
        Vec3(30.0, -90.0, 45.0),
    ],
    [
        Vec3(39.92, 7.999999999999999, 26.0),
        Vec3(43.2, -24.000000000000004, 11.999999999999993),
        Vec3(48.000000000000114, -120.00000000000003, 60.00000000000006),
    ],
    [
        Vec3(42.147499999999994, 6.637500000000001, 26.68125),
        Vec3(46.04999999999998, -30.75, 15.374999999999986),
        Vec3(65.99999999999989, -150.0, 74.99999999999989),
    ],
    [
        Vec3(44.540000000000006, 4.8999999999999995, 27.550000000000004),
        Vec3(49.80000000000001, -39.0, 19.5),
        Vec3(84.00000000000011, -180.0, 90.00000000000011),
    ],
    [
        Vec3(47.1425, 2.712500000000002, 28.643749999999997),
        Vec3(54.44999999999999, -48.74999999999999, 24.375),
        Vec3(102.00000000000023, -209.99999999999994, 104.99999999999989),
    ],
    [
        Vec3(50.0, 0.0, 30.0),
        Vec3(60.0, -60.0, 30.0),
        Vec3(120.0, -240.0, 120.0),
    ],
]

POINTS_ORDER_3 = [
    Vec3(0.0, 0.0, 0.0),
    Vec3(3.0000000000000004, 5.437500000000001, 5.606250000000001),
    Vec3(6.000000000000001, 9.75, 10.425),
    Vec3(9.0, 12.937499999999998, 14.456249999999999),
    Vec3(12.000000000000002, 15.000000000000002, 17.700000000000003),
    Vec3(15.0, 15.937499999999998, 20.15625),
    Vec3(18.0, 15.75, 21.825),
    Vec3(20.9875, 14.5125, 22.74375),
    Vec3(23.8, 13.199999999999998, 23.4),
    Vec3(26.387500000000003, 12.1125, 23.943749999999998),
    Vec3(28.749999999999996, 11.249999999999998, 24.374999999999996),
    Vec3(30.8875, 10.612499999999997, 24.693749999999994),
    Vec3(32.8, 10.2, 24.899999999999995),
    Vec3(34.4875, 10.0125, 24.99375),
    Vec3(36.05, 9.9, 25.05),
    Vec3(37.8125, 9.375, 25.3125),
    Vec3(39.800000000000004, 8.399999999999999, 25.799999999999997),
    Vec3(42.0125, 6.975, 26.5125),
    Vec3(44.45, 5.099999999999999, 27.450000000000003),
    Vec3(47.112500000000004, 2.7750000000000026, 28.612499999999997),
    Vec3(50.0, 0.0, 30.0),
]

POINTS_ORDER_2 = [
    Vec3(0.0, 0.0, 0.0),
    Vec3(2.0, 4.0, 4.0),
    Vec3(4.0, 8.0, 8.0),
    Vec3(6.0, 12.0, 12.0),
    Vec3(8.0, 16.0, 16.0),
    Vec3(10.0, 20.0, 20.0),
    Vec3(13.999999999999998, 18.0, 21.0),
    Vec3(17.999999999999996, 16.0, 22.0),
    Vec3(22.000000000000004, 14.0, 23.0),
    Vec3(26.0, 12.0, 24.0),
    Vec3(30.0, 10.0, 25.0),
    Vec3(32.0, 10.0, 25.0),
    Vec3(34.0, 10.0, 25.0),
    Vec3(36.0, 10.0, 25.0),
    Vec3(38.0, 10.0, 25.0),
    Vec3(40.0, 10.0, 25.0),
    Vec3(42.0, 7.999999999999998, 26.0),
    Vec3(44.0, 6.000000000000001, 27.0),
    Vec3(46.0, 3.999999999999999, 28.0),
    Vec3(48.0, 2.0000000000000018, 28.999999999999996),
    Vec3(50.0, 0.0, 30.0),
]


class TestNurbsPythonCorrectness:
    # Test if package "geomdl" (a.k.a. NURBS Python) is still correct.
    @pytest.mark.parametrize(
        "order,results",
        [
            [2, POINTS_ORDER_2],
            [3, POINTS_ORDER_3],
            [4, POINTS_ORDER_4],
        ],
        ids=["degree=1", "degree=2", "degree=3"],
    )
    def test_point_calculation_is_correct(self, order, results):
        curve = BSpline(DEFPOINTS, order=order).to_nurbs_python_curve()
        points = curve.evaluate_list(PARAMS)
        for expect, point in zip(results, points):
            assert expect.isclose(point)

    def test_derivative_calculation_is_correct(self):
        spline = BSpline(DEFPOINTS, order=4).to_nurbs_python_curve()
        for t, expected in zip(PARAMS, DERIVATIVES_ORDER_4):
            results = spline.derivatives(t, order=2)
            for e, p in zip(expected, results):
                assert e.isclose(p)


@pytest.mark.parametrize(
    "order,results",
    [
        [2, POINTS_ORDER_2],
        [3, POINTS_ORDER_3],
        [4, POINTS_ORDER_4],
    ],
    ids=["degree=1", "degree=2", "degree=3"],
)
def test_bspline_point_calculation_to_pre_calculated_results(order, results):
    spline = BSpline(DEFPOINTS, order=order)
    for p, expected in zip(spline.points(PARAMS), results):
        assert p.isclose(expected)


def test_bspline_derivative_calculation_to_pre_calculated_results():
    spline = BSpline(DEFPOINTS, order=4)
    for points, expected in zip(
        spline.derivatives(PARAMS, n=2), DERIVATIVES_ORDER_4
    ):
        for p, e in zip(points, expected):
            assert p.isclose(e)


def test_bspline_point_calculation_against_derivative_calculation():
    # point calculation and derivative calculation are not the same functions
    # for optimization reasons. The derivatives() function returns the curve
    # point and n derivatives, check if both functions return the
    # same curve point:
    spline = BSpline(DEFPOINTS, order=4)
    curve_points = [p[0] for p in spline.derivatives(PARAMS, n=1)]
    for p, expected in zip(curve_points, spline.points(PARAMS)):
        assert p.isclose(expected)
