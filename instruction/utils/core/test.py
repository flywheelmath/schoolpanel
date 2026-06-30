from parser import Parser
from models import Node, DomainEntity, LayoutNode, Cell, Grid, TaskEntity, SubtaskEntity, GraphEntity, TableEntity, TextEntity

test_md = """
::: task {label="2."}
Analyze the trajectory of the launched projectile and answer the following questions.

::: grid {cols=12}

::: cell {col_span=7}
The height $h(t)$ in meters of a projectile after $t$ seconds is modeled by the function $h(t) = -4.9t^2 + 19.6t + 1.5$.

::: subtask {label="2a."}
Determine the maximum height reached by the projectile. Show your work.

::: grid {cols=12}
::: cell {col_span=6}
*Hint: Remember to find the vertex of the parabola.*
:::
::: cell {col_span=6}
::: table {rows=2, cols=2}
t | h(t)
1 | 16.2
2 | 21.1
:::
:::
:::
:::

::: subtask {label="2b."}
At what exact time does the projectile hit the ground?
:::

:::

::: cell {col_span=5}
::: graph {height=300, width=300}
y = -4.9x^2 + 19.6x + 1.5
bounds_x = [-1, 5]
bounds_y = [-5, 25]
:::
:::

:::
:::
"""

def print_ast(node, level=0):
    indent = "  " * level
    
    # Check if it's a Layout or Domain node for visualization
    node_type = "Layout" if isinstance(node, LayoutNode) else "Domain"
    
    if isinstance(node, TaskEntity):
        print(f"{indent}[{node_type}] TaskEntity (Label: {node.label}) -> Prompt: '{node.content[:20]}...'")
        for child in node.children:
            print_ast(child, level + 1)
            
    elif hasattr(node, 'children') and isinstance(node.children, list):
        # Grids
        span_info = f"span={node.col_span}" if hasattr(node, 'col_span') else ""
        print(f"{indent}[{node_type}] {type(node).__name__} {span_info}")
        for child in node.children:
            print_ast(child, level + 1)
            
    elif isinstance(node, Cell):
        print(f"{indent}[{node_type}] Cell (span={node.col_span})")
        for child in node.children:
            print_ast(child, level + 1)
            
    else:
        # Leaves (Graph, Text)
        body = getattr(node, 'content', getattr(node, 'raw_body', ''))
        print(f"{indent}[{node_type}] {type(node).__name__} -> '{body[:2000]}...'")

if __name__ == "__main__":
    parser = Parser(test_md)
    ast = parser.parse()
    
    print("=== PIPELINE STAGE 1: RAW AST ===")
    for node in ast:
        print_ast(node)
