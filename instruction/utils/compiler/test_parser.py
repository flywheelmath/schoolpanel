# test_parser.py
from core.lexer import lex_markdown
from core.parser import parse_markdown

test_markdown = """
::: tasks {counter_type: "alph", shape: "parens"}
* x + 5 = 7
* x - 3 = 10
* x + 8 = 20
:::

::: graph {width: "40%"}
plot: "x^2 * sin(x)"
:::
"""

def test_pipeline():
    print("--- 1. Lexing ---")
    chunks = lex_markdown(test_markdown)
    for chunk in chunks:
        print(f"Found block: {chunk['tag']}")

    print("\n--- 2. Parsing ---")
    ast = parse_markdown(test_markdown)
    for node in ast:
        print(f"Parsed node: {type(node).__name__}")
        if hasattr(node, 'processed_subtasks'):
            print(f"  - Subtasks: {len(node.processed_subtasks)}")

if __name__ == "__main__":
    test_pipeline()
