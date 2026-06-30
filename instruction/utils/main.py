from visitors.layout import LayoutVisitor
from visitors.tex import RenderTexVisitor

layout_engine = LayoutVisitor()
for node in ast:
    layout_engine.visit(node)

tex_engine = RenderTexVisitor()
for node in ast:
    tex_engine.visit(node)

print(tex_engine.get_result())
