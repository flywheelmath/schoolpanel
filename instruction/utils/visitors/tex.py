import re
from .base import ASTVisitor
from core.models import (
    Cell,
    Grid,
    GraphEntity,
    SubtaskEntity,
    TableEntity,
    TaskEntity,
    TextEntity,
)

class LayoutGridTracker:
    def __init__(self, total_cols=12):
        self.total_cols = total_cols
        self.matrix = []

    def _ensure_row_exists(self, row_idx):
        while len(self.matrix) <= row_idx:
            self.matrix.append([False] * self.total_cols)

    def find_next_available_slot(self):
        row_idx = 0
        while True:
            self._ensure_row_exists(row_idx)
            for col_idx in range(self.total_cols):
                if not self.matrix[row_idx][col_idx]:
                    return row_idx, col_idx
            row_idx += 1

    def occupy_space(self, start_row, start_col, row_span, col_span):
        for r in range(start_row, start_row + row_span):
            self._ensure_row_exists(r)
            for c in range(start_col, start_col + col_span):
                if c < self.total_cols:
                    self.matrix[r][c] = True

def process_tex_text(content: str) -> str:
    parts = re.split(r'(\\\[.*?\\\]|\\\(.*?\\\))', content, flags=re.DOTALL)

    # Special LaTeX characters

    for i in range(len(parts)):
        if i % 2 == 0:
            text = parts[i]
            if not text: continue

            text = re.sub(r'</?v-click>', '', text)
            text = re.sub(r'(?m)^---\s*$', r'\n\n', text)

            code_blocks = []
            def shield_code(match):
                code_blocks.append(match.group(1))
                return f"CODEPLACEHOLDER{len(code_blocks)-1}"
            text = re.sub(r'`([^`]+)`', shield_code, text)

            text = text.replace('\\', '\\textbackslash ')
            text = re.sub(r'([&%$_{}])', r'\\\1', text)

            text = re.sub(r'\*\*(.*?)\*\*', r'\\textbf{\1}', text)
            text = re.sub(r'\*(.*?)\*', r'\\textit{\1}', text)
            text = re.sub(r'==(.*?)==', r'\\colorbox{red}{\1}', text)

            text = re.sub(r'(?m)^###\s+(.*)$', r'\\subsubsection*{\1}', text)
            text = re.sub(r'(?m)^##\s+(.*)$', r'\\subsection*{\1}', text)
            text = re.sub(r'(?m)^#\s+(.*)$', r'\\section*{\1}', text)


            text = re.sub(r'(#)', r'\\\1', text)
            text = text.replace('~', '\\textasciitilde{}')
            text = text.replace('^', '\\textasciicircum{}')

            def handle_markdown_links(match):
                display_text = match.group(1)
                address_target = match.group(2)
                clean_address = address_target.replace('\\', '')
                return f"\\href{{{clean_address}}}{{{display_text}}}"

            text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', handle_markdown_links, text)

            def handle_bare_url(match):
                target = match.group(1)
                clean_target = target.replace('\\', '')
                return f"\\url{{{clean_target}}}"

            text = re.sub(r'(?m)(?<!\{)(https?://[^\s<]+)', handle_bare_url, text)

            text = re.sub(r'"([^"]*)"', r"``\1''", text)
            text = text.replace('--', '---')
            text = text.replace('[Blank]', r'\blank')

            for idx, raw_code in enumerate(code_blocks):
                escaped_code = (raw_code.replace('&', '\\&')
                                        .replace('%', '\\%')
                                        .replace('$', '\\$')
                                        .replace('_', '\\_')
                                        .replace('#', '\\#')
                                        .replace('{', '\\{')
                                        .replace('}', '\\}'))
                text = text.replace(f"CODEPLACEHOLDER{idx}", f"\\texttt{{{escaped_code}}}")

            parts[i] = text

    assembled = "".join(parts)

    # Markdown lists

    lines = assembled.split('\n')
    in_bullet_list = False
    in_num_list = False
    in_blockquote = False
    out_lines = []

    for line in lines:
        stripped = line.strip()

        if not stripped:
            if in_bullet_list:
                out_lines.append(r'\end{itemize}')
                in_bullet_list = False
            if in_num_list:
                out_lines.append(r'\end{enumerate}')
                in_num_list = False
            if in_blockquote:
                out_lines.append(r'\end{quote}')
                in_blockquote = False
            out_lines.append(line)
            continue

        is_bullet_trigger = bool(re.match(r'^\s*[-*]\s+', line))
        is_num_trigger = bool(re.match(r'^\s*\d+\.\s+', line))
        is_quote_trigger = bool(re.match(r'^\s*>\s*', line))

        if is_bullet_trigger or is_num_trigger or is_quote_trigger:
            if in_blockquote and not is_quote_trigger:
                out_lines.append(r'\end{quote}')
                in_blockquote = False

        if is_quote_trigger:
            if in_bullet_list:
                out_lines.append(r'\end{itemize}')
                in_bullet_list = False
            if in_num_list:
                out_lines.append(r'\end{enumerate}')
                in_num_list = False
            if not in_blockquote:
                out_lines.append(r'\begin{quote}')
                in_blockquote = True

            clean_quote_line = re.sub(r'^\s*>\s*', '', line)
            out_lines.append(f"  {clean_quote_line}")

        elif is_bullet_trigger:
            if in_num_list:
                out_lines.append(r'\end{enumerate}')
                in_num_list = False
            if not in_bullet_list:
                out_lines.append(r'\begin{itemize}')
                in_bullet_list = True
            item_text = re.sub(r'^\s*[-*]\s+(.*)', r'  \\item \1', line)
            out_lines.append(item_text)

        elif is_num_trigger:
            if in_bullet_list:
                out_lines.append(r'\end{itemize}')
                in_bullet_list = False
            if not in_num_list:
                out_lines.append(r'\begin{enumerate}')
                in_num_list = True
            item_text = re.sub(r'^\s*\d+\.\s+(.*)', r'  \\item \1', line)
            out_lines.append(item_text)

        elif in_blockquote:
            out_lines.append(f"  {line.strip()}")

        elif in_bullet_list or in_num_list:
            out_lines.append(f"    {line.strip()}")

        else:
            out_lines.append(line)

    if in_bullet_list:
        out_lines.append(r'\end{itemize}')
    if in_num_list:
        out_lines.append(r'\end{enumerate}')
    if in_blockquote:
        out_lines.append(r'\end{quote}')

    return "\n".join(out_lines)

