# instruction/utils/compiler/test_parser.py
from compiler import compile

test_markdown = """
::: tasks {counter_type: "alph", shape: "parens", resume: False}
* x + 5 = 7
* 2x - 3 = 9
:::

::: graph {xmin: -10, xmax: 10, ymin: -10, ymax: 10}
plot: "x^2 - 4" {color: "blue", domain: "-3 < x <= 3"}
plot: "y > 2*x + 1" {color: "red"}
plot: "x^2 + y^2 = 25"
:::
"""

def test_pipeline():
    ast = compile(test_markdown)
    
    print("--- AST Output ---")
    for i, node in enumerate(ast):
        print(f"\nBlock {i+1}: {type(node).__name__}")
        
        # Test Task Layout & State
        if hasattr(node, 'processed_subtasks'):
            for sub in node.processed_subtasks:
                print(f"  [{sub.label}] Row: {sub.row_tex} | Col: {sub.col_tex} | Text: {sub.text}")
                
        # Test Graph Evaluation
        if hasattr(node, 'plots'):
            for plot in node.plots:
                print(f"\n  Plot: {plot['original_expr']}")
                print(f"    Type: {plot['type']} | Color: {plot['color']} | Dashed: {plot.get('dashed', False)}")
                
                if plot.get('computed_coordinates'):
                    print(f"    Coords: {plot['computed_coordinates'][:60]}...")
                if plot.get('fill_polygon'):
                    print(f"    Shading Vertices: {plot['fill_polygon']}")

if __name__ == "__main__":
    test_pipeline()
