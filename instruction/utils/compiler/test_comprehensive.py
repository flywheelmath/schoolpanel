import uuid
from core.ast_models import TaskBlock, Subtask, CompositeBlock, GraphBlock

# Import your actual table parser and renderer
from plugins.tables.parser import parse_table
from plugins.tables.render_tex import render_tex as render_table_tex

# Assuming these are your graph endpoints based on our previous work
from plugins.graphs.compute import compute_graph
from plugins.graphs.render_tex import render_tex as render_graph_tex

def test_comprehensive_pipeline():
    print("1. Generating Nested Graph Block...")
    # Mocking the AST that your graph parser would generate
    graph_ast = GraphBlock(
        config={"xmin": -5, "xmax": 5, "ymin": -5, "ymax": 5, "scale": 0.5},
        plots=[
            {"original_expr": "y = 2x - 3"},
            {"original_expr": "y = -x + 3"}
        ]
    )
    # Run your compute and render pipeline for the graph
    compute_graph(graph_ast)
    graph_tex = render_graph_tex(graph_ast)

    print("2. Parsing and Generating Nested Table Block...")
    # Markdown payload for the table, complete with delta arrows!
    table_markdown = """
| x | f(x) = 2x - 3 | g(x) = -x + 3 |
|---|---------------|---------------|
| 1 | -1            | 2             |
| 2 [v: +1] | 1 [v: +2] | 1 [v: -1] |
| 3 [v: +1] | 3 [v: +2] | 0 [v: -1] |
"""
    table_ast = parse_table(table_markdown, "col_width=4em")
    table_tex = render_table_tex(table_ast)

    print("3. Assembling the AST Hierarchy (Composite -> Task -> Subtasks)...")
    
    # Embed the rendered components into Subtasks
    subtask_1 = Subtask(
        text="Graph the system of linear equations:",
        workspace=graph_tex
    )
    
    subtask_2 = Subtask(
        text="Verify the intersection point $(2, 1)$ using a table of values. Note the constant rates of change:",
        workspace=table_tex
    )

    task_block = TaskBlock(
        processed_subtasks=[subtask_1, subtask_2],
        subtask_counter_type="arabic"
    )

    composite_block = CompositeBlock(
        children=[task_block]
    )

    print("4. Rendering Final Document...")
    
    # Simulate the Layout Visitor rendering the TaskBlock
    # (Since we haven't explicitly coded visitors/layout.py together, we mock its output here)
    document_body = []
    document_body.append("\\section*{Composite Task: Systems of Equations}")
    document_body.append("\\begin{enumerate}[label=\\textbf{\\arabic*.}]")
    
    for st in task_block.processed_subtasks:
        document_body.append(f"  \\item {st.text}")
        document_body.append("  \\vspace{1em}")
        document_body.append(f"  {st.workspace}")
        document_body.append("  \\vspace{2em}")
        
    document_body.append("\\end{enumerate}")

    # 5. Wrap in the full LaTeX template
    body_content = "\n".join(document_body)
    full_document = f"""\\documentclass[letterpaper, 11pt]{{article}}

\\usepackage[margin=1in]{{geometry}}
\\usepackage{{amsmath}}
\\usepackage{{enumitem}}

% TikZ and all required libraries for BOTH graphs and tables
\\usepackage{{tikz}}
\\usepackage{{pgfplots}}
\\pgfplotsset{{compat=1.18}}
\\usetikzlibrary{{tikzmark}}
\\usetikzlibrary{{matrix}}
\\usetikzlibrary{{arrows.meta}}
\\usetikzlibrary{{patterns.meta}}

\\begin{{document}}

{body_content}

\\end{{document}}
"""

    with open("test_comprehensive_output.tex", "w") as f:
        f.write(full_document)

    print("\n✅ Successfully generated 'test_comprehensive_output.tex'.")
    print("⚠️  CRITICAL: Run `pdflatex test_comprehensive_output.tex` TWICE to resolve table anchors!")

if __name__ == "__main__":
    test_comprehensive_pipeline()
