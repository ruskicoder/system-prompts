---
name: architecture-diagrams
description: Rules and workflow for drawing legible architecture, deployment, context
  and integration diagrams by hand placement in draw.io, for an agent that lays out
  a figure from code. Covers what goes in one figure, reading direction, tiers, nesting
  depth, fixed orthogonal routing, request and response pairs, label placement, print-size
  font arithmetic, colour and icons, and a geometry lint plus a crop-by-crop visual
  check before anyone sees the figure. Use when drawing, redrawing, fixing or reviewing
  a system architecture, deployment, context or integration diagram, any boxes-and-arrows
  figure bound for a report or slide, or a question about how such a figure should
  be laid out.
argument-hint: '[figure, .drawio file or question]'
---

<!-- Generated from skills/architecture-diagrams.md by tools/generate_integrations.py. Edit the source file, not this one. -->

# Skill: Architecture Diagrams

A figure is done when a reader who has never seen the system can read every label at print size and
follow every arrow to its end without guessing. Work in this order: decide the content, then the
grid, then the routes, then check the geometry with the lint and the render by eye. A project's own
diagram conventions take precedence; raise any strain with their owner. Run every figure through
the `diagram-check-loop` workflow before showing it.

## 1. Content before layout

1. One figure answers one question at one level of detail. An overview shows deliverables (apps,
   services, stores, devices, third parties) and how they talk; a module or class breakdown belongs
   in its own figure. Keep the two levels apart.
2. Inventory the content from the code, not from an older figure or a charter: every block opens to
   a real path, every protocol is the one the code uses, every third party is one the code calls.
   Write the inventory (block, path, protocol) before drawing.
3. Name things once, the same way in every figure and in the text. A rename changes every figure
   that shows the thing.
4. Budget about 15 to 25 nodes for a page, and stay under about 40 cells. Past that, split the
   figure or bundle edges (rule 30); do not shrink the text.
5. Every external system that the figure's system calls, or that calls it, is drawn and connected,
   including calls made from the frontend (map tiles loaded in the browser connect to the web app).
6. A component sits inside what contains it at runtime: an ORM inside the backend, a queue inside
   the process that owns it. Never draw a part outside its host to save room.

## 2. Reading direction and tiers

7. Pick one reading direction, normally left to right: sources and actors on the left, stores and
   third parties on the right. Every main flow moves in that direction.
8. When two flows exist (people and machines, control and data), give each a horizontal tier and let
   them meet in as few places as possible, ideally one.
9. Put all third parties in one column or one row at the side where the flows end, in the order the
   flows reach them, so no line travels across the figure to find one.
10. Align on shared centre lines: boxes in a row share a centre y, boxes in a column share a centre x.
    Snap every coordinate to a 10 px grid.
11. Leave more space between groups than inside them, so grouping reads before any border does:
    40 to 60 px inside a row, 80 to 120 px between tiers, wider where edges run between.

## 3. Grouping and nesting

12. Groups are boundaries that mean something: a runtime host, a network, a trust zone, an owner. A
    group that only decorates is removed.
13. At most two levels of nesting under the figure's outer boundary. A third level (system, cloud,
    container, application, module) is where legibility goes; flatten it by naming the host in the
    box title.
14. A group is a parent cell (`container=1`), never a box laid on top of others, and its children
    keep at least 30 px from its border so lines and titles have a gutter.
15. Group titles sit top left, on the group's own fill, and nothing crosses them.
16. Use a vendor's group style only for what it means: an AWS Cloud group only around what runs on
    AWS. A generic or planned environment gets a plain group with a plain title.

## 4. Edges and routing

17. Draw every edge as a fixed polyline: `edgeStyle=none`, pinned `exitX`/`exitY` and
    `entryX`/`entryY`, and every bend as an explicit waypoint. Never leave routing to the editor's
    orthogonal router, and never add waypoints to a router edge: the router re-routes between them.
18. Horizontal and vertical segments only; a diagonal only where a right angle is impossible.
19. Zero edge crossings is the target. A crossing costs more readability than a bend or a longer
    route. A jump arc is a last resort and is named in the review.
20. At most two bends per edge in an overview, four anywhere. Each bend is a turn the reader has to
    follow.
