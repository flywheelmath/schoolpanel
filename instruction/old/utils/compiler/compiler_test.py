from core.parser import Parser
from visitors.layout import LayoutVisitor

# 1. Test Input: A grid with mixed spans and nesting
test_md = """
::: grid {col_span=12}
::: cell {col_span=4}
Graph the function.
:::
::: cell {col_span=5}
::: graph {col_span=3}
y = x^2
:::
::: graph {col_span=1}
y = x^2
:::

:::
::: cell {col_span=2}
::: graph {col_span=3}
y = x^2
:::
:::
:::
"""

# 2. Run the Parser
parser = Parser(test_md)
ast = parser.parse()

# 3. Run the LayoutVisitor
visitor = LayoutVisitor()
for node in ast:
    visitor.visit(node)

# 4. Helper to print the tree
def print_tree(node, level=0):
    indent = "  " * level
    if hasattr(node, 'children'):
        print(f"{indent}{type(node).__name__} (row={getattr(node, 'row_tex', 0)}, col={getattr(node, 'col_tex', 0)})")
        for child in node.children:
            print_tree(child, level + 1)
    else:
        print(f"{indent}{type(node).__name__} (row={getattr(node, 'row_tex', 0)}, col={getattr(node, 'col_tex', 0)})")

print("Generated AST Tree:")
for node in ast:
    print_tree(node)
