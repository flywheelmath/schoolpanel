# test_text_engine.py
from core.parser import Tokenizer, Parser
from visitors.tex import RenderTeXVisitor

test_layout_md = r"""
::: task {label="5."}
# Layout Grid Tracker Verification

::: grid {cols="12"}
  ::: cell {col_span="4", row_span="2"}
  **Cell 1 (Left Column)**
  This cell covers 4 columns and spans 2 rows vertically.
  :::

  ::: cell {col_span="8", row_span="1"}
  **Cell 2 (Top Right)**
  This cell covers 8 columns in row 1.
  :::

  ::: cell {col_span="8", row_span="1"}
  **Cell 3 (Bottom Right)**
  This should automatically skip past the 4 columns blocked by Cell 1, landing smoothly in the 2nd row, 5th column.
  :::
:::
:::
"""

print("=== PARSING & RENDERING GRID LAYOUT ===")
parser = Parser(test_layout_md)
tokens = Tokenizer(test_layout_md).tokenize()
ast = parser.parse()

tex_engine = RenderTeXVisitor()
for node in ast:
    tex_engine.visit(node)

print(tex_engine.get_result())
