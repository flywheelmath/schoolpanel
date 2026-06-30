from .base import ASTVisitor
from core.models import Cell, Grid


class LayoutVisitor(ASTVisitor):
    def __init__(self):
        self.context_stack = [12]

    def visit_grid(self, node: Grid):
        parent_cols = self.context_stack[-1]
        cols = node.config.get("cols", parent_cols)
        self.context_stack.append(cols)
        try:
            self.generic_visit(node)
        finally:
            self.context_stack.pop()
        print(f"DEBUG: Entering {type(node).__name__}, Stack: {self.context_stack}")

    def visit_cell(self, node: Cell):
        grid_cols = self.context_stack[-1]
        node.width_fraction = node.col_span / grid_cols
        self.generic_visit(node)
        print(f"DEBUG: Entering {type(node).__name__}, Stack: {self.context_stack}")
