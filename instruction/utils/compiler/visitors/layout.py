from .base import BaseVisitor
from core.ast_models import CompositeBlock, Subtask, TaskBlock

class LayoutVisitor(BaseVisitor):
    def __init__(self):
        self.context_stack = [{'row': 0, 'col': 0, 'max_cols': 4}]

    def visit_compositeblock(self, block: CompositeBlock):
        self.context_stack.append({
            'row': 0,
            'col': 0,
            'max_cols': block.config.get("cols", 4)
        })

        for child in block.children:
            self.visit(child)

        self.context_stack.pop()

    def visit_taskblock(self, block: TaskBlock):
        ctx = self.context_stack[-1]
        max_cols = ctx["max_cols"]

        block.config['col_width_pct'] = 1 / max_cols
        block.config['col_width_tex'] = f"\\textwidth / {max_cols}"

        for subtask in block.processed_subtasks:
            span = subtask.col_span

            if ctx['col'] + span > max_cols:
                ctx['row'] += 1
                ctx['col'] = 0

            subtask.row_tex = ctx['row']
            subtask.col_tex = ctx['col']

            ctx['col'] += span
