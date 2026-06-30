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


class RenderTeXVisitor(ASTVisitor):
    def __init__(self):
        self.output = []

    def get_result(self) -> str:
        return "\n".join(self.output)

    def visit_grid(self, node: Grid):
        self.output.append(r"% --- Start Grid ---")
        for child in node.children:
            self.visit(child)
        self.output.append(r"% --- End Grid ---")

    def visit_cell(self, node: Cell):
        self.output.append(
            f"\\begin{{minipage}}[t]{{{node.width_fraction:.5f}\\textwidth}}"
        )
        for child in node.children:
            self.visit(child)
        self.output.append(r"\end{minipage}")

    def visit_textentity(self, node: TextEntity):
        self.output.append(node.content + "\n")

    def visit_taskentity(self, node: TaskEntity):
        self.output.append(f"\\begin{{task}}{{{node.label}}}")
        self.output.append(node.content + "\n")
        self.generic_visit(node)
        self.output.append("\\end{task}\n")

    def visit_subtaskentity(self, node: SubtaskEntity):
        self.output.append(f"\\begin{{subtask}}{{{node.label}}}")
        self.output.append(node.content)
        self.generic_visit(node)
        self.output.append("\\end{subtask}")

    def visit_graphentity(self, node: GraphEntity):
        self.output.append(r"% --- Start graph ---")
        self.output.append(node.raw_body)
        self.output.append(r"% --- End graph ---")

    def visit_tableentity(self, node: TableEntity):
        self.output.append(r"% --- Start table ---")
        self.output.append(node.raw_body)
        self.output.append(r"% --- End table ---")
