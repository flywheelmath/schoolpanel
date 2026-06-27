from abc import ABC, abstractmethod

class BaseVisitor:
    @abstractmethod
    def visit(self, node):
        if isinstance(node, list):
            for n in node:
                self.visit(n)
        elif hasattr(node, 'children'):
            for child in node.children:
                self.visit(child)
        else:
            method_name = f"visit_{type(node).__name__.lower()}"
            visitor_method = getattr(self, method_name, self.generic_visit)
            visitor_method(node)

    @abstractmethod
    def generic_visit(self, node):
        pass
