from .base import BaseVisitor
from plugins.graphs.render_tex import render_tex as render_graph
#from plugins.tables.render_tex import render_tex as render_table
from plugins.tasks.render_tex import render_tex as render_task

class RenderTexVisitor(BaseVisitor):
    def __init__(self):
        self.output = []

    def visit_taskblock(self, node):
        self.output.append(render_task(node))

    def visit_graphblock(self, node):
        self.output.append(render_graph(node))

    def visit_tableblock(self, node):
        self.output.append(render_table(node))

    def get_result(self):
        return "\n".join(self.output)
