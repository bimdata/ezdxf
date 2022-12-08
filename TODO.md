TODO
====
 
Add-ons
-------

- drawing add-on improvements:
  - (>v1.0) render SHX fonts and SHAPE entities as paths by the frontend 
    from `.shx` or `.shp` files
  
  - (>v1.0) proper rendering pipeline: Frontend -> Stage0 -> ... -> Backend 
    Introducing the Designer() class was the first step, but the implementation 
    is not as flexible as required. Possible rendering stages:
    - linetype rendering
    - 3D text rendering as path-patches
    - optional stage to render ALL text as path-patches, this could be used for 
      backends without good text support like the Pillow backend.
    - ortho-view projection (TOP, LEFT, FRONT, ...)
    
    The pipeline should be passed to the Frontend() class as component or 
    set on the fly. The composition of the pipeline from various stages is a 
    very important feature.
  
    REMINDER FOR MYSELF: Decoupling of the rendering stages and the pipeline 
    is very important, the first proof of concept was too tightly 
    coupled (viewport rendering)!!!!

  - (>v1.0) Native SVG exporter, planned after the matplotlib backend supports 
    all v1.0 features. 

  - (>v1.0) Native PDF exporter? Problem: The PDF 1.7 reference has ~1300 pages, 
    but I assume I only need a fraction of that information for a simple exporter. 
    I can use Matplotlib for text rendering as Bèzier curves if required.  
  
    Existing Python packages for PDF rendering: 
    - pycairo: binary wheels for Windows on PyPI - could handle SVG & PDF, but I 
      don't know how much control I get from cairo. The advantage of a native 
      exporter would be to get full control over all available features of the 
      output format, by the disadvantage of doing ALL the work by myself.
    - pypoppler: only source code distribution from 2013 on PyPI
    - python-poppler-qt5: only source code distribution on PyPI
    - Reportlab: more report or magazine page layout oriented
    - PyQt: QPrinter & QPainter - https://wiki.qt.io/Handling_PDF
  
    In consideration, if the SVG exporter works well.
  
  - (>1.0) Support for `Layout.dxf.plot_layout_options` in export mode of 
    class `RenderContext`:
    - plot with plot-styles; disable loading of the ctb-table in set_currrent_layout()
    - plot entity lineweights; if disabled which linewidth should be used instead?
    - scale lineweights; scale by what?
    - plot transparencies
    - hide paperspace entities (`DXFGraphic.dxf.paperspace` attribute is `True`)
    
    VIEWPORT borders are not plotted at all by the `drawing` add-on
    
- (>v1.0) DWG loader, planned for the future. Cython will be required for the 
  low level stuff, no pure Python implementation.
- (>v1.0) text2path: add support for SHX fonts

Render Tools
------------

- (>v1.0) ACAD_TABLE tool to render content as DXF primitives to create the 
  content of the anonymous block `*T...`
- (>v1.0) factory methods to create ACAD_TABLE entities
- (>v1.0) fix LWPOLYLINE parsing error in ProxyGraphic, see test script 239
- (>v1.0) tool to create proxy graphic 
- (>v1.0) add `ShxFont` and `ShpFont` classes to `ezdxf.tools.fonts`

DXF Entities
------------

- (>v1.0) ACAD_TABLE entity load and export support beyond `AcadTableBlockContent`
- (>v1.0) ACAD_TABLE tool to manage content at table and cell basis
- (>v1.0) GEODATA version 1 support, see mpolygon examples and DXF reference R2009
- (>v1.0) FIELD, used by ACAD_TABLE and MTEXT
- (>v1.0) explode HATCH pattern into LINE entities, points are represented by 
  zero-length LINE entities, because the POINT entity has a special meaning.
- (>v1.0) HATCH: shift hatch pattern origin, see discussion #769 
  and examples/entities/hatch_pattern_modify_origin.py
- (>v1.0) extend ACIS support
- (>v1.0) clipping path support for block references, see XCLIP command and 
  discussion #760

Selection Module
----------------

(>1.0) A module to select entities based on their spatial location and shape 
like in CAD applications, but using the bounding box of the entities instead 
their real geometry for simplicity.

Selection methods:
- rectangle selection - entity bbox inside a rectangular window
- rectangle crossing - entity bbox inside or crossing a rectangular window
- circle selection - entity bbox inside a circular window
- circle crossing - entity bbox inside or crossing a circular window
- polygon selection - entity bbox inside a polygonal window
- polygon crossing - entity bbox inside or crossing a polygonal window
- fence selection - entity bboxes crossing an arbitrary polyline
- cluster selection - entity bboxes located near together (k_means, dbscan)
- chain selection - linked bboxes starting at a given point or entity (RTree)

The selection geometry should be an object:
- Rectangle
- Circle
- Polygon
- Fence

The selection result should be an `EntityQuery` container, which already has 
`Set` operations to combine multiple selections:
- union of selections
- subtract selected entities from a previous selection
- intersection of selection

The selection methods should support a bounding box cache as an optional 
parameter to improve the performance for multiple selections for the 
same base entities.

