from .base import ASTVisitor
from core.models import (
    Cell,
    Grid,
    GraphEntity,
    SubtaskEntity,
    TableEntity,
    TaskEntity,
    TextEntity,
)


class RenderVueVisitor(ASTVisitor):
    def __init__(self):
        self.output = []

    def get_result(self) -> str:
        content = "\n".join(self.output)
        return f'<template>\n  <div class="curriculum-task">\n{content}\n  </div>\n</template>'

    def visit_grid(self, node: Grid):
        self.output.append("    ")
        self.output.append(
            '    <div style="display: flex; flex-wrap: wrap; width: 100%;">'
        )

        for child in node.children:
            self.visit(child)

        self.output.append("    </div>")
        self.output.append("    ")

    def visit_cell(self, node: Cell):
        percentage = node.width_fraction * 100
        self.output.append(
            f'      <div style="width: {percentage:.5f}%; box-sizing: border-box; padding-right: 1rem;">'
        )

        for child in node.children:
            self.visit(child)

        self.output.append("      </div>")

    def visit_taskentity(self, node: TaskEntity):
        self.output.append('    <div class="task-block" style="margin-bottom: 2rem;">')
        self.output.append(f"      <h3>{node.label}</h3>")
        self.output.append(f'      <div class="task-content">{node.content}</div>')
        self.generic_visit(node)
        self.output.append("    </div>")

    def visit_subtaskentity(self, node: SubtaskEntity):
        self.output.append('    <div class="subtask-block" style="margin-top: 1rem;">')
        self.output.append(f'      <div class="task-content">{node.content}</div>')
        self.generic_visit(node)
        self.output.append("    </div>")

    def visit_textentity(self, node: TextEntity):
        self.output.append(f"      <p>{node.content}</p>")

    def visit_graphentity(self, node: GraphEntity):
        self.output.append(f'      <GraphRenderer :raw-data="`{node.raw_body}`" />')

    def visit_tableentity(self, node: TableEntity):
        self.output.append(f'      <TableRenderer :raw-data="`{node.raw_body}`" />')
