import re
from .md_to_tex import process_md_to_tex
from .base import BaseRenderVisitor
from .layout import BaseGridRenderStrategy, DualHeightRowsGridStrategy
from core.models import (
    Cell,
    Grid,
    GraphEntity,
    Node,
    SectionHeadingEntity,
    SubtaskEntity,
    TableEntity,
    TaskEntity,
    TaskPromptEntity,
)


class RenderTeXVisitor(BaseRenderVisitor):
    def __init__(self, context=None, grid_strategy: BaseGridRenderStrategy = None):
        super().__init__(context=context)
        self.grid_strategy = grid_strategy or DualHeightRowsGridStrategy()
        self.file_extension = "tex"

    def visit_grid(self, node: Grid):
        self.grid_strategy.render(node, self)

    def visit_cell(self, node: Cell):
        if node.content:
            clean_content = process_md_to_tex(node.content)
            width_fraction = self.context.get_width(node)
            self.render_semantic_environment("cell", clean_content, width_fraction)
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
        clean_content = process_md_to_tex(node.content)
        self.render_semantic_environment("subtask", clean_content, width_fraction)
        self.generic_visit(node)

    def visit_graphentity(self, node: GraphEntity):
        self.emit_line(node.raw_body)

    def visit_tableentity(self, node: TableEntity):
        self.emit_line(node.raw_body)

    def visit_sectionheadingentity(self, node: SectionHeadingEntity):
        tex_headers = {
            1: r"\section*",
            2: r"\subsection*",
            3: r"\subsubsection*",
            4: r"\paragraph",
        }
        cmd = tex_headers.get(node.level, r"\paragraph")
        self.emit_line(f"{cmd}{{{node.content}}}\n")

    def visit_node(self, node: Node):
        if node.content.strip():
            clean_content = process_md_to_tex(node.content)
            self.emit_line(f"{clean_content}\n\n")

    def render_semantic_environment(self, env_name, content, width_fraction):
        self.emit_line(f"\\{env_name}[{width_fraction:.4f}]{{{content}}}\n")
