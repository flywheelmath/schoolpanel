# test.py
from core.parser import Tokenizer, Parser
from visitors.layout import LayoutVisitor
from visitors.tex import RenderTeXVisitor
from visitors.vue import RenderVueVisitor

test_md = """
::: task {label="2."}
Analyze the trajectory of the projectile.
::: grid {cols=12}
::: cell {col_span=7}
The height $h(t) = -4.9t^2 + 19.6t + 1.5$.
::: subtask {label="2a."}
Determine the maximum height.
::: grid {cols=4}
::: cell {col_span=4}
*Hint: Find the vertex.*
:::
:::
:::
:::
::: cell {col_span=5}
::: graph {xmin=-1, xmax=5}
y = -4.9x^2 + 19.6x + 1.5
:::
:::
:::
"""

# 1. Parsing Phase
parser = Parser(test_md)
tokens = Tokenizer(test_md).tokenize()
ast = parser.parse()

# 2. Layout Pass (Virtual Grid Calculation)
layout_engine = LayoutVisitor()
for node in ast:
    layout_engine.visit(node)

# 3. Render Passes
tex_engine = RenderTeXVisitor()
vue_engine = RenderVueVisitor()

for node in ast:
    tex_engine.visit(node)
    vue_engine.visit(node)

print("=== GENERATED LATEX OUTPUT ===")
print(tex_engine.get_result())
print("\n=== GENERATED VUE TEMPLATE ===")
print(vue_engine.get_result())
