import os
from contextlib import contextmanager
from core.models import (
    Node,
    Grid,
    Cell,
    TaskEntity,
    SubtaskEntity,
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
        self.file_extension = "txt"
        self.indent_level = 0

    @contextmanager
    def indent(self):
        self.indent_level += 1
        try:
            yield
        finally:
            self.indent_level -= 1

    def emit_line(self, text: str):
        indentation = "  " * self.indent_level
        lines = text.splitlines(keepends=True)
        for line in lines:
            if line.strip():
                self.output.append(indentation + line)
            else:
                self.output.append(line)

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

    def write_to_dir(self, output_dir: str, filename_slug: str) -> str:
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        full_filename = f"{filename_slug}.{self.file_extension}"
        target_path = os.path.join(output_dir, "visitors/config/", full_filename)

        with open(target_path, "w", encoding="utf-8") as f:
            f.write(self.get_result())

        return target_path
