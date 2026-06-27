from base import BaseVisitor
from core.ast_models import GraphBlock
from plugins.graphs.compute import compute_graph

SAMPLES_COUNT = 501

class ComputationVisitor(BaseVisitor):
    def generic_visit(self, node):
        pass

    def visit_graphblock(self, block: GraphBlock):
        compute_graph(block)
