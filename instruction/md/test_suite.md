SSG Architecture Test Suite

This document rigorously tests the compiler pipeline, verifying the Lexer, Math Engine, and both the LaTeX and Vue Renderers.

Part 1: 2D Task Grid & Macros

This block tests the 2D grid reservation algorithm. The second task spans two rows vertically, which should force the subsequent tasks to gracefully wrap around it without causing DOM or LaTeX tabular overlaps. It also tests the macro injection from macros.json.
::tasks
cols=3, counter='arabic', shape='circle'

[colspan=2] Test A: Simplify the following complex fraction using the provided blank scaffold:
$\blankfraction[2]$

[rowspan=2] Test B (Vertical Block): This task spans two full rows. The engine should reserve the space beneath it.

Test C: Standard 1x1 task. $\blank[3]$

Test D: Because of Test B's rowspan, this should appear directly below Test C, skipping the middle column!

[colspan=3] Test E: This task has colspan=3 and should span the entire bottom row of the matrix, triggering pagination if max_rows is exceeded.
::

Part 2: Vertical Delta Tables & Line Breaks

This table tests the Math Engine's enrich_table_deltas method, automatically calculating the +4 and +5 differences between the $y$-values and generating the TikZ/Vue arrows. It also tests <br> translation.
::table
arrows=True, align='c'
$x$ | $f(x)$ | Notes
1 | 3 | Start of sequence
2 | 7 | Diff is +4
3 | 12 | Diff is +5



(Non-linear!)
4 | 19 | Diff is +7
::

Part 3: Transposed (Horizontal) Delta Tables

This table forces the engine to transpose the data structure and calculates the deltas horizontally, routing the arrows over the top and bottom of the matrix.
::table
arrows=True, transpose=True
$x$ | 1 | 2 | 3 | 4
$y$ | 10 | 8 | 6 | 4
::

Part 4: The Physics & Math Engine

This graph stresses the Math Engine's domain parsers, inequality shading, parametric evaluations, and label positioning.
::graph
xmin=-8, xmax=8, ymin=-8, ymax=8, grid='both', hide_zero=False

plot("y <= 0.5x + 2", color="green", behavior="linear", label="y \le \frac{1}{2}x + 2")

plot("abs(x - 3) - 4", color="red", behavior="abs", label="g(x)")

plot(x="5cos(t)", y="5sin(t)", color="purple", dashed=True, label="Circle")

point(3, -4, label="Vertex", color="red")
point(-4, 0, label="Root", color="green")
point(0, 5, label="y-int", color="purple")
::
