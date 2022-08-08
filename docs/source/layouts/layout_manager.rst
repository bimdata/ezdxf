.. _layout_manager:

Layout Manager
==============

.. module:: ezdxf.layouts
    :noindex:

The layout manager is unique to each DXF drawing, access the layout manager as
:attr:`~ezdxf.document.Drawing.layouts` attribute of the
:class:`~ezdxf.document.Drawing` object
(e.g. ``doc.layouts.rename("Layout1", "PlanView")``).

.. class:: Layouts

    The :class:`Layouts` class manages :class:`~ezdxf.layouts.Paperspace` layouts and
    the :class:`~ezdxf.layouts.Modelspace`.

    .. automethod:: __len__

    .. automethod:: __contains__

    .. automethod:: __iter__() -> Iterable[Layout]

    .. automethod:: names

    .. automethod:: names_in_taborder

    .. automethod:: modelspace() -> Modelspace

    .. automethod:: get(name: str) -> Layout

    .. automethod:: new(name: str, dxfattribs: dict = None) -> Paperspace

    .. automethod:: rename

    .. automethod:: delete

    .. automethod:: active_layout() -> Paperspace

    .. automethod:: set_active_layout

    .. automethod:: get_layout_for_entity(entity: DXFEntity) -> Layout