21. No edge passes through a box, a label, a group title, or along a border. An edge crosses a group
    border only to enter or leave the group that holds one of its ends, and only once.
22. Two-way traffic is two one-way arrows, request solid and response dashed, in the same colour, 8 to
    12 px apart and parallel along their whole run. A double-headed arrow hides which side starts the
    exchange.
23. Each edge gets its own attachment point on a box side; the edges of one pair attach symmetric
    about the side's centre. Never stack two arrowheads on one point.
24. Keep at least 20 px of straight run before every arrowhead and after every start.
25. Parallel edges keep one spacing for the whole figure; a channel between two groups holds its lines
    at that spacing, sorted so none crosses another on the way in or out.

## 5. Labels and text

26. Every arrow is labelled with what travels on it (a noun, plus the protocol between deliverables,
    for example "telemetry, MQTT/TLS"), never a bare "uses" or "calls".
27. Labels are their own text cells, placed beside their segment on the side away from its partner
    (request label above, response label below), with clear space all round. A label is never on a
    line, never touching another label, and never further from its line than from any other line.
28. Names stay at two lines at most and never break mid-word. Full names first; one short form per
    thing.
29. Print size decides font size. Compute it: printed width in pt divided by canvas width in px is the
    scale (1 cm is 28.35 pt). Body text prints at 8 pt or more and never below 7 pt. For a 24 cm wide
    figure (A4 landscape body, 680 pt) a 1200 px canvas prints 1 px at 0.57 pt, so 14 px text prints
    at 7.9 pt and 15 px at 8.5 pt. Choose the canvas width from the page, not the page from the
    canvas.
30. When repeated edges would crowd a figure, bundle them into one arrow to a group and state the
    bundling convention in the text that cites the figure.

## 6. Colour, icons and images

31. Colour carries one meaning per figure and the same meaning across figures (for example one hue per
    flow kind). Every colour is paired with a second cue, line style or label, so the figure survives
    grey print.
32. Pastel fills for groups, saturated strokes for flows, black or near-black text. Text contrast
    against its fill is at least 4.5:1.
33. Vendor icons are used unmodified (no crop, stretch or recolour) and only for that vendor's
    product. A generic block (a container, a server, a browser) gets a generic icon.
34. A product render or photo is used for hardware the project builds, at a size where its caption
    stays the dominant label.
35. No legend when the text explains the notation; where the project requires one, it lists only the
    line styles and colours actually used.

## 7. Workflow

1. **Inventory**: list blocks, paths, protocols and third parties from the code (section 1). Settle
   the level of detail with the owner when unsure.
2. **Sketch**: a text sketch of tiers, columns and flows; get the owner's yes before writing XML.
3. **Generator**: write the figure as a small script that emits draw.io XML from coordinates on a
   10 px grid: groups as parent cells, edges as fixed polylines, labels as text cells. Keep the script
   beside the `.drawio` file; every change goes through it.
4. **Lint to zero**: run `scripts/drawio_lint.py` from this skill's folder:
   `python3 <skill folder>/scripts/drawio_lint.py <file.drawio> --print-width-cm <cm>`. Fix every
   finding (AUTO, DIAG, CROSS, RUN, THRU, FRAME, BORDER, TERM, BENDS, LABEL, OVERLAP, FIT, SIZE, EXIT)
   in the generator. A finding kept on purpose is named in the report with its reason. The lint needs
   Python 3 with Pillow and Arial or Liberation Sans; `DRAWIO_LINT_FONT_DIR` points it at another
   folder holding those fonts.
5. **Export**: render headless with draw.io desktop, for example
   `drawio -x -f png -s 2 -b 12 -o <out.png> <file.drawio>` (Flatpak:
   `flatpak run --filesystem=<dir> com.jgraph.drawio.desktop -x ...`). Very large PNGs are cut off
   silently, so keep the export scale moderate.
6. **Look**: read the whole render, then crops of at most about 1000 by 700 px at full size, because
   an image viewer shrinks anything wider than about 2000 px and hides small collisions. Check every
   label, every arrowhead, every group title, and the bottom and right edges.
7. **Print check**: view the render at its printed width (or the built page) and confirm the smallest
   text is readable.
8. **Cross-check**: same names as the other figures, the specs, the schema and the code.
9. **Show** the owner only after steps 4 to 8 pass, with a record of what was checked.
