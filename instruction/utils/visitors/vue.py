from .base import BaseRenderVisitor
from core.models import (
    Cell,
    Grid,
    GraphEntity,
    Node,
    SubtaskEntity,
    TableEntity,
    TaskEntity,
    TaskPromptEntity,
)


class RenderVueVisitor(BaseRenderVisitor):
    def __init__(self, context=None):
        super().__init__(context=context)
        self.file_extension = "md"
        self.subtask_counter = 0

    def emit_headmatter(self):
        self.output.append("---\ntheme: default\nmdc: true\n---\n\n")

    def emit_line(self, line: str = ""):
        if line.strip():
            self.output.append(line)

    def visit_taskentity(self, node: TaskEntity):
        self.output.append("---\n\n")
        self.subtask_counter = 0

        prompts = [c for c in node.children if isinstance(c, TaskPromptEntity)]
        for p in prompts:
            self.visit(p)

        cols = node.config.get("cols", 2)
        flow = node.config.get("flow", "row")
        self.output.append(f'<SubtaskGrid cols="{cols}" flow="{flow}">\n\n')

        with self.indent():
            remaining_children = [
                c for c in node.children if not isinstance(c, TaskPromptEntity)
            ]
            for child in remaining_children:
                self.visit(child)

        self.emit_line("\n</SubtaskGrid>\n\n")

    def visit_taskpromptentity(self, node: TaskPromptEntity):
        if node.content.strip():
            self.emit_line(f"{node.content}\n\n")

    def visit_subtaskentity(self, node: SubtaskEntity):
        label = chr(ord("a") + self.subtask_counter)
        self.subtask_counter += 1

        if not node.content.strip():
            return

        lines = node.content.strip().split("\n")
        formatted_body = []
        first_line = lines[0].strip()
        if self.indent_level % 2 == 0:
            bullet = "-"
        else:
            bullet = "*"
        formatted_body.append(f"{bullet} ({label}) {first_line}")

        for line in lines[1:]:
            if not line.strip():
                formatted_body.append("")
                continue

            if line.startswith("  ") or line.startswith("\t"):
                formatted_body.append(f"  {line}")
            else:
                formatted_body.append(f"  {line}")

        self.emit_line("\n".join(formatted_body) + "\n")
        self.generic_visit(node)

    def visit_grid(self, node: Grid):
        self.emit_line('<div class="grid-row">\n')
        with self.indent():
            self.generic_visit(node)
        self.emit_line("</div>\n\n")

    def visit_cell(self, node: Cell):
        col_span = node.config.get("col_span", 4)
        self.emit_line(f'<div class="grid-cell col-{col_span}">\n')
        with self.indent():
            if node.content:
                self.emit_line(node.content + "\n")
            self.generic_visit(node)
        self.emit_line("</div>\n")