Usage should look like this:

```python
from ezdxf import select
from ezdxf import bbox

...

entities = doc.modelspace()

# optional bounding box cache for faster processing of multiple queries:
bbox_cache = bbox.Cache()

rect = select.Rectangle(x0=0, y0=0, x1=10, y1=10)
circle = select.Circle(x=30, y=30, radius=10)

# union:
selection0 = select.inside(entities, rect, cache=bbox_cache)
selection1 = select.crossing(entities, circle, cache=bbox_cache)
result = selection0 | selection1

# subtraction:
selection = select.inside(entities, rect, cache=bbox_cache)
ignore = select.crossing(selection, circle, cache=bbox_cache)
result = selection - ignore
```

Extended entity geometry for selection:
Ezdxf uses the `disassemble` module for the bounding box calculation, which 
deconstructs DXF entities into path and/or mesh primitives. This data
could be used to select entities not only by their bounding box, but also
by their vertices for mesh primitives and by their control points or flattened 
vertices for path entities. 

EntityGeometry enum:
- BBOX
- CONTROL_POINTS
- VERTICES

This feature would require a different caching strategy, because the bounding 
box cache does not contain the disassembled primitives and reusing an existing 
bounding box cache is not possible.

Issues:
- How to handle 2D/3D selections?
- 2D selections always in top-view mode?
- Using special box- and sphere selections for 3D selection?

Xref Module
-----------

(>v1.0) A core module `ezdxf.xref` as replacement for the `Importer` add-on.
This module adds management features for external references, but also improve
import and exchange of data and ressources with DXF documents.

- AutoCAD does not support DXF files as XREF objects!
- ezdxf will only support DXF files as XREF objects, use the `odafc` add-on to 
  convert DWG to DXF
- has to be much more versatile than the current `Importer` add-on otherwise 
  just improve and extend the `Importer` add-on 

Features:
- resource management like CAD applications, e.g. layer names of xrefs: 
  <dwg-name>$0$layername
- `xref.bind(xref_block)`: convert a XREF into a common BLOCK, this replaces 
  the modelspace import of the `Importer` add-on
- `xref.attach(doc, "xref_filename.dxf")`, replaces `Drawing.add_xref_def()`
- manage resources by the `XRefManager` class

XRefManager:
- create: `xmgr = xref.XRefManager(source_doc, target_doc)`
- `xmgr.import_modelspace()` import all modelspace entities
- `xmgr.import_entities(entities)` import selected entities
- modify entities on import (transform, change DXF properties)
- `xmgr.import_block("block_name")`
- `xmgr.import_resources(resource_desc)`
- `xmgr.import_paperspace("layout_name")`???
- `xmgr.finalize()`

Convert Document to DXF R12
---------------------------

(>v1.0) A module to convert a whole DXF document into DXF R12 inplace, this is 
a destructive process and converts or explodes DXF entities:
- explode MTEXT, MULTILEADER, MLINE, ACAD_TABLE, ARC_DIMENSION
- convert MESH to PolyFaceMesh
- convert LWPOLYLINE into 2D polyline
- flatten SPLINE into a 3D polyline
- flatten ELLIPSE into a 3D polyline
- ACIS based entities with only flat faces could be converted to PolyFaceMesh 
- render HATCH and MPOLYGON entities with pattern filling into a BLOCK as LINE 
  entities

Removes all data not supported by DXF R12:
- all ACIS based entities which contain curved faces 
- HATCH and MPOLYGON entities with solid or gradient filling. The mapbox-earcut 
  algorithm for polygon triangulation does not support nested holes. 
- IMAGE and UNDERLAY entities
- XLINE and RAY entities
- OBJECTS and the CLASSES sections
- all but the first paper space layout

DXF Document
------------

- (>v1.0) copy DXF document by serializing and reloading the document in memory 
  or by file-system, this is not efficient but safe.

Increase Minimal Required Python Version
----------------------------------------

(v1.1) Python 3.8 - maybe jumping straight to Python 3.9

- https://docs.python.org/3/whatsnew/3.8.html
- import `Protocol` from `typing` instead from `typing_extensions`
- `typing.Literal`
- walrus operator `:=`

Python 3.9 in late 2023, after release of Python 3.12

- https://docs.python.org/3/whatsnew/3.9.html
- type hinting generics in standard collections: 
  `dict[tuple[int, str], list[str]]` can be used in regular code outside of annotations,
  import of `List`, `Dict` or `Tuple` is not required anymore

Python 3.10 in late 2024, after release of Python 3.13

- https://docs.python.org/3/whatsnew/3.10.html
- structural pattern matching?
- typing: union operator `|`, outside of annotations (type aliases)
- dataclasses: `__slots__`
- `itertools.pairwise()` replaces `ezdxf.tools.take2()`

Python 3.11 in late 2025, after release of Python 3.14

- https://docs.python.org/3/whatsnew/3.11.html
- exception groups?
- `typing.Self`


Apply minimal Python version update to:

- README.md
- setup.py
- toplevel index.rst
- introduction.rst
- setup.rst
