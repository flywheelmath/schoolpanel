# test_task_grid_pipeline.py
from core.models import Grid, Cell, TaskEntity, SubtaskEntity, TextEntity
from visitors.tex import RenderTeXVisitor, DualHeightRowsGridStrategy 

# Define custom mock objects to mirror the AST structures built by your core parser
def create_text_node(text_content):
    node = TextEntity()
    node.content = text_content
    node.children = []
    return node

def create_subtask_node(col_span, row_span, text):
    node = SubtaskEntity()
    node.config = {"col_span": str(col_span), "row_span": str(row_span)}
    node.content = text
    node.children = []
    return node

def create_task_node(col_span, row_span, prompt_col_span, prompt_text, subtasks):
    node = TaskEntity()
    node.config = {"col_span": str(col_span), "row_span": str(row_span), "prompt_col_span": str(prompt_col_span)}
    node.content = prompt_text
    node.children = subtasks
    return node

def create_cell_node(col_span, row_span, children):
    node = Cell()
    node.config = {"col_span": str(col_span), "row_span": str(row_span)}
    node.children = children
    return node

# --- STRESS TEST MATRIX DESIGN ---
# Global Row Pass 1: Columns 0-4 are blocked by a tall graphic placeholder cell.
# Columns 4-12 will host a cluster of Tasks that must stack cleanly.
left_graphic_cell = create_cell_node(4, 3, [create_text_node(r"\vbox to 3in{\vfill\centering [Complex Cartesian Coordinate Graph Space]\vfill}")])

# Task A: Prompts/Subtasks that fit in the remaining 8 columns
task_a_subtasks = [
    create_subtask_node(4, 1, "Find the inverse matrix equation."),
    create_subtask_node(4, 1, "Evaluate the determinant bounds.")
]
right_task_a = create_task_node(8, 1, 8, "Given the linear transformation matrix $T: \\mathbb{R}^2 \\to \\mathbb{R}^2$:", task_a_subtasks)

# Task B: Follows Task A inside the right-hand column bundle (Lookahead target)
task_b_subtasks = [
    create_subtask_node(8, 1, "Prove convergence using the Ratio Test.")
]
right_task_b = create_task_node(8, 2, 4, "Analyze the behavior of the infinite power series expression:", task_b_subtasks)

# Global Grid Root Node Assembly
global_grid = Grid()
global_grid.config = {"cols": "12"}
global_grid.children = [
    left_graphic_cell,
    right_task_a,
    right_task_b
]

# Set up AST tree structures array
ast_root = [global_grid]

print("=== EXECUTING RIGOROUS TASK & LAYOUT PIPELINE EXCLUSION ===")
# Use your decoupled Strategy pattern layout walker
strategy = DualHeightRowsGridStrategy()
tex_visitor = RenderTeXVisitor(grid_strategy=strategy)

for node in ast_root:
    tex_visitor.visit(node)

print(tex_visitor.get_result())
