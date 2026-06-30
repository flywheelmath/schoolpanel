from core.models import (
    Node,
    Grid,
    Cell,
    TaskEntity,
    SubtaskEntity,
    TextEntity,
    GraphEntity,
    TableEntity
)

class ASTVisitor:
    def visit(self, node: Node):
        method_name = f'visit_{type(node).__name__.lower()}'
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node: Node):
        if hasattr(node, 'children') and isinstance(node.children, list):
            for child in node.children:
                self.visit(child)

        elif hasattr(node, 'content') and node.content:
            if not isinstance(node.content, list):
                self.visit(node.content)
