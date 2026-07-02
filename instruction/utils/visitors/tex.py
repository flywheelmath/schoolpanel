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
        width = getattr(node, "width_fraction", 1.00)
        self.output.append(f"\\begin{{minipage}}[t]{{{width:.4f}\\textwidth}}\n")
        self.generic_visit(node)
        self.output.append(r"\end{minipage}")

    def emit_task_start(self, node, width_fraction):
        self.output.append(f"\\begin{{task}}[{width_fraction:.4f}]\n")

    def emit_task_end(self, node):
        self.output.append("\\end{task}\n")

    def visit_taskentity(self, node: TaskEntity):
        parent_span = int(node.config.get("col_span", 12))
        task_fraction = parent_span / 12.0
        self.context.set_width(node, task_fraction)

        self.emit_task_start(node, task_fraction)

        self.current_task_span = parent_span
        self.generic_visit(node)
        self.emit_task_end(node)

    def visit_taskpromptentity(self, node: TaskPromptEntity):
        parent_span = getattr(self, "current_task_span", 12)
        prompt_span = int(node.config.get("col_span", parent_span))
        prompt_fraction = prompt_span / parent_span

        clean_content = process_md_to_tex(node.content)

        self.render_semantic_environment("prompt", clean_content, prompt_fraction)

    def visit_subtaskentity(self, node: SubtaskEntity):
        item_span = int(node.config.get("col_span", 12))
        width_fraction = item_span / 12.0
        subtask_text = node.content if isinstance(node.content, str) else ""
        if not subtask_text and hasattr(node, "children"):
            text_parts = [c.content for c in node.children if isinstance(c, TextEntity)]
            subtask_text = "\n".join(text_parts).strip()

        clean_content = process_md_to_tex(subtask_text)
        self.render_semantic_environment("subtask", clean_content, width_fraction)

    def visit_textentity(self, node: TextEntity):
        if node.content.strip().startswith("\\"):
            self.output.append(node.content + "\n")
        else:
            clean_tex = process_md_to_tex(node.content)
            self.output.append(clean_tex + "\n")

    def visit_graphentity(self, node: GraphEntity):
        self.output.append(r"% --- Start graph ---")
        self.output.append(node.raw_body)
        self.output.append(r"% --- End graph ---")

    def visit_tableentity(self, node: TableEntity):
        self.output.append(r"% --- Start table ---")
        self.output.append(node.raw_body)
        self.output.append(r"% --- End table ---")

    def render_semantic_environment(self, env_name, content, width_fraction):
        self.output.append(f"  \\begin{{{env_name}}}[{width_fraction:.4f}]\n")
        self.output.append(f"    {content}\n")
        self.output.append(f"  \\end{{{env_name}}}\n")
