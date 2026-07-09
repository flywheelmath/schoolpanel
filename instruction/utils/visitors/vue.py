from typing import List, Tuple

from .base import BaseRenderVisitor
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


class RenderVueVisitor(BaseRenderVisitor):
    def __init__(self, context=None):
        super().__init__(context=context)
        self.file_extension = "md"
        self.subtask_counter = 0

    def emit_headmatter(self):
        self.output.append("---\ntheme: default\nmdc: true\n---\n\n")

    def visit_taskentity(self, node: TaskEntity):
        self.output.append("---\n\n")
        self.subtask_counter = 0

        prompts = [c for c in node.children if isinstance(c, TaskPromptEntity)]
        for p in prompts:
            self.visit(p)

        cols = node.config.get("cols", 2)
        flow = node.config.get("flow", "row")
        self.output.append(f'<SubtaskGrid cols="{cols}" flow="{flow}">\n\n')

        with self.indent():
            remaining_children = [
                c for c in node.children if not isinstance(c, TaskPromptEntity)
            ]
            for child in remaining_children:
                self.visit(child)

        self.emit_line("\n</SubtaskGrid>\n\n")

    def visit_taskpromptentity(self, node: TaskPromptEntity):
        if node.content.strip():
            self.emit_line(f"{node.content}\n\n")

    def visit_subtaskentity(self, node: SubtaskEntity):
        label = chr(ord("a") + self.subtask_counter)
        self.subtask_counter += 1

        if not node.content.strip():
            return

        lines = node.content.strip().split("\n")
        formatted_body = []
        first_line = lines[0].strip()
        if self.indent_level % 2 == 0:
            bullet = "-"
        else:
            bullet = "*"
        formatted_body.append(f"{bullet} ({label}) {first_line}")

        for line in lines[1:]:
            if not line.strip():
                formatted_body.append("")
                continue

            if line.startswith("  ") or line.startswith("\t"):
                formatted_body.append(f"  {line}")
            else:
                formatted_body.append(f"  {line}")

        self.emit_line("\n".join(formatted_body) + "\n")
        self.generic_visit(node)

    def visit_grid(self, node: Grid):
        self.emit_line('<div class="grid-row">\n')
        with self.indent():
            self.generic_visit(node)
        self.emit_line("</div>\n\n")

    def visit_cell(self, node: Cell):
        col_span = node.config.get("col_span", 4)
        self.emit_line(f'<div class="grid-cell col-{col_span}">\n')
        with self.indent():
            if node.content:
                self.emit_line(node.content + "\n")
            self.generic_visit(node)
        self.emit_line("</div>\n")

    def visit_node(self, node: Node):
        if node.content.strip():
            self.emit_line(f"{node.content.strip()}\n\n")

    def visit_sectionheadingentity(self, node: SectionHeadingEntity):
        prefix = "#" * node_level
        self.emit_line(f"{prefix} {node.content}\n\n")

    def draw_list(self, data: ListData) -> None:
        tag_name = "ol" if data.list_type == "ordered" else "ul"
        self.emit_line(f'<{tag_name} class="graph-document-list {data.style_class}">\n')
        for item in data.items:
            marker_attr = f'  data-marker="{item.custom_marker}"' if item.custom_marker else ""
            self.emit_line(f'  <li{marker_attr}>{item.content}</li>\n')
        self.emit_line(f'</{tag_name}>\n')


    def visit_graphentity(self, node: GraphEntity):
        cfg = GraphConfigAdapter(node.config)
        svg_w, svg_h = 500, 500

        def to_screen(mx: float, my: float) -> Tuple[float, float]:
            sx = ((mx - cfg.xmin) / (cfg.xmax - cfg.xmin)) * svg_w
            sy = svg_h - (((my - cfg.ymin) / (cfg.ymax - cfg.ymin)) * svg_h)
            return round(sx, 1), round(sy, 1)
   
        self.emit_line('<div class="graph-wrapper my-4 flex justify-center">\n')
        self.emit_line(f'  <svg viewBox="0 0 {svg_w} {svg_h}" class="graph-svg-canvas">\n')

        self._vue_draw_grid(cfg, to_screen, svg_w, svg_h)
        self._vue_draw_axes(cfg, to_screen, svg_w, svg_h)

        for child in node.children:
            if type(child).__name__ != "PlotData":
                continue

            if hasattr(child, "fill_polygons") and child.fill_polygons:
                for poly in child.fill_polygons:
                    screen_pts = [to_screen(pt[0], pt[1]) for pt in poly]
                    points_str = " ".join(f"{x},{y}" for x, y in screen_pts)
                    self.emit_line(f'    <polygon points="{points_str}" class="graph-plot-fill" />\n')

            if hasattr(child, "computed_paths") and child.computed_paths:
                for path in child.computed_paths:
                    if len(path) < 2:
                        continue
    
                    screen_pts = [to_screen(pt[0], pt[1]) for pt in path]
                    path_d = f"M {screen_pts[0][0]} {screen_pts[0][1]} " + " ".join(f"L {x} {y}" for x, y in screen_pts[1:])
                    style_class = "graph-plot-dashed" if "dashed" in child.config.get("style", "") else "graph-plot-solid"
                    self.emit_line(f'    <path d="{path_d}" fill="none" class="graph-plot-line {style_class}" />\n')

        self.emit_line('  </svg>\n')
        self.emit_line('</div>\n\n')

    def _vue_draw_grid(self, cfg: GraphConfigAdapter, to_screen, svg_w: int, svg_h: int):
        curr_y = cfg.ymin
        while curr_y <= cfg.ymax:
            if abs(curr_y) > 1e-7:
                _, sy = to_screen(cfg.xmin, curr_y)
                self.emit_line(f'    <line x1="0" y1="{sy}" x2="{svg_w}" y2="{sy}" class="graph-grid-line" />\n')
            curr_y += cfg.ystep

        curr_x = cfg.xmin
        while curr_x <= cfg.xmax:
            if abs(curr_x) > 1e-7:
                sx, _ = to_screen(curr_x, cfg.ymin)
                self.emit_line(f'    <line x1="{sx}" y1="0" x2="{sx}" y2="{svg_h}" class="graph-grid-line" />\n')
            curr_x += cfg.xstep

    def _vue_draw_axes(self, cfg: GraphConfigAdapter, to_screen, svg_w: int, svg_h: int):
        axis_x, axis_y = to_screen(0, 0)
        self.emit_line(f'    <line x1="0" y1="{axis_y}" x2="{svg_w}" y2="{axis_y}" class="graph-axis-line" />\n')
        self.emit_line(f'    <line x1="{axis_x}" y1="0" x2="{axis_x}" y2="{svg_h}" class="graph-axis-line" />\n')

        curr_x = cfg.xmin
        while curr_x <= cfg.xmax:
            if abs(curr_x) > 1e-7:
                sx, sy = to_screen(curr_x, 0)
                if cfg.xmin <= curr_x <= cfg.xmax:
                    self.emit_line(f'    <text x="{sx}" y="{sy + 15}" class="graph-label-text" text-anchor="middle">{int(curr_x) if curr_x.is_integer() else curr_x}</text>\n')
            curr_x += cfg.xlabelstep

        curr_y = cfg.ymin
        while curr_y <= cfg.ymax:
            if abs(curr_y) > 1e-7:
                sx, sy = to_screen(0, curr_y)
                if cfg.ymin <= curr_y <= cfg.ymax:
                    self.emit_line(f'    <text x="{sx - 10}" y="{sy + 4}" class="graph-label-text" text-anchor="end">{int(curr_y) if curr_y.is_integer() else curr_y}</text>\n')
            curr_y += cfg.ylabelstep

        label_x_x, label_x_y = to_screen(cfg.xmax, 0)
        label_y_x, label_y_y = to_screen(0, cfg.ymax)
        self.emit_line(f'    <text="{label_x_x - 15}" y="{label_x_y - 10}" class="graph-axis-title" text-anchor="end">{cfg.xlabel}</text>\n')
        self.emit_line(f'    <text="{label_y_x + 15}" y="{label_y_y + 15}" class="graph-axis-title" text-anchor="start">{cfg.ylabel}</text>\n')
