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

class BaseGridRenderStrategy:
    def render(self, node: Grid, visitor: 'RenderTeXVisitor'):
        raise NotImplementedError("Grid layout strategies must implement render()")

class DualHeightRowsGridStrategy(BaseGridRenderStrategy):
    def render(self, node: Grid, visitor: 'RenderTeXVisitor'):
        out = visitor.output
        out.append("% --- Begin Tree-Partition Lookahead Grid ---\n")

        cells = [child for child in node.children if isinstance(child, Cell)]

        while cells:
            current_line_cells = []
            accumulated_cols = 0

            while cells and accumulated_cols < 12:
                next_c = cells[0]
                col_span = int(next_c.config.get("col_span", 1))
                if accumulated_cols + col_span <= 12:
                    current_line_cells.append(cells.pop(0))
                    accumulated_cols += col_span
                else:
                    break

            if not current_line_cells: break

            best_split = 0
            min_variance = float('inf')

            def get_max_span(subset):
                return max([int(c.config.get("row_span", 1)) for c in subset]) if subset else 0

            for i in range(len(current_line_cells) + 1):
                left_max = get_max_span(current_line_cells[:i])
                right_max = get_max_span(current_line_cells[i:])

                variance = abs(left_max - right_max)
                if variance < min_variance:
                    min_variance = variance
                    best_split = i

            left_partition = current_line_cells[:best_split]
            right_partition = current_line_cells[best_split:]

            left_max = get_max_span(left_partition)
            right_max = get_max_span(right_partition)

            left_width_cols = sum(int(c.config.get("col_span", 1)) for c in left_partition)
            right_width_cols = sum(int(c.config.get("col_span", 1)) for c in right_partition)

            left_width_fraction = max((left_width_cols / 12.0) - 0.02, 0)
            right_width_fraction = max((right_width_cols / 12.0) - 0.02, 0)

            out.append("\\noindent\n")

            if left_max == right_max or len(left_partition) == 0 or len(right_partition) == 0:
                for cell in current_line_cells:
                    span = int(cell.config.get("col_span", 1))
                    width_fraction = max((span / 12.0) - 0.02, 0)
                    out.append(f"\\begin{{minipage}}[t]{{{width_fraction:.4f}\\textwidth}}\n")
                    visitor.generic_visit(cell)
                    out.append("\n\\end{minipage}\\hfill\n")
            else:
                is_left_taller = left_max > right_max
                taller_partition = left_partition if is_left_taller else right_partition
                shorter_partition = right_partition if is_left_taller else left_partition

                taller_max = max(left_max, right_max)
                shorter_max = min(left_max, right_max)
                shorter_width_cols = right_width_cols if is_left_taller else left_width_cols

                taller_width_fraction = left_width_fraction if is_left_taller else right_width_fraction
                out.append(f"\\begin{{minipage}}[t]{{{taller_width_fraction:.4f}\\textwidth}}\n")
                for cell in taller_partition:
                    span = int(cell.config.get("col_span", 1))
                    parent_width = sum(int(x.config.get("col_span", 1)) for x in taller_partition)
                    inner_width = span / parent_width
                    out.append(f"\\begin{{minipage}}[t]{{{inner_width:.4f}\\linewidth}}\n")
                    visitor.generic_visit(cell)
                    out.append("\n\end{minipage}\\hfill\n")
                out.append("\\end{minipage}\\hfill\n")

                smaller_width_fraction = right_width_fraction if is_left_taller else left_width_fraction
                out.append(f"\\begin{{minipage}}[t]{{{smaller_width_fraction:.4f}\\textwidth}}\n")
                out.append("\\begin{minipage}[t]{\\linewidth}\n")
                for cell in shorter_partition:
                    span = int(cell.config.get("col_span", 1))
                    inner_width = span / shorter_width_cols if shorter_width_cols > 0 else 1.0
                    out.append(f"\\begin{{minipage}}[t]{{{inner_width:.4f}\\linewidth}}\n")
                    visitor.generic_visit(cell)
                    out.append("\n\\end{minipage}\\hfill\n")
                out.append("\\end{minipage}\\par\\vspace{1.5ex}\n")

                remaining_space = taller_max - shorter_max

                while remaining_space > 0 and cells:
                    next_cell = cells[0]
                    next_span = int(next_cell.config.get("col_span", 1))
                    next_row_span = int(next_cell.config.get("row_span", 1))

                    if next_span <= shorter_width_cols:
                        if next_row_span <= remaining_space + 1:
                            cells.pop(0)
                            out.append("\\begin{minipage}[t]{\\linewidth}\n")
                            inner_width = next_span / shorter_width_cols if shorter_width_cols > 0 else 1.0
                            out.append(f"\\begin{{minipage}}[t]{{{inner_width:.4f}\\linewidth}}\n")
                            visitor.generic_visit(next_cell)
                            out.append("\n\\end{minipage}\\hfill\n")
                            out.append("\\end{minipage}\\par\\vspace{1.5ex}\n")

                            if next_row_span == remaining_space + 1:
                                remaining_space = 0
                            else:
                                remaining_space -= next_row_span
                        else:
                            break
                    else:
                        break
                    
                out.append("\\end{minipage}\n")

            out.append("\n\\par\\vspace{2.5ex}\\noindent\n")

        out.append("% --- End Tree-Partition Lookahead Grid ---\n")

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
    def __init__(self, grid_strategy: BaseGridRenderStrategy = None):
        self.output = []
        self.grid_strategy = grid_strategy or DualHeightRowsGridStrategy()

    def get_result(self) -> str:
        return "".join(self.output)

    def visit_grid(self, node: Grid):
        self.grid_strategy.render(node, self)

    def visit_cell(self, node: Cell):
        width = getattr(node, "width_fraction", 0.98)
        self.output.append(f"\\begin{{minipage}}[t]{{{width:.4f}\\textwidth}}\n")
        self.generic_visit(node)
        self.output.append(r"\end{minipage}")
    
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

