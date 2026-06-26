# instruction/utils/compiler/test_parser.py
from compiler import compile
import json

test_markdown = """
::: tasks {counter_type: "alph", shape: "parens"}
- x + 5 = 7
- x - 3 = 10
:::

::: tasks {resume: True}
* x + 8 = 20
:::
"""

def test_pipeline():
    ast = compile(test_markdown)
    
    print("--- AST Output After Layout Visitor ---")
    for i, node in enumerate(ast):
        print(f"Block {i+1}:")
        if hasattr(node, 'processed_subtasks'):
            for sub in node.processed_subtasks:
                print(f"  [{sub.label}] Row: {sub.row_tex} | Col: {sub.col_tex} | Text: {sub.text}")

if __name__ == "__main__":
    test_pipeline()
