from .base import BaseVisitor
from core.ast_models import TableBlock

class TableLayoutVisitor(BaseVisitor):
    def visit_tableblock(self, block: TableBlock):
        cols = len(block.headers)
        block.config['col_def'] = "|" + " X |" * cols
        block.config['width_tex'] = "\\textwidth"
