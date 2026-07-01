from .base import BaseRenderVistor
from core.models import (
    Cell,
    Grid,
    GraphEntity,
    SubtaskEntity,
    TableEntity,
    TaskEntity,
    TextEntity,
)


class RenderVueVisitor(BaseRenderVisitor):
    def __init__(self):
        super().__init__()
        self.output = []

    def get_result(self) -> str:
        content = "\n".join(self.output)
        return content

    def visit_grid(self, node: Grid):
        self.output.append('<Grid>')
        for child in node.children:
            self.visit(child)
        self.output.append("</Grid>")

    def visit_cell(self, node: Cell):
        percentage = node.width_fraction * 100
        self.output.append(f'  <GridCell :width-percent="{percentage:.5f}">')
        for child in node.children:
            self.visit(child)
        self.output.append(f'  </GridCell>')

    def visit_taskentity(self, node: TaskEntity):
        self.output.append('\n---\n')
        self.output.append(f'### {node.label} {node.content}')
        self.generic_visit(node)

    def visit_subtaskentity(self, node: SubtaskEntity):
        self.output.append(f'\n**{node.label}** {node.content}')
        self.generic_visit(node)

    def visit_textentity(self, node: TextEntity):
        self.output.append(node.content)

    def visit_graphentity(self, node: GraphEntity):
        self.output.append(f'<GraphRenderer :raw-data="`{node.raw_body}`" />')

    def visit_tableentity(self, node: TableEntity):
        self.output.append(f'<TableRenderer :raw-data="`{node.raw_body}`" />')
