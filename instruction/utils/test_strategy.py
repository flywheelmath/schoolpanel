# test_strategy.py
from core.parser import Tokenizer, Parser
from visitors.tex import RenderTeXVisitor, DualHeightRowsGridStrategy

test_markdown = r"""
# Strategy Pattern Layout Test

::: grid {cols="12"}
  ::: cell {col_span="6", row_span="1"}
  **Right Sibling 1**
  This is a short 1-row cell.
  :::
  
  ::: cell {col_span="6", row_span="2"}
  **Right Sibling 2 (The Filler)**
  The strategy engine should look ahead, see this 2-row cell, 
  realize that 1 + 2 = 3 (matching the left anchor), and pack it seamlessly 
  underneath Right Sibling 1!
  :::

  ::: cell {col_span="6", row_span="3"}
  **The Tall Left Anchor**
  This cell requests a massive 3-row vertical span.
  Because it is the tallest in the row, it will become the parent anchor.
  :::
  
:::
"""

test_markdown = r"""
# Rigorous Hierarchical Layout Test

::: grid {cols="12"}
  % --- BLOCK 1: Tall on the Right ---
  ::: cell {col_span="6", row_span="1"}
  **1. Left Short (Row 1)**
  Starts the first block.
  :::
  ::: cell {col_span="6", row_span="4"}
  **2. Right Tall Anchor (Row 1-4)**
  This is a massive 4-row cell on the right.
  The engine should partition here and realize the left side is shorter.
  :::
  ::: cell {col_span="6", row_span="1"}
  **3. Left Filler A (Row 2)**
  First lookahead cell.
  :::
  ::: cell {col_span="6", row_span="2"}
  **4. Left Filler B (Row 3-4)**
  Second lookahead cell. (1 + 1 + 2 = 4).
  This should perfectly exhaust the left side's remaining space!
  :::

  % --- BLOCK 2: Tall Left & Variance Partitioning ---
  ::: cell {col_span="4", row_span="3"}
  **5. Left Tall Anchor (Row 5-7)**
  New row block begins. 3-row anchor on the left.
  :::
  ::: cell {col_span="4", row_span="1"}
  **6. Right Multicell A (Row 5)**
  First half of the short side.
  :::
  ::: cell {col_span="4", row_span="1"}
  **7. Right Multicell B (Row 5)**
  Second half of the short side.
  The variance engine should group 6 & 7 together!
  :::
  ::: cell {col_span="8", row_span="2"}
  **8. Right Filler (Row 6-7)**
  Lookahead filler that takes up the full 8-column width of the right partition.
  It should tuck perfectly underneath 6 & 7.
  :::
:::
"""

print("=== PARSING & RENDERING STRATEGY GRID ===")
# Parse the raw markdown into our AST
parser = Parser(test_markdown)
ast = parser.parse()

# Instantiate the Visitor and specifically inject our new Strategy
strategy = DualHeightRowsGridStrategy()
tex_visitor = RenderTeXVisitor(grid_strategy=strategy)

# Run the compilation
for node in ast:
    tex_visitor.visit(node)

print(tex_visitor.get_result())
