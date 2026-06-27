import re
import numpy as np
import sympy
import matplotlib.pyplot as plt
from base import BaseVisitor
from core.ast_models import GraphBlock

SAMPLES_COUNT = 501

class ComputationVisitor(BaseVisitor):
    def visit(self, ast_nodes: list):
        for node in ast_nodes:
            if isinstance(node, GraphBlock):
                self.visit_graphblock(node)

    def visit_graphblock(self, block: GraphBlock):
        xmin = float(block.config.get("xmin", -5))
        xmax = float(block.config.get("xmax", 5))
        ymin = float(block.config.get("ymin", -5))
        ymax = float(block.config.get("ymax", 5))

        x_range = xmax - xmin
        y_range = ymax - ymin

        for plot in block.plots:
            d_min, d_max = xmin, xmax
            if plot.get("domain"):
                match = re.search(r'(-?\d+\.?\d*)\s*(<|<=)\s*[x]\s*(<|<=)\s*(-?\d+\.?\d*)', plot["domain"])
                if match:
                    d_min, d_max = float(match.group(1)), float(match.group(4))

            terminal_pt = None
            plot["computed_paths"] = []

            if plot["type"] == "function":
                x_vals = np.linspace(d_min, d_max, SAMPLES_COUNT)
                safe_expr = plot["original_expr"].replace('^', '**')
                try:
                    f = sympy.lambdify(sympy.Symbol('x'), sympy.sympify(safe_expr), "numpy")
                    y_vals = f(x_vals)
                    valid_mask = (y_vals >= ymin) & (y_vals <= ymax) & (x_vals >= xmin) & (x_vals <= xmax)
                    valid_indices = np.where(valid_mask)[0]

                    if len(valid_indices) > 0:
                        segments = np.split(valid_indices, np.where(np.diff(valid_indices) != 1)[0] + 1)

                        for seg in segments:
                            if len(seg) > 1:
                                path_str = " ".join([f"({x_vals[i]:.3f}, {y_vals[i]:.3f})" for i in seg])
                                plot["computed_paths"].append(path_str)

                        last_idx = valid_indices[-1]
                        terminal_pt = (x_vals[last_idx], y_vals[last_idx])

                except Exception as e:
                    print(f"Math Error ({plot['original_expr']}): {e}")

            elif plot["type"] == "implicit":
                lhs, rhs = plot["original_expr"].split("=")
                implicit_expr = f"({lhs}) - ({rhs})"

                try:
                    f = sympy.lambdify(sympy.symbols('x y'), sympy.sympify(safe_expr), "numpy")
                    X, Y = np.meshgrid(np.linspace(xmin-1, xmax+1, 200), np.linespace(ymin-1, ymax+1, 200))
                    Z = f(X, Y)
                    if np.isscalar(Z): Z = np.full_like(X, Z)
                    contour = plt.contour(X, Y, Z, levels=[0])
                    max_x = -float('inf')
                    term_y = 0

                    for collection in contour.collections:
                        for path in collection.get_paths():
                            valid_vertices = [v for v in path.vertices if xmin <= v[0] <= xmax and ymin <= v[1] <= ymax]
                            if len(valid_vertices) > 1:
                                path_str = " ".join([f"({vx:.3f}, {vy:.3f})" for vx, vy in valid_vertices])
                                plot["computed_paths"].append(path_str)

                                for vx, vy in valid_vertices:
                                    if vx > max_x:
                                        max_x, term_y = vx, vy
                    plt.close()

                    if max_x != -float('inf'):
                        terminal_pt = (max_x, term_y)

                except Exception as e:
                    print(f"Implicit Math Error ({plot['original_expr']}): {e}")

            elif plot["type"] == "inequality":
                op_match = re.search(r'(<=|>=|<|>)', plot["original_expr"])
                op = op_match.group(1)
                lhs, rhs = plot["original_expr"].split(op)

                boundary_expr = f"({rhs} - ({lhs})"
                plot["fill_polygon"] = "(-5, -5) (5, -5) (-5, 5)" # placeholder

            if plot.get("label") and not plot.get("label_pos") and terminal_pt:
                t_x, t_y = terminal_pt

                pos_y = "above"
                pos_x = "right"

                if t_y > ymax - (0.15 * y_range):
                    pos_y = "below"
                elif t_y < ymin + (0.15 * y_range):
                    pos_y = "above"

                if t_x > xmax - (0.15 * x_range):
                    pos_x = "left"
                elif t_x < xmin + (0.15 * x_range):
                    pos_x = "right"

                plot["label_pos"] = f"{pos_y} {pos_x}".strip()

        for pt in block.points:
            if pt.get("label") and not pt.get("label_pos"):
                pos_y, pos_x = "above", "right"
                if pt["y"] > ymax - (0.15 * y_range):
                    pos_y = "below"
                if pt["y"] < ymin + (0.15 * y_range):
                    pos_y = "above"
                if pt["x"] > xmax - (0.15 * x_range):
                    pos_x = "left"
                if pt["x"] < xmin + (0.15 * x_range):
                    pos_x = "right"
                pt["label_pos"] = f"{pos_y} {pos_x}".strip()
