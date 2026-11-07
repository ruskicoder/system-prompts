---
name: diagram-check-loop
description: Check a boxes-and-arrows figure before anyone sees it. Runs the architecture-diagrams geometry lint to zero findings, renders the figure headless, reads the render whole and in full-size crops, checks it at print width, and cross-checks names against the code and the other figures. Use for "draw the architecture diagram", "fix this figure", after any change to a draw.io file, and before a figure goes into a report or slide.
argument-hint: "<.drawio file or figure> [print width in cm]"
---

# Workflow: Diagram Check Loop

## When to Use
| Criteria | Match |
|----------|-------|
| Intention | draw, redraw, fix or review an architecture, deployment, context or integration figure |
| Input | a `.drawio` file (uncompressed), or a figure to draw from code |
| Power Mode | Balanced |

## Required Skills
- architecture-diagrams (rules, generator approach, lint)
- ui-ux-philosophy (recognition, hierarchy and accessibility rules where the figure is read on screen)
- build-discipline, communication-tone

## Rules
- A figure is shown to the owner only after steps 2 to 6 pass. "Looks fine in the editor" is not a
  check.
- Every change goes through the figure's generator script, never a hand edit of the XML alone, so the
  next run does not undo it.
- The render and the crops are looked at with the image tool, not described from the XML.
- Do not start a second draw.io or browser process when one is running; check available memory
  first on a constrained machine, and close what you opened after each check.
- At most three fix rounds. Whatever is still open after that goes in the report with its reason.

## Flow

### Step 1: Inventory and sketch (new figures only)
List blocks, code paths, protocols and third parties from the code (architecture-diagrams section 1).
Draw a text sketch of tiers, columns and flows and get the owner's yes before writing XML.

### Step 2: Lint to zero
Run the lint from the architecture-diagrams skill folder:

    python3 <skill folder>/scripts/drawio_lint.py <file.drawio> --print-width-cm <cm>

Fix every finding in the generator and run it again until it prints 0 findings. A finding kept on
purpose is named in the report with its reason.

### Step 3: Render
Export the figure headless with draw.io desktop, for example:

    drawio -x -f png -s 2 -b 12 -o <out.png> <file.drawio>

On Linux with the Flatpak build: `flatpak run --filesystem=<dir> com.jgraph.drawio.desktop -x ...`.

### Step 4: Look whole, then in crops
Read the whole render, then crops of at most about 1000 by 700 px at full size, covering the whole
figure, because image viewers shrink large images and hide small collisions. For each crop check
every label, arrowhead, group title, attachment point, and the right and bottom edges.

### Step 5: Print check
View the render at its printed width (or the built page) and confirm the smallest text is readable
and every line style is distinguishable in grey.

### Step 6: Cross-check
Names match the other figures, the specs, the schema and the code; every block opens to a real path.

### Step 7: Report
Use the communication-tone reply contract. Done lists the lint result (0 findings, or the kept ones
with reasons), the render path, the crops looked at and the print width checked. State lists
anything still open.

## Outputs
- The updated generator script, `.drawio` file and render.
- A check record: lint output, crops read, print width, cross-check result.
