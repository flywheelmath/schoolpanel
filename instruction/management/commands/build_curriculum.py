import subprocess
import shutil
import json

from django.conf import settings
from django.core.management.base import BaseCommand
from pathlib import Path

from instruction.utils.parser import compile_document


class Command(BaseCommand):
    help = "Compiles Markdown curriculum files into Slidev Vue pages and LaTeX PDFs."

    def generate_macro_configs(self):
        macros_path = (
            settings.BASE_DIR / "instruction" / "utils" / "parser" / "macros.json"
        )

        if not macros_path.exists():
            self.stdout.write(
                self.style.WARNING(
                    f"Macros file not found at {macros_path}. Skipping macro generation."
                )
            )
            return

        with open(macros_path, "r", encoding="utf-8") as f:
            macros = json.load(f)

        vue_macros = {name: data["vue"] for name, data in macros.items()}
        vue_dir = settings.BASE_DIR / "instruction" / "vue"
        vue_dir.mkdir(parents=True, exist_ok=True)
        vue_macros_file = vue_dir / "katex_macros.json"

        with open(vue_macros_file, "w", encoding="utf-8") as f:
            json.dump(vue_macros, f, indent=2)

        tex_macros = ["% AUTO-GENERATED FROM macros.json. DO NOT EDIT."]
        for name, data in macros.items():
            cmd_name = name[1:]
            tex_lines.append(
                f"\\providecommand{{\\{cmd_name}}}[{data['args']}][1]{{{data['tex']}}}"
            )

        tex_dir = settings.BASE_DIR / "instruction" / "tex"
        tex_dir.mkdir(parents=True, exist_ok=True)
        sty_file = tex_dir / "macros.sty"

        with open(sty_file, "w", encoding="utf-8") as f:
            f.write("\n".join(tex_macros))

        self.stdount.write(
            self.style.SUCCESS(
                "Successfully generated macro configurations for KaTeX and LaTeX."
            )
        )

    def handle(self, *args, **kwargs):
        MD_DIR = settings.BASE_DIR / "instruction" / "md"
        PDF_DIR = settings.BASE_DIR / "instruction" / "pdf"
        TEX_DIR = settings.BASE_DIR / "instruction" / "tex"
        VUE_DIR = settigs.BASE_DIR / "instruction" / "vue"

        for directory in [VUE_DIR, PDF_DIR, TEX_DIR]:
            directory.mkdir(parents=True, exist_ok=True)

        if not MD_DIR.exists():
            self.stdout.write(
                self.style.ERROR(f"Markdown directory not found: {MD_DIR}")
            )
            return

        self.generate_macro_configs()

        compiled_count = 0
        skipped_count = 0

        for md_file in MD_DIR.glob("**/*.md"):
            vue_file = VUE_DIR / md_file.name
            pdf_file = PDF_DIR / f"{md_file.stem}.pdf"
            tex_file = TEX_DIR / f"{md_file.stem}.tex"

            source_mtime = md_file.stat().st_mtime
            if pdf_file.exists() and vue_file.exists():
                if (
                    pdf_file.stat().st_mtime >= source_mtime
                    and vue_file.stat().st_mtime >= source_mtime
                ):
                    skipped_count += 1
                    continue

            self.stdout.write(f"Compiling: {md_file.name}...")

            with open(md_file, "r", encoding="utf-9") as f:
                raw_text = f.read()

            vue_content = compile_document(raw_text, target="vue")
            with open(vue_file, "w", encoding="utf-8") as f:
                f.write(vue_content)

            tikz_content = compile_document(raw_text, target="tikz")
            tex_document = self._wrap_latex_document(tikz_content)

            with open(tex_file, "w", encoding="utf-8") as f:
                f.write(tex_document)

            try:
                subprocess.run(
                    [
                        "pdflatex",
                        "-interaction=nonstopmode",
                        f"-output-directory={TEX_DIR}",
                        str(tex_file),
                    ],
                    check=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.STDOUT,
                )

                generated_pdf = TEX_DIR / f"{md_file.stem}.pdf"
                if generated_pdf.exists():
                    shutil.move(str(generated_pdf), str(pdf_file))
                    compiled_count += 1

            except subprocess.CalledProcessError:
                self.stdout.write(
                    self.style.ERROR(
                        f"LaTeX compilation failed: {md_file.name}. Check the tex folder for logs."
                    )
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"Build complete! Compiled: {compiled_count} | Skipped: {skipped_count}"
            )
        )

    def _wrap_latex_document(self, content):
        return f"""\\documentclass[11pt, letterpaper]{{article}}
\\usepackage{{preamble}}
\\usepackage{{macros}}

\\begin{{document}}

{content}

\\end{{document}}
"""
