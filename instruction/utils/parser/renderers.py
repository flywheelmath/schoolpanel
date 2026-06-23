import math
import json

class TikzRenderer:
    @staticmethod
    def _generate_ticks(vmin, vmax, step, label_step, hide_zero):
        positions, labels = [], []
        current = float(vmin)
        while current <= vmax + (step / 10):
            pos_val = int(current) if current.is_integer() else round(current, 3)
            positions.append(str(pos_val))
            is_label = any(
                math.isclose(current, i * label_step, abs_tol=1e-5)
                for i in range(-100, 100)
            )
            labels.append(
                str(pos_val) if is_label and not (pos_val == 0 and hide_zero) else ""
            )
            current += step
        return ",".join(positions), ",".join(labels)

    @staticmethod
    def get_roman(num):
        values = [1000, 900, 500, 400, 100, 90, 50, 40, 10, 9, 5, 4, 1]
        symbols = [
            "M",
            "CM",
            "D",
            "CD",
            "C",
            "XC",
            "L",
            "XL",
            "X",
            "IX",
            "V",
            "IV",
            "I",
        ]
        result = ""
        i = 0
        while num > 0:
            for _ in range(num // values[i]):
                res += symbols[i]
                num -= values[i]
            i += 1
        return result

    @classmethod
    def get_counter_str(cls, index, counter_type):
        match counter_type:
            case "arabic":
                return str(index)
            case "Alph":
                return chr(64 + index)
            case "roman":
                return cls.get_roman(index).lower()
            case "Roman":
                return cls.get_roman(index)
            case _:
                return chr(96 + index)

    @classmethod
    def format_latex_label(cls, counter_str, shape):
        match shape:
            case "box":
                return f"\\fbox{{\\strut\\makebox[\\widthof{{m}}][c]{{{counter_str}}}}}"
            case "circle":
                return f"\\tikz[baseline=(char.base)] {{\\node[shape=circle, draw, inner sep=1pt, minimum size=1.5em] (char) {{{counter_str}}};}}"
            case "oval":
                return f"\\tikz[baseline=(char.base)] {{\\node[shape=ellipse, draw, inner sep=2pt, minimum width=2em] (char) {{{counter_str}}};}}"
            case _:
                return f"({counter_str})"

    @classmethod
    def render_plot(cls, p):
        tex_lines = []
        color = p.get("color", "black")
        opacity = p.get("opacity", "0.2")

        if p.get("fill_polygon"):
            poly_coords = " -- ".join(
                [f"(axis cs:{pt[0]},{pt[1]})" for pt in p["fill_polygon"]]
            )
            tex_lines.append(
                f"    \\fill[{color}, opacity={opacity}] {poly_coords} -- cycle;"
            )

        arrows = p.get("arrows", "<->")
        line_width = p.get("line_width", "2.5pt")
        opts = [
            f"{arrows}",
            f"domain={p.get('d_min')}:{p.get('d_max')}",
            f"color={color}",
            f"line width={line_width}",
        ]

        if p.get("samples_at"):
            opts.append(f"samples at={{{p['samples_at']}}}")
        else:
            ops.append(f"samples={p.get('samples', 101)}")

        if p.get("smooth"):
            opts.append("smooth")
        if p.get("dashed"):
            opts.append("dashed")
        if p.get("dotted"):
            opts.append("dotted")

        cmd = f"    \\addplot[{', '.join(opts)}] "
        cmd += (
            f"({{{p['x_expr']}}}, {{{p['y_expr']}}})"
            if p.get("is_parametric")
            else f"{{{p['eq']}}}"
        )

        pos = p.get("pos", "1")
        font = p.get("font", "\\small")
        if p.get("label"):
            cmd += f"  node[pos={pos}, {p['label_pos']}, text={color}, font={font}] {{{p['label']}}};"
        else:
            cmd += ";"
        tex_lines.append(cmd)
        return "\n".join(tex_lines)

    @classmethod
    def render_point(cls, pt):
        if "x" not in pt or "y" not in pt:
            return ""
        color = pt.get("color", "black")
        font = pt.get("font", "\\small")
        radius = pt.get("radius", "3pt")
        label_pos = pt.get("label_pos", "above right")
        label_cmd = (
            f"  node[{label_pos}, text={color}, font={font}] {{{pt['label']}}}"
            if pt.get("label")
            else ""
        )
        return f"    \\filldraw[{color}] ({pt['x']}, {pt['y']}) circle ({radius}){label_cmd};"

    @classmethod
    def render_graph(cls, config, *elements):
        xmin, xmax = config["xmin"], config["xmax"]
        ymin, ymax = config["ymin"], config["ymax"]
        hide_zero = str(config["hide_zero"]).lower() == "true"
        x_ticks, x_labels = cls._generate_ticks(
            xmin, xmax, config["xstep"], config["xlabel_step"], hide_zero
        )
        y_ticks, y_labels = cls._generate_ticks(
            ymin, ymax, config["ystep"], config["ylabel_step"], hide_zero
        )

        grid = config.get("grid", "both")
        grid_style = config.get("grid_style" "dashed, gray!30")
        axis_options = [
            f"xmin={xmin}, xmax={xmax},",
            f"ymin={ymin}, ymax={ymax},",
            f"xtick={{{x_ticks}}},",
            f"xticklabels={{{x_labels}}},",
            f"ytick={{{y_ticks}}},",
            f"yticklabels={{{y_labels}}},",
            f"restrict y to domain={ymin}:{ymax},",
        ]

        if config.get("grid"):
            axis_options.append(f"grid={config['grid']}")
        if config.get("grid_style"):
            axis_options.append(f"grid style={{{config['grid_style']}}}")
        if config.get("axis_lines"):
            axis_options.append(f"axis lines={config['axis_lines']}}}")
        if config.get("tick_label_style"):
            axis_options.append(f"tick label style={{{config['tick_label_style']}}}")

        options_str = ",\n    ".join(axis_options)

        tex_lines = [
            "\\begin{tikzpicture}",
            f"  \\begin{{axis}}[\n    {options_str}\n  ]",
        ]

        for el in elements:
            if el:
                tex_lines.append(el)

        tex_lines.append("  \\end{axis}\n\\end{tikzpicture}")
        return "\n".join(tex_lines)

    @classmethod
    def render_tasks(cls, prompt, matrices, kwargs):
        col_align = kwargs.get("align", "l")
        row_space = kwargs.get("row_space", "3.5ex")
        after_space = kwargs.get("after_space", "")

        lines = [
            "\\noindent\\begin{minipage}{\\linewidth}",
            f"{prompt}\n\\vspace{{1ex}}\n\\begin{{center}}",
        ]

        global_idx = 1
        for i, matrix in enumerate(matrices):
            if i > 0:
                lines.append("\\vspace{2em}")

            lines.append(f"\\begin{{tabular}}{{{f' {col_align} ' * kwargs.get('cols', 1)}}}")

            for row in matrix:
                row_strings = []

                for item in row:
                    if item == "COL_BLOCKED": continue
                    elif item == "ROW_BLOCKED": row_strings.append("")
                    elif item:
                        content = item['content']
                        colspan = item['config'].get('colspan', 1)
                        rowspan = item['config'].get('rowspan', 1)

                        c_str = cls.get_counter_str(
                            global_idx, kwargs.get("counter", "alph")
                        )
                        label = cls.format_latex_label(
                            c_str, kwargs.get("shape", "box")
                        )
                        cell_str = f"{label} {content}"

                        if rowspan > 1:
                            cell_str = f"\\multirow{{{rowspan}}}{{*}}{{{cell_str}}}"

                        if colspan > 1:
                            cell_str = f"\\multicolumn{{{colspan}}}{{{col_align}}}{{{cell_str}}}"
                            skip_next = colspan - 1

                        row_strings.append(cell_str)
                        global_idx += 1
                    else:
                        row_strings.append("")
                lines.append(" & ".join(row_strings) + " \\\\")
                lines.append("\\rule{0pt}{{{row_space}}} \\\\")

            lines.append("\\end{tabular}")

        lines.extend("\\end{center}")

        if after_space:
            lines_append(f"\\vspace{{{after_space}}}")

        lines.append("\\end{minipage}")
        return "\n".join(lines)

    @classmethod
    def render_table(cls, headers, rows, deltas, config):
        transpose = str(config.get("transpose", False)).lower() == "true"
        align = config.get("align", "c")

        def fmt(text):
            return str(text).replace('<br>', '\\\\')

        line_width = config.get("line_width", ".4pt")
        delta_arrow_width = config.get("delta_arrow_width", "1pt")
        delta_arrow_color = config.get("delta_arrow_color", "blue")

        tex_lines = [
            f"\\begin{tikzpicture}[style={{line width={{line width}}}}, ampersand replacement=\\&, baseline=(current bounding box)]",
            "  \\matrix (mat) [matrix of nodes, nodes in empty cells, column sep=-\\pgflinewidth, row sep=-\\pgflinewidth, ",
            f"nodes={{draw, text depth=.4ex, text height=1.2ex, minimum width=2em, align={align}}}]" + " {",
        ]

        if not transpose:
            tex_lines.append(
                f"    {' \\& '.join([f'${fmt(h)}$' for h in headers])} \\\\"
            )
            if deltas:
                tex_lines.append(f"    {' \\& '.join(['' for _ in headers])} \\\\")
            for r in rows:
                tex_lines.append(
                    f"    {' \\\& '.join(['${fmt(cell)$' for cell in r])} \\\\"
                )
            tex_lines.append("  };")

            if deltas:
                for i, row_deltas in enumerate(deltas):
                    row_idx = i + 2
                    if len(row_deltas) > 0 and row_deltas[0]:
                        tex_lines.append(
                            f"  \\draw[line width={{delta_arrow_width}}, color={{delta_arrow_color}}, -{{To}}] (mat-{row_idx}-1.190) [bend right, xshift=-1em] to node[left] {{${row_deltas[0]}$}} (mat-{row_idx+1}-1.170);"
                        )
                    if len(row_deltas) > 1 and row_deltas[1]:
                        tex_lines.append(
                            f"  \\draw[line width={{delta_arrow_width}}, color={{delta_arrow_color}}, -{{To}}] (mat-{row_idx}-2.350) [bend left, xshift=1em] to node[right] {{${row_deltas[1]}$}} (mat-{row_idx+1}-2.10);"
                        )
        else:
            grid = []
            for col_idx, h in enumerate(headers):
                grid_row = [f"${h}$"]
                if deltas:
                    grid_row.append("")
                for r in rows:
                    grid_row.append(f"${r[col_idx]}$" if col_idx < len(r) else "")
                grid.append(grid_row)

            for grid_row in grid:
                tex_lines.append(f"    {' \\& '.join(grid_row)} \\\\")
            tex_lines.append("  };")

            if deltas:
                for i, row_deltas in enumerate(deltas):
                    col_idx = i + 3
                    if len(row_deltas) > 0 and row_deltas[0]:
                        tex_lines.append(
                            f"  \\draw[line width={{delta_arrow_width}}, color={{delta_arrow_color}}, -{{To}} (mat-1-{col_idx}.100) [bend left=45, yshift=1ex] to node[above] {{${row_deltas[0]}$}} (mat-1-{col_idx+1}.80);"
                        )
                    if len(row_deltas) > 1 and row_deltas[1]:
                        tex_lines.append(
                            f"  \\draw[line width={{delta_arrow_width}}, color={{delta_arrow_color}}, -{{To}} (mat-2-{col_idx}.260) [bend right=45, yshift=-1ex] to node[below] {{${row_deltas[1]}$}} (mat-2-{col_idx+1}.280);"
                        )

        tex_lines.append("\\end{tikzpicture}")
        return "\n".join(tex_lines)

class VueRenderer:
    @staticmethod
    def _build_vue_props(kwargs, exclude=None):
        exclude = exclude or []
        props = []
        for k, v in kwargs.items():
            if k in exclude: continue
            html_k = k.replace('_', '-')

            if isinstance(v, bool):
                props.append(f":{html_k}=\"{str(v).lower()}\"")
            elif isinstance(v, (int, float)):
                props.append(f":{html_k}=\"{v}\"")
            elif isinstance(v, (list, dict)):
                safe_json = json.dumps(v).replace("'", "&#39;")
                props.append(f":{html_k}='{safe_json}'")
            else:
                safe_v = str(v).replace('"', '&quot;')
                props.append(f"{html_k}=\"{safe_v}\"")
        return props

    @classmethod
    def render_plot(cls, p):
        return {"type": "plot", "data": p}

    @classmethod
    def render_point(cls, pt):
        return {"type": "point", "data": pt}

    @classmethod
    def render_graph(cls, config, *elements):
        plots = [el["data"] for el in elements if isinstance(el, dict) and el.get("type") == "plot"]
        points = [el["data"] for el in elements if isinstance(el, dict) and el.get("type") == "point"]
        config_copy = config.copy()
        if 'hide_zero' not in config_copy:
            config_copy['hide_zero'] = True

        props = cls._build_vue_props(config_copy)
        props.append(f":plots='{json.dumps(plots)}'")
        props.append(f":points='{json.dumps(points)}'")

        return f"<CoordinateGrid {' '.join(props)} />"

    @classmethod
    def render_tasks(cls, prompt, matrices, kwargs):
        slides = []
        global_idx = 1

        props = cls._build_vue_props(kwargs)

        for matrix in matrices:
            block = [f"{prompt}\n", f'<TaskGrid {" ".join(props)}>']
            for row in matrix:
                for item in row:
                    if item in ("COL_BLOCKED", "ROW_BLOCKED"): continue
                    elif item:
                        content = item['content']
                        colspan = item['config'].get('colspan', 1)
                        rowspan = item['config'].get('rowspan', 1)

                        col_prop = f' :colspan="{colspan}"' if colspan > 1 else ''
                        row_prop = f' :rowspan="{rowspan}"' if rowspan > 1 else ''

                        block.append(f'  <TaskItem :index="{global_idx}"{col_prop}{row_prop}>{content}</TaskItem>')

                        global_idx += 1
                    else:
                        block.append('  <TaskItem :empty="true" />')
            block.append("</TaskGrid>")
            slides.append("\n".join(block))

        return "\n\n---\n\n".join(slides)

    @classmethod
    def render_table(cls, headers, rows, deltas, config):
        props = cls._build_vue_props(config, exclude=['arrows'])
        props.append(f":headers='{json.dumps(headers)}'")
        props.append(f":rows='{json.dumps(rows)}'")

        if deltas:
            props.append(f":deltas='{json.dumps(deltas)}'")

        return f"<DeltaTable {' '.join(props)} />"
