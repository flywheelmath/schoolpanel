from .core.models import (
    Node,
    Grid,
    Cell,
    TaskEntity,
    SubtaskEntity,
    TextEntity,
    GraphEntity,
    TableEntity,
)


class RenderContext:
    def __init__(self):
        self.widths = {}

    def set_width(self, node, fraction: float):
        self.widths[id(node)] = fraction

    def get_width(self, node) -> float:
        return self.widths.get(id(node), 1.0)

class BaseRenderVisitor:
    def __init__(self, context=None):
        self.output = []
        self.context = context or RenderContext()

    def get_result(self) -> str:
        return "".join(self.output)

    def visit(self, node: Node, context=None):
        method_name = f"visit_{type(node).__name__.lower()}"
        visitor_method = getattr(self, method_name, self.generic_visit)
        return visitor_method(node)

    def generic_visit(self, node: Node):
        if hasattr(node, "children") and isinstance(node.children, list):
            for child in node.children:
                self.visit(child)

    def visit_taskentity(self, node: TaskEntity):
        parent_span = int(node.config.get("col_span", 12))
        task_fraction = parent_span / 12.0
        self.context.set_width(node, task_fraction)

        self.emit_task_start(node, task_fraction)

        prompt_span = int(node.config.get("prompt_col_span", parent_span))
        prompt_fraction = (prompt_span / parent_span)
        self.emit_prompt(node, prompt_fraction)

        self.generic_visit(node)

        self.emit_task_end(node)

    def visit_subtaskentity(self, node: SubtaskEntity):
        width_fraction = self.context.get_width(node)
        self.emit_subtask(node, width_fraction)

    def emit_task_start(self, node: Node): pass
    def emit_prompt(self, node: Node, width_fraction: float): pass
    def emit_task_end(self, node: Node): pass
    def emit_subtask(self, node: Node, width_fraction: float): pass


