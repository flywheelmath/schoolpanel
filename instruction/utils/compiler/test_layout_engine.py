from compiler import compile
from core.ast_models import CompositeBlock, TaskBlock

def test_nested_hierarchy():
    with open("test_suite.md", "r") as f:
        md_content = f.read()

    print("--- Parsing Nested AST ---")
    ast = compile(md_content)
    
    # 1. Verify Structure
    assert isinstance(ast, CompositeBlock), "Top level should be a CompositeBlock"
    assert len(ast.children) == 2, "Should have 2 nested TaskBlocks"
    
    for i, child in enumerate(ast.children):
        print(f"\nTaskBlock {i+1}:")
        assert isinstance(child, TaskBlock)
        
        for j, st in enumerate(child.processed_subtasks):
            print(f"  Subtask {j+1} [Span: {st.row_span_tex}x{st.col_span_tex}]")
            
            # 2. Verify Span Logic
            if i == 1 and j == 0: # Check Subtask B1
                assert st.col_span_tex == 4, "Subtask B1 should span 4 cols"
                assert st.row_span_tex == 2, "Subtask B1 should span 2 rows"

    print("\n--- Hierarchy Validation Passed ---")

if __name__ == "__main__":
    test_nested_hierarchy()
