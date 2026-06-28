from plugins.tables.parser import parse_table
from plugins.tables.render_tex import render_tex

def test_pipeline():
    # Markdown payload showcasing the new multi-span syntax!
    markdown_payload = """
| x | f(x) |
|---|------|
| 1 | 3.5  |
| 2 [v: +1] | 7.0 [v: +3.5] |
| 3 [v,2: +2] | 10.5 [v,2: +7] [h,1: \\times 3.5] |
"""
    config_string = "col_width=3em"

    print("Parsing Markdown...")
    ast = parse_table(markdown_payload, config_string)
    
    print("\nRendering to LaTeX...")
    tex_output = render_tex(ast)

    full_document = f"""\\documentclass[letterpaper, 11pt]{{article}}
\\usepackage[margin=1in]{{geometry}}
\\usepackage{{amsmath}}
\\usepackage{{tikz}}
\\usetikzlibrary{{tikzmark}}
\\usetikzlibrary{{matrix}}
\\usetikzlibrary{{arrows.meta}}

\\begin{{document}}
\\section*{{Multi-Span Delta Test}}
\\vspace{{2em}}

{tex_output}

\\end{{document}}
"""

    with open("test_output_table.tex", "w") as f:
        f.write(full_document)

    print("\nSuccessfully generated 'test_output_table.tex'.")
    print("Run: pdflatex test_output_table.tex")

if __name__ == "__main__":
    test_pipeline()
