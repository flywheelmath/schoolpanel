import re
import numpy as np
import sympy
import matplotlib.pyplot as plt
from core.ast_models import GraphBlock

SAMPLES_COUNT = 501

def compute_graph(block: GraphBlock):
    xmin = float(block.config.get("xmin", -5))
    xmax = float(block.config.get("xmax", 5))
    ymin = float(block.config.get("ymin", -5))
    ymax = float(block.config.get("ymax", 5))
    pad = 1.0

    x_range = np.linspace(xmin - pad, xmax + pad, 300)
    y_range = np.linspace(ymin - pad, ymax + pad, 300)
    X, Y = np.meshgrid(x_range, y_range)

    for plot in block.plots:
        d_min, d_max = xmin, xmax
        if plot.get("domain"):
            match = re.search(r'(-?\d+\.?\d*)\s*(<|<=)\s*[x]\s*(<|<=)\s*(-?\d+\.?\d*)', plot["domain"])
            if match:
                d_min, d_max = float(match.group(1)), float(match.group(4))

        plot["computed_paths"] = []
        plot["fill_polygons"] = []

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
            except Exception as e:
                print(f"Math Error ({plot['original_expr']}): {e}")

        elif plot["type"] == "implicit":
            lhs, rhs = plot["original_expr"].split("=")
            safe_expr = f"({lhs}) - ({rhs})".replace('^', '**')
            try:
                f = sympy.lambdify(sympy.symbols('x y'), sympy.sympify(safe_expr), "numpy")
                Z = f(X, Y)
                contour_set = plt.contour(X, Y, Z, levels=[0])
                for path in contour_set.get_paths():
                    if len(path.vertices) > 1:
                        path_str = " ".join([f"({vx:.3f}, {vy:.3f})" for vx, vy in path.vertices])
                        plot["computed_paths"].append(path_str)
            except Exception as e:
                print(f"Implicit Math Error ({plot['original_expr']}): {e}")

        elif plot["type"] == "inequality":
            op_match = re.search(r'(<=|>=|<|>)', plot["original_expr"])
            op = op_match.group(1)
            lhs, rhs = plot["original_expr"].split(op)
            safe_expr = f"({lhs}) - ({rhs})".replace('^', '**')
            plot["dashed"] = op in ["<", ">"]

            try:
                f = sympy.lambdify(sympy.symbols('x y'), sympy.sympify(safe_expr), "numpy")
                
                X, Y = np.meshgrid(np.linspace(xmin, xmax, 100), np.linspace(ymin, ymax, 100))
                Z = f(X, Y)
                
                z_min, z_max = np.min(Z), np.max(Z)
                levels = [0.0, max(1.0, z_max * 2.0)] if op in [">", ">="] else [min(-1.0, z_min * 2.0), 0.0]

                cf = plt.contourf(X, Y, Z, levels=levels)
                for path in cf.get_paths():
                    for poly in path.to_polygons():
                        if len(poly) > 2:
                            plot["fill_polygons"].append(" -- ".join([f"({vx:.2f}, {vy:.2f})" for vx, vy in poly]))

                cl = plt.contour(X, Y, Z, levels=[0])
                for path in cl.get_paths():
                    if len(path.vertices) > 1:
                        plot["computed_paths"].append(" -- ".join([f"({vx:.2f}, {vy:.2f})" for vx, vy in path.vertices]))

                plt.close()
            except Exception as e:
                print(f"Inequality Math Error ({plot['original_expr']}): {e}")
