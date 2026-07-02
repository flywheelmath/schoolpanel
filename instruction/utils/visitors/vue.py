from .base import BaseRenderVisitor
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
    def emit_task_stark(self, node: TaskEntity, width_fraction):
        self.output.append("---\n\n")

    def emit_prompt(self, node, width_fraction):
        self.output.append(f"{node.content}\n\n")
        cols = node.config.get("cols", 2)
        flow = node.config.get("flow", "row")
        self.output.append(f'<SubtaskGrid cols="{cols}" flow="{flow}">\n\n')

    def emit_subtask(self, node, width_fraction):
        self.output.append(f"- **{node.label}.** {node.content}\n")

    def emit_task_end(self, node):
        self.output.append('\n</SubtaskGrid>\n\n')
