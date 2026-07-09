import re
from .md_to_tex import process_md_to_tex
from .base import BaseRenderVisitor
from .layout import BaseGridRenderStrategy, DualHeightRowsGridStrategy
from core.models import (
    Cell,
    Grid,
    GraphEntity,
    Node,
    SectionHeadingEntity,
    SubtaskEntity,
    TableEntity,
    TaskEntity,
    TaskPromptEntity,
)
from graph.config import GraphConfigAdapter


class RenderTeXVisitor(BaseRenderVisitor):
    def __init__(self, context=None, grid_strategy: BaseGridRenderStrategy = None):
        super().__init__(context=context)
        self.grid_strategy = grid_strategy or DualHeightRowsGridStrategy()
        self.file_extension = "tex"

    def visit_grid(self, node: Grid):
        self.grid_strategy.render(node, self)

    def visit_cell(self, node: Cell):
        if node.content:
            clean_content = process_md_to_tex(node.content)
            width_fraction = self.context.get_width(node)
            self.render_semantic_environment("cell", clean_content, width_fraction)
        self.generic_visit(node)

    def emit_task_start(self, node, width_fraction):
        self.emit_line(f"\\begin{{task}}[{width_fraction:.4f}]\n")

    def emit_task_end(self, node):
        self.emit_line("\\end{task}\n")

    def visit_taskentity(self, node: TaskEntity):
        width_fraction = self.context.get_width(node)
        self.emit_task_start(node, width_fraction)

        with self.indent():
            self.grid_strategy.render(node, self)

        self.emit_task_end(node)

    def visit_taskpromptentity(self, node: TaskPromptEntity):
        width_fraction = self.context.get_width(node)
        clean_content = process_md_to_tex(node.content)
        self.render_semantic_environment("prompt", clean_content, width_fraction)

    def visit_subtaskentity(self, node: SubtaskEntity):
        width_fraction = self.context.get_width(node)
        clean_content = process_md_to_tex(node.content)
        self.render_semantic_environment("subtask", clean_content, width_fraction)
        self.generic_visit(node)

    def visit_sectionheadingentity(self, node: SectionHeadingEntity):
        tex_headers = {
            1: r"\section*",
            2: r"\subsection*",
            3: r"\subsubsection*",
            4: r"\paragraph",
        }
        cmd = tex_headers.get(node.level, r"\paragraph")
        self.emit_line(f"{cmd}{{{node.content}}}\n")

    def visit_node(self, node: Node):
        if node.content.strip():
            clean_content = process_md_to_tex(node.content)
            self.emit_line(f"{clean_content}\n\n")

    def render_semantic_environment(self, env_name, content, width_fraction):
        self.emit_line(f"\\{env_name}[{width_fraction:.4f}]{{{content}}}\n")

    def visit_graphentity(self, node: GraphEntity):
        cfg = GraphConfigAdapter(node.config)

        self.emit_line(r"\begin{center}")
        self.emit_line(r"\begin{tikzpicture}[scale=0.5]")
        self._tex_draw_grid(cfg)
        self._tex_draw_axes(cfg)

        for child in node.children:
            if type(child).__name__ != "PlotData":
                continue

            if hasattr(child, "fill_polygons") and child.fill_polygons:
                for poly in child.fill_polygons:
                    coord_str = " -- ".join(f"({round(pt[0],3)},{round(pt[1],3)})" for pt in poly)
                    self.emit_line(f"  \\fill[graph-plot-fill] {coord_str} -- cycle;")

            if hasattr(child, "computed_paths") and child.computed_paths:
                for path in child.computed_paths:
                    if len(path) < 2:
                        continue
                    coord_str = " -- ".join(f"({round(pt[0],3)},{round(pt[1],3)})" for pt in path)
                    line_style = "graph-plot-line"
                    if "dashed" in child.config.get("style", ""):
                        line_style += ", dashed"
                    self.emit_line(f"  \\draw[{line_style}] {coord_str};")

        self.emit_line(r"\end{tikzpicture}")
        self.emit_line(r"\end{center}" + "\n")

    def _tex_draw_grid(self, cfg: GraphConfigAdapter):
        self.emit_line(f"  \\draw[graph-grid, step={cfg.xstep}] ({cfg.xmin},{cfg.ymin}) grid ({cfg.xmax},{cfg.xmax},{cfg.ymax});")

    def _tex_draw_axes(self, cfg: GraphConfigAdapter):
        arrow_opt = f", {cfg.arrows}" if cfg.arrows and cfg.arrows.lower() != "none" else ""
        self.emit_line(f"  \\draw[graph-axis{arrow_opt}] ({cfg.xmin},0) -- ({cfg.xmax},0) node[right] {{{cfg.xlabel}}};")
        self.emit_line(f"  \\draw[graph-axis{arrow_opt}] (0,{cfg.ymin}) -- (0,{cfg.ymax}) node[above] {{{cfg.ylabel}}};")

        curr_x = cfg.xmin
        while curr_x <= cfg.xmax:
            if abs(curr_x) > 1e-7:
                label_val = int(curr_x) if curr_x.is_integer() else curr_x
                self.emit_line(f"  \\node[below, class=graph-tick-label] at ({curr_x},0) {{{label_val}}};")
            curr_x += cfg.xlabelstep

        curr_y = cfg.ymin
        while curr_y <= cfg.ymax:
            if abs(curr_y) > 1e-7:
                label_val = int(curr_y) if curr_y.is_integer() else curr_y
                self.emit_line(f"  \\node[left, class=graph-tick-label] at (0,{curr_y}) {{{label_val}}};")
            curr_y += cfg.ylabelstep

    def visit_tableentity(self, node: TableEntity):
        self.emit_line(node.raw_body)

    def draw_list(self, data: ListData) -> None:
        env_name = "enumerate" if data.list_type == "ordered" else "itemize"
        self.emit_line(f"\\begin{{{env_name}}}\n")
        for item in data.items:
            marker_prefix = f"[{item.custom_marker}]" if item.custom_marker else ""
            self.emit_line(f"  \\item{marker_prefix} {item.content}\n")
        self.emit_line(f"\\end{{{env_name}}}\n")
