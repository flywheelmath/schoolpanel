from base import BaseVisitor
from core.ast_models import Subtask, TaskBlock

class LayoutVisitor(BaseVisitor):
    def visit(self, ast_nodes: list):
        for node in ast_nodes:
            self._dispatch(node)

    def generic_visit(self, node):
        pass

    def visit_taskblock(self, block: TaskBlock):
        max_cols = block.config.get("cols_tex", 4)

        current_row = 0
        current_col = 0

        for subtask in block.processed_subtasks:
            span = subtask.col_span

            if current_col + span > max_cols:
                current_row += 1
                current_col = 0

            subtask.row_tex = current_row
            subtask.col_tex = current_col

            current_col += span
