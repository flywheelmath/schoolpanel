from core.ast_models import TaskBlock
from visitors.base import BaseVisitor

class RenderTexVisitor(BaseVisitor):
    output = []

    cols = block.config.get("cols_tex", 4)
    col_width = block.config.get("col_width_tex", f"\\textwidth/{cols}")

    for sub in block.processed_subtasks:
        if sub.col_tex == 0 and output:
            output.append(f"\\vspace{{{block.config.get('workspace', '3cm')}}} \\\\")

        output.append(f"\\begin{{minipage}}[t]{{{col_width}}}")
        output.append(f"\\textbf{{{sub.label}}} {sub.text}")
        output.append("\\end{minipage}")

        if sub.col_tex < cols - 1:
            output.append("\\hfill")

    output.append(f"\\vspace{{{block.config.get('workspace', '3cm')}}}")
    return "\n".join(output) + "\n\\vspace{1em}"
