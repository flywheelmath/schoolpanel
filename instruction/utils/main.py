import os
import sys

from core.parser import Parser, Tokenizer
from visitors.vue import RenderVueVisitor
from visitors.tex import RenderTeXVisitor


def compile_custom_markdown(input_filepath: str, output_dir: str, filename_slug: str):
    if not os.path.exists(input_filepath):
        print(f"[ERROR] Source file not found at: {input_filepath}")
        sys.exit(1)

    with open(input_filepath, "r", encoding="utf-8") as f:
        raw_markdown = f.read()

    print(f"[SSG] Parsing source document: {input_filepath}...")

    tokens = Tokenizer(raw_markdown).tokenize()
    parser = Parser(tokens)
    ast_nodes = parser.parse()

    print("[SSG] Executing Vue rendering pass...")
    vue_visitor = RenderVueVisitor()
    vue_visitor.output.append("---\ntheme: default\nmdc: true\n---\n\n")

    for node in ast_nodes:
        vue_visitor.visit(node)
    vue_path = vue_visitor.write_to_dir(output_dir, filename_slug)

    print("[SSG] Executing TeX rendering pass...")
    tex_visitor = RenderTeXVisitor()

    for node in ast_nodes:
        tex_visitor.visit(node)
    tex_path = tex_visitor.write_to_dir(output_dir, filename_slug)

    print("\n[SSG SUCCESS] Compilation complete:")
    print(f"Vue path: {vue_path}")
    print(f"TeX path: {tex_path}")


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print(
            "Usage: python main.py [input_file.md] [output_directory] [filename_slug]"
        )
        sys.exit(1)

    compile_custom_markdown(
        input_filepath=sys.argv[1], output_dir=sys.argv[2], filename_slug=sys.argv[3]
    )
