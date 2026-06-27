from base import BaseVisitor
from core.ast_models import TableBlock

class TableLayoutVisitor(BaseVisitor):
    def visit(self, node):
        if isinstance(node, TableBlock):
            self.visit_table(node)

    def visit_tableblock(self, block: TableBlock):
        num_cols = len(block.headers)
        col_width = 1.0 / num_cols
        block.config['col_width_percentage'] = col_width
