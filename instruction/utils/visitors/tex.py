import re
from .md_to_tex import process_md_to_tex
from .base import BaseRenderVisitor
from .layout import BaseGridRenderStrategy, DualHeightRowsGridStrategy
from core.models import (
    Cell,
    Grid,
    GraphEntity,
    SubtaskEntity,
    TableEntity,
    TaskEntity,
    TaskPromptEntity,
    TextEntity,
)


class RenderTeXVisitor(BaseRenderVisitor):
    def __init__(self, context=None, grid_strategy: BaseGridRenderStrategy = None):
        super().__init__(context=context)
        self.grid_strategy = grid_strategy or DualHeightRowsGridStrategy()
        self.file_extension = "tex"

    def visit_grid(self, node: Grid):
        self.grid_strategy.render(node, self)

    def visit_cell(self, node: Cell):
        self.generic_visit(node)

    def emit_task_start(self, node, width_fraction):
        self.emit_line(f"\\begin{{task}}[{width_fraction:.4f}]\n")

    def emit_task_end(self, node):
        self.emit_line("\\end{task}\n")

    def visit_taskentity(self, node: TaskEntity):
        width_fraction = self.context.get_width(node)
        self.emit_task_start(node, width_fraction)

        with self.indent():
            self.grid_strategy.render(node, self)

        self.emit_task_end(node)

    def visit_taskpromptentity(self, node: TaskPromptEntity):
        width_fraction = self.context.get_width(node)
        clean_content = process_md_to_tex(node.content)
        self.render_semantic_environment("prompt", clean_content, width_fraction)

    def visit_subtaskentity(self, node: SubtaskEntity):
        width_fraction = self.context.get_width(node) 
        subtask_text = node.content if isinstance(node.content, str) else ""
        if not subtask_text and hasattr(node, "children"):
            text_parts = [c.content for c in node.children if isinstance(c, TextEntity)]
            subtask_text = "\n".join(text_parts).strip()

        clean_content = process_md_to_tex(subtask_text)
        self.render_semantic_environment("subtask", clean_content, width_fraction)

    def visit_textentity(self, node: TextEntity):
        if node.content.strip().startswith("\\"):
            self.emit_line(node.content + "\n")
        else:
            clean_tex = process_md_to_tex(node.content)
            self.emit_line(clean_tex + "\n")

    def visit_graphentity(self, node: GraphEntity):
        self.emit_line(node.raw_body)

    def visit_tableentity(self, node: TableEntity):
        self.emit_line(node.raw_body)

    def render_semantic_environment(self, env_name, content, width_fraction):
        self.emit_line(f"\\{env_name}[{width_fraction:.4f}]{{{content}}}\n")