class RenderTeXVisitor(ASTVisitor):
    def __init__(self):
        self.output = []
        self.grid_tracker = None

    def get_result(self) -> str:
        return "".join(self.output)

    def visit_grid(self, node: Grid):
        self.output.append("% --- Start Grid ---\n")
        old_tracker = getattr(self, "grid_tracker", None)
        self.grid_tracker = LayoutGridTracker(total_cols=12)

        for child in node.children:
            self.visit(child)

        self.grid_tracker = old_tracker
        self.output.append("% --- End Grid ---\n")

    def visit_cell(self, node: Cell):
        if not getattr(self, "grid_tracker", None):
            self.output.append("\\noindent\n\\begin{minipage}{\\linewidth}\n")
            self.generic_visit(node)
            self.output.append("\\end{minipage}\n")
            return

        col_span = int(node.config.get("col_span", 1))
        row_span = int(node.config.get("row_span", 1))

        start_row, start_col = self.grid_tracker.find_next_available_slot()
        self.grid_tracker.occupy_space(start_row, start_col, row_span, col_span)

        width_fraction = (col_span / 12.0) - 0.025
        if width_fraction <= 0:
            width_fraction = 0.95

        if start_col == 0 and start_row > 0:
            self.output.append("\\par\\vspace{1.5ex}\\noindent\n")

        self.output.append(f"\\begin{{minipage}}[t]{{{width_fraction:.4f}\\textwidth}}\n")
        self.generic_visit(node)
        self.output.append("\\end{minipage}\n")

    def visit_textentity(self, node: TextEntity):
        clean_tex = process_tex_text(node.content)
        self.output.append(clean_tex + "\n")

    def visit_taskentity(self, node: TaskEntity):
        self.output.append(f"\n\\begin{{task}}{{{node.label}}}")
        self.output.append(node.content + "\n")
        self.generic_visit(node)
        self.output.append("\\end{task}\n")

    def visit_subtaskentity(self, node: SubtaskEntity):
        self.output.append(f"\\begin{{subtask}}{{{node.label}}}")
        self.output.append(node.content)
        self.generic_visit(node)
        self.output.append("\\end{subtask}")

    def visit_graphentity(self, node: GraphEntity):
        self.output.append(r"% --- Start graph ---")
        self.output.append(node.raw_body)
        self.output.append(r"% --- End graph ---")

    def visit_tableentity(self, node: TableEntity):
        self.output.append(r"% --- Start table ---")
        self.output.append(node.raw_body)
        self.output.append(r"% --- End table ---")

