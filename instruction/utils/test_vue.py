# instruction/tests/test_visitors.py
import pytest
from .vue import RenderVueVisitor

class TaskEntity:
    def __init__(self, content, config=None, children=None):
        self.content = content
        self.config = config or {}
        self.children = children or []

class SubtaskEntity:
    def __init__(self, label, content, children=None):
        self.label = label
        self.content = content
        self.children = children or []

def test_render_vue_visitor_minimalist_flow():
    """
    Verifies that RenderVueVisitor correctly serializes a TaskEntity and its 
    Subtask children into the minimalist Slidev/SubtaskGrid layout format.
    """
    # 1. Arrange: Build a realistic mini-AST representing an equation task
    subtask_a = SubtaskEntity(label="a", content="$2x = 10 \\rightarrow x = 5$", children=[])
    subtask_b = SubtaskEntity(label="b", content="Check: $2(5) + 5 = 15$", children=[])
    
    task_node = TaskEntity(
        content="Solve for $x$: $2x + 5 = 15$",
        config={"cols": 2, "flow": "row"},
        children=[subtask_a, subtask_b]
    )

    # 2. Act: Initialize the visitor and execute traversal
    visitor = RenderVueVisitor()
    visitor.visit(task_node)
    result = visitor.get_result()

    # 3. Assert: Verify the structural layout expectations are met exactly
    
    # Assert slide boundary separator and prompt rendering
    print(result)
    assert "---\n\n" in result
    assert "Solve for $x$: $2x + 5 = 15$\n\n" in result
    
    # Assert that the wrapper tag parses props correctly for frontend extraction
    assert '<SubtaskGrid cols="2" flow="row">' in result
    
    # Assert subtasks preserve standard Markdown list formatting for innerHTML parsing
    assert "- **a.** $2x = 10 \\rightarrow x = 5$\n" in result
    assert "- **b.** Check: $2(5) + 5 = 15$\n" in result
    
    # Assert closing boundary tags are matched cleanly to prevent syntax leakage
    assert "\n</SubtaskGrid>\n\n" in result


def test_render_vue_visitor_config_fallbacks():
    """
    Verifies that the visitor falls back gracefully if config properties 
    are missing from the TaskEntity node configuration block.
    """
    # Arrange an entity lacking explicit presentation configs
    task_node = TaskEntity(
        content="Raw prompt content string",
        config={},  # Empty dictionary check
        children=[]
    )
    
    # Act
    visitor = RenderVueVisitor()
    visitor.visit(task_node)
    result = visitor.get_result()
    
    # Assert defaults populate seamlessly from the dictionary .get defaults (cols=2, flow='row')
    print(result)
    assert '<SubtaskGrid cols="2" flow="row">' in result
