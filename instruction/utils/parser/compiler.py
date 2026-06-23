import re
import math

from .lexer import Lexer
from .math_engine import MathEngine
from .renderers import TikzRenderer, VueRenderer


def compile_document(raw_text, target="vue"):
    def graph_replacer(match):
        config_str, content_str = Lexer.split_config_block(match.group(1))
        config = Lexer.parse_graph_config(
            config_str,
            {
                "xmin": -10,
                "xmax": 10,
                "ymin": -10,
                "ymax": 10,
                "xstep": 1,
                "ystep": 1,
                "xlabel_step": 2,
                "ylabel_step": 2,
                "hide_zero": True,
            },
        )
        raw_plots = [
            Lexer.parse_kwargs(m.group(1))
            | {"eq": Lexer.extract_positional_eq(m.group(1))}
            for m in re.finditer(r"plot\((.*?)\)", content_str)
        ]
        raw_points = [
            Lexer.parse_kwargs(m.group(1))
            | {
                "x": Lexer.extract_positional_coords(m.group(1))[0],
                "y": Lexer.extract_positional_coords(m.group(1))[1],
            }
            for m in re.finditer(r"point\((.*?)\)", content_str)
        ]

        plots = MathEngine.enrich_plots(raw_plots, config)
        points = MathEngine.enrich_points(raw_poitns, config)

        if target == "tex":
            rendered_elements = [TikzRenderer.render_plot(p) for p in plots] + [
                TikzRenderer.render_point(pt) for pt in points
            ]
            return TikzRenderer.render_graph(config, *rendered_elements)
        elif target == "vue":
            rendered_elements = [VueRenderer.render_plot(p) for p in plots] + [
                VueRenderer.render_point(pt) for pt in points
            ]
            return VueRenderer.render_graph(config, *rendered_elements)

    def table_replacer(match):
        config_str, content_str = Lexer.split_config_block(match.group(1))
        config = Lexer.parse_graph_config(config_str, {"arrows": False})
        headers, rows = Lexer.parse_table_content(content_str)

        deltas = MathEngine.enrich_table_deltas(rows) if config.get("arrows") else []

        return (
            VueRenderer.render_table(headers, rows, deltas, config)
            if target == "vue"
            else TikzRenderer.render_table(headers, rows, deltas, config)
        )

    def task_replacer(match):
        prompt = match.group("prompt").strip()
        config_str, items_str = Lexer.split_config_block(match.group("content"))

        kwargs = Lexer.parse_graph_config(
            config_str, {"cols": 1, "counter": "alph", "shape": "block"}
        )
        parsed_items = Lexer.parse_task_content(items_str)

        max_rowspan = max(
            [item["config"].get("rowspan", 1) for item in parsed_items], default=1
        )
        cols = kwargs["cols"]

        if "max_rows_tex" in kwargs and target == "tex":
            max_rows_tex = kwargs["max_rows_tex"]
        else:
            max_rows_tex = max(max_rowspan, 3)

        if "max_rows_vue" in kwargs and target == "vue":
            max_rows_vue = kwargs["max_rows_vue"]
        else:
            max_rows_vue = max_rowspan

        if target == "tex":
            max_rows = max_rows_tex
            kwargs["max_rows"] = max_rows
        elif target == "vue":
            max_rows = max_rows_vue
            kwargs["max_rows"] = max_rows

        virtual_grid = []

        def get_cell(r, c):
            while len(virtual_grid) <= r:
                virtual_grid.append([None] * cols)
            return virtual_grid[r][c]

        def set_cell(r, c, val):
            while len(virtual_grid) <= r:
                virtual_grid.append([None] * cols)
            virtual_grid[r][c] = val

        current_r, current_c = 0, 0

        for item in parsed_items:
            colspan = min(item["config"].get("colspan", 1), cols)
            rowspan = item["config"].get("rowspan", 1)

            while True:
                if current_c + colspan > cols:
                    current_r += 1
                    current_c = 0
                    continue

                can_fit = True
                for c in range(current_c, current_c + colspan):
                    if get_cell(current_r, c) is not None:
                        can_fit = False
                        break

                if can_fit:
                    break
                else:
                    current_c += 1
                    if current_c >= cols:
                        current_r += 1
                        current_c = 0

                set_cell(current_r, current_c, item)

                for r in range(current_r, current_r + rowspan):
                    for c in range(current_c, current_c + colspan):
                        if r == current_r and c == current_c:
                            continue
                        if r == current_r:
                            set_cell(r, c, "COL_BLOCKED")
                        else:
                            set_cell(r, c, "ROW_BLOCKED")

                current_c += colspan

            matrices = []
            for i in range(0, len(virtual_grid), max_rows):
                matrices.append(virtual_grid[i : i + max_rows])

            if target == "tex":
                return TikzRenderer.render_tasks(prompt, matrices, kwargs)
            elif target == "vue":
                return VueRenderer.render_tasks(prompt, matrices, kwargs)

        text = re.sub(
            r"(?P<prompt>(?:(?!\n::).)*?)\n::tasks\n(?P<content>.*?)\n::",
            task_replacer,
            raw_text,
            flags=re.DOTALL,
        )
        text = re.sub(r"::table\n(.*?)\n::", table_replacer, text, flags=re.DOTALL)
        text = re.sub(r"::graph\n(.*?)\n::", graph_replacer, text, flags=re.DOTALL)

        return text
