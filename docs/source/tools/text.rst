.. _Text Tools:

Text Tools
==========

.. module:: ezdxf.tools.text

MTextEditor
-----------

.. autoclass:: MTextEditor

    .. attribute:: text

        The MTEXT content as a simple string.

    .. automethod:: append

    .. automethod:: __iadd__

    .. automethod:: __str__

    .. automethod:: clear

    .. automethod:: font

    .. automethod:: height

    .. automethod:: scale_height

    .. automethod:: width_factor

    .. automethod:: char_tracking_factor

    .. automethod:: oblique

    .. automethod:: color

    .. automethod:: aci

    .. automethod:: rgb

    .. automethod:: underline

    .. automethod:: overline

    .. automethod:: strike_through

    .. automethod:: group

    .. automethod:: stack

    .. automethod:: paragraph

    .. automethod:: bullet_list

Constants stored in the :class:`MTextEditor` class:

=================== ==========
NEW_LINE            ``'\P'``
NEW_PARAGRAPH       ``'\P'``
NEW_COLUMN          ``'\N``
UNDERLINE_START     ``'\L'``
UNDERLINE_STOP      ``'\l'``
OVERSTRIKE_START    ``'\O'``
OVERSTRIKE_STOP     ``'\o'``
STRIKE_START        ``'\K'``
STRIKE_STOP         ``'\k'``
ALIGN_BOTTOM        ``'\A0;'``
ALIGN_MIDDLE        ``'\A1;'``
ALIGN_TOP           ``'\A2;'``
NBSP                ``'\~'``
TAB                 ``'^I'``
=================== ==========

.. autoclass:: ParagraphProperties(indent=0, left=0, right=0, align=DEFAULT, tab_stops=[])

    .. automethod:: tostring


.. class:: ezdxf.lldxf.const.MTextParagraphAlignment

    .. attribute:: DEFAULT

    .. attribute:: LEFT

    .. attribute:: RIGHT

    .. attribute:: CENTER

    .. attribute:: JUSTIFIED

    .. attribute:: DISTRIBUTED


Single Line Text
----------------

.. autoclass:: TextLine

    .. autoproperty:: width

    .. autoproperty:: height

    .. automethod:: stretch

    .. automethod:: font_measurements

    .. automethod:: baseline_vertices

    .. automethod:: corner_vertices

    .. automethod:: transform_2d

Functions
---------

.. autofunction:: caret_decode

.. autofunction:: estimate_mtext_content_extents

.. autofunction:: estimate_mtext_extents

.. autofunction:: fast_plain_mtext

.. autofunction:: is_text_vertical_stacked

.. autofunction:: is_upside_down_text_angle

.. autofunction:: leading

.. autofunction:: plain_mtext

.. autofunction:: plain_text

.. autofunction:: safe_string

.. autofunction:: text_wrap

.. autofunction:: upright_text_angle
