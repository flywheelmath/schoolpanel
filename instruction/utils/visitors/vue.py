from .base import BaseRenderVisitor
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


class RenderVueVisitor(BaseRenderVisitor):
    def __init__(self):
        super().__init__()
        self.file_extension = "md"
        self.subtask_counter = 0
        self.in_subtask_scope = False

    def emit_task_start(self, node: TaskEntity, width_fraction):
        self.output.append("---\n\n")
        self.subtask_counter = 0

    def emit_prompt(self, node, width_fraction):
        if node.content:
            self.output.append(f"{node.content}\n\n")

        cols = node.config.get("cols", 2)
        flow = node.config.get("flow", "row")

    def emit_subtask(self, node, width_fraction):
        label = chr(ord('a') + self.subtask_counter)
        self.subtask_counter += 1
        self.output.append(f"- **{label}.** {node.content}\n")

    def visit_taskentity(self, node: TaskEntity):
        self.output.append("---\n\n")
        self.subtask_counter = 0

        prompts = [c for c in node.children if isinstance(c, TaskPromptEntity)]
        for p in prompts:
            self.visit(p)

        cols = node.config.get("cols", 2)
        flow = node.config.get("flow", "row")
        self.output.append(f'<SubtaskGrid cols="{cols}" flow="{flow}">\n\n')

        remaining_children = [c for c in node.children if not isinstance(c, TaskPromptEntity)]
        for child in remaining_children:
            self.visit(child)

        self.output.append('\n</SubtaskGrid>\n\n')

    def visit_taskpromptentity(self, node: TaskPromptEntity):
        self.output.append(f"{node.content}\n\n")

    def visit_subtaskentity(self, node: SubtaskEntity):
        label = chr(ord('a') + self.subtask_counter)
        self.subtask_counter += 1
        subtask_content = node.content if isinstance(node.content, str) else ""
        if not subtask_content and hasattr(node, "children"):
            text_parts = [c.content for c in node.children if isinstance(c, TextEntity)]
            subtask_content = "\n".join(text_parts).strip()

        self.output.append(f"- ({label}) {subtask_content}\n")

    def visit_textentity(self, node: TextEntity):
        if not self.in_subtask_scope:
            self.output.append(f"{node.content}\n")
