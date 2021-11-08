.. _tut_angular_dimension:

Tutorial for Angular Dimensions (work in progress)
==================================================

Please read the :ref:`tut_linear_dimension` before, if you haven't.

.. note::

    `Ezdxf` does not consider all DIMSTYLE variables, so the
    rendering results are different from CAD applications.

Dimension Style "EZ_CURVED"
---------------------------

All factory methods to create angular dimensions uses the dimension style
"EZ_CURVED" for curved dimension lines which is defined as:

- angle unit is decimal degrees
- measurement text height = 0.25 (drawing scale = 1:100)
- measurement text location is above the dimension line
- closed filled arrow and arrow size :attr:`dimasz` = 0.25

This DIMENSION style only exist if the argument `setup` is ``True`` for creating
a new DXF document by :meth:`ezdxf.new`.
Every dimension style which does not exist will be replaced by the dimension
style "Standard" at DXF export by :meth:`save` or :meth:`saveas`
(e.g. dimension style setup was not initiated).

Add all `ezdxf` specific resources (line types, text- and dimension styles)
to an existing DXF document:

.. code-block:: Python

    import ezdxf
    from ezdxf.tools.standards import setup_drawing

    doc = ezdxf.readfile("your.dxf")
    setup_drawing(doc, topics="all")

Factory Methods to Create Angular Dimensions
--------------------------------------------

Defined by Center, Radius and Angles
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The first example shows an angular dimension defined by the center point, radius,
start- and end angles:

.. code-block:: Python

    import ezdxf

    # Create a DXF R2010 document:
    # Use argument setup=True to setup the default dimension styles.
    doc = ezdxf.new("R2010", setup=True)

    # Add new entities to the modelspace:
    msp = doc.modelspace()

    # Add an angular DIMENSION defined by the center point, start- and end angles,
    # the measurement text is placed at the default location above the dimension
    # line:
    dim = msp.add_angular_dim_cra(
        center=(5, 5),  # center point of the angle
        radius= 7,  # distance from center point to the start of the extension lines
        start_angle=30,  # start angle in degrees
        end_angle=150,  # end angle in degrees
        distance=3,  # distance from start of the extension lines to the dimension line
        dimstyle="EZ_CURVED",  # default angular dimension style
    )

    # Necessary second step to create the BLOCK entity with the dimension geometry.
    # Additional processing of the DIMENSION entity could happen between adding
    # the entity and the rendering call.
    dim.render()
    doc.saveas("angular_dimension_cra.dxf")

Angle by 2 Lines
~~~~~~~~~~~~~~~~

The next example shows an angular dimension for an angle defined by two lines:

.. code-block:: Python

    import ezdxf

    doc = ezdxf.new("R2010", setup=True)
    msp = doc.modelspace()

    # Setup the geometric parameters for the DIMENSION entity:
    base = (5.8833, -6.3408)  # location of the dimension line
    p1 = (2.0101, -7.5156)  # start point of 1st leg
    p2 = (2.7865, -10.4133)  # end point of 1st leg
    p3 = (6.7054, -7.5156)  # start point of 2nd leg
    p4 = (5.9289, -10.4133)  # end point of 2nd leg

    # Draw the lines for visualization, not required to create the
    # DIMENSION entity:
    msp.add_line(p1, p2)
    msp.add_line(p3, p4)

    # Add an angular DIMENSION defined by two lines, the measurement text is
    # placed at the default location above the dimension line:
    dim = msp.add_angular_dim_2l(
        base=base,  # defines the location of the dimension line
        line1=(p1, p2),  # start leg of the angle
        line2=(p3, p4),  # end leg of the angle
        dimstyle="EZ_CURVED",  # default angular dimension style
    )

    # Necessary second step to create the dimension line geometry:
    dim.render()
    doc.saveas("angular_dimension_2l.dxf")

The example above creates an angular :class:`~ezdxf.entities.Dimension` entity
to measures the angle between two lines (`line1` and `line2`).

The `base` point defines the location of the dimension line (arc), any point on
the dimension line is valid. The points `p1` and `p2` define the first leg of
the angle, `p1` also defines the start point of the first extension line.
The points `p3` and `p4` define the second leg of the angle and point `p3` also
defines the start point of the second extension line.

The measurement of the DIMENSION entity is the angle enclosed by the first and
the second leg and where the dimension line passes the `base` point.

The return value `dim` is **not** a dimension entity, instead a
:class:`~ezdxf.entities.DimStyleOverride` object is
returned, the dimension entity is stored as :attr:`dim.dimension`.

Angler by 3 Points
~~~~~~~~~~~~~~~~~~

TODO ...

Placing Measurement Text
------------------------

Default Text Location
~~~~~~~~~~~~~~~~~~~~~

The DIMSTYLE "EZ_CURVED" places the measurement text in the center of the angle
above the dimension line. The first examples above show the measurement text at
the default text location.

The text direction angle is always perpendicular to the line from the text center
to the center point of the angle unless this angle is manually overridden.

.. note::

    Not all possibles features of DIMSTYLE are supported by the `ezdxf` rendering
    procedure and especially for the angular dimension there are less features
    implemented than for the linear dimension because of the lack of good
    documentation.

.. seealso::

    - Graphical reference of many DIMVARS and some advanced information:
      :ref:`dimstyle_table_internals`
    - Source code file `standards.py`_ shows how to create your own DIMSTYLES.
    - The Script `dimension_angular.py`_ shows examples for angular dimensions.

User Defined Text Locations
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Beside the default location it is always possible to override the text location
by a user defined location. This location also determines the angle of the
measurement text.

.. code-block:: python

    dim = msp.add_angular_dim_3p(
        base=(0, 4),  # location of the dimension line
        center=(0, 0),  # center point of angle
        p1=(-3, 3),  # defines the start angle and the start point of the first extension line
        p2=(3, 3),  # defines the end angle and the start point of the second extension line
        location=(1, 5),  # user defined measurement text location
    )

.. image:: gfx/dim_angular_user.png

Overriding Measurement Text
---------------------------

See Linear Dimension Tutorial: :ref:`tut_overriding_measurement_text`

Measurement Text Formatting and Styling
---------------------------------------

See Linear Dimension Tutorial: :ref:`tut_measurement_text_formatting_and_styling`


.. _dimension_angular.py:  https://github.com/mozman/ezdxf/blob/master/examples/render/dimension_angular.py
.. _standards.py: https://github.com/mozman/ezdxf/blob/master/src/ezdxf/tools/standards.py