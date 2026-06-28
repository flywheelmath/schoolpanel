import re
import numpy as np
import sympy
import matplotlib.pyplot as plt
from core.ast_models import GraphBlock

SAMPLES_COUNT = 201

def sanitize_expr(expr_str):
    expr_str = re.sub(r'(\d)([a-zA-Z\(])', r'\1*\2', expr_str)
    return expr_str.replace("^", "**")

def is_linear(safe_expr):
    x, y = sympy.symbols('x y')
    expr = sympy.sympify(safe_expr)

    dx = sympy.diff(expr, x)
    dy = sympy.diff(expr, y)

    return dx.is_constant() and dy.is_constant()

def compute_relation(plot):
    expr_str = sanitize_expr(plot["original_expr"])

    if any(rel in expr_str for rel in ["<=", ">="]):
        rel = next(r for r in ["<=", ">="] if r in expr_str)
        lhs, rhs = expr_str.split(rel)
        plot["rel"], plot["safe_expr"] = rel, f"({lhs.strip()}) - ({rhs.strip()})"
        plot["relation_type"] = "nonstrict_inequality"
    elif any(rel in expr_str for rel in ["<", ">"]):
        rel = next(r for r in ["<", ">"] if r in expr_str)
        lhs, rhs = expr_str.split(rel)
        plot["rel"], plot["safe_expr"] = rel, f"({lhs.strip()}) - ({rhs.strip()})"
        plot["relation_type"] = "strict_inequality"
    elif "=" in expr_str:
        lhs, rhs = expr_str.split("=")
        plot["rel"], plot["safe_expr"] = "=", f"({lhs.strip()}) - ({rhs.strip()})"
        plot["relation_type"] = "equation"
    elif "t" in expr_str.lower():
        x_expr, y_expr = expr_str.split(",")
        plot["safe_x_expr"], plot["safe_y_expr"] = x_expr.strip(), y_expr.strip()
        plot["relation_type"] = "parametric"
    else:
        plot["rel"], plot["safe_expr"] = "=", f"y - ({expr_str})"
        plot["relation_type"] = "equation"

    plot["dashed"] = plot["relation_type"] == "strict_inequality"
    return plot["relation_type"]

def compute_graph(block: GraphBlock):
    xmin = float(block.config.get("xmin", -5))
    xmax = float(block.config.get("xmax", 5))
    ymin = float(block.config.get("ymin", -5))
    ymax = float(block.config.get("ymax", 5))

    for plot in block.plots:
        plot["computed_paths"] = []
        plot["fill_polygons"] = []
        relation_type = compute_relation(plot)

        if relation_type == "parametric":
            t_min, t_max = 0, 2 * np.pi

            if plot.get("domain"):
                match = re.search(r'(-?\d+\.?\d*)\s*(<|<=)\s*[t]\s*(<|<=)\s*(-?\d+\.?\d*)', plot["domain"])
                if match:
                    t_min, t_max = float(match.group(1)), float(match.group(4))

            t_vals = np.linspace(t_min, t_max, SAMPLES_COUNT)

            fx = sympy.lambdify(sympy.Symbol('t'), sympy.sympify(plot["safe_x_expr"]), "numpy")
            fy = sympy.lambdify(sympy.Symbol('t'), sympy.sympify(plot["safe_y_expr"]), "numpy")           

            x_vals, y_vals = fx(t_vals), fy(t_vals)
            valid_mask = (y_vals >= ymin) & (y_vals <= ymax) & (x_vals >= xmin) & (x_vals <= xmax)
            path_str = " -- ".join([f"({vx:.3f},{vy:.3f})" for vx, vy in zip(x_vals[valid_mask], y_vals[valid_mask])])
            plot["computed_paths"].append(path_str)

        elif is_linear(plot["safe_expr"]):
            d_min, d_max = xmin, xmax
            if plot.get("domain"):
                match = re.search(r'(-?\d+\.?\d*)\s*(<|<=)\s*x\s*(<|<=)\s*(-?\d+\.?\d*)', plot["domain"])
                if match: d_min, d_max = float(match.group(1)), float(match.group(4))

            compute_linear_graph(plot, xmin, xmax, ymin, ymax)

        else:
            d_min, d_max = xmin, xmax
            if plot.get("domain"):
                match = re.search(r'(-?\d+\.?\d*)\s*(<|<=)\s*x\s*(<|<=)\s*(-?\d+\.?\d*)', plot["domain"])
                if match: d_min, d_max = float(match.group(1)), float(match.group(4))
                
            f = sympy.lambdify(sympy.symbols('x y'), sympy.sympify(plot["safe_expr"]), "numpy")
            X, Y = np.meshgrid(np.linspace(xmin, xmax, SAMPLES_COUNT), np.linspace(ymin, ymax, SAMPLES_COUNT))
            Z = f(X, Y)

            contour_set = plt.contour(X, Y, Z, levels=[0])
            for path in contour_set.get_paths():
                v = path.vertices
                v_list = [tuple(p) for p in v]
                simplified = rdp(v_list, epsilon=0.001)

                mask = (v[:,0] >= d_min) & (v[:,0] <= d_max) & (v[:,1] >= ymin) & (v[:,1] <= ymax)
                if np.any(mask):
                    plot["computed_paths"].append(" -- ".join([f"({vx:.3f},{vy:.3f})" for vx, vy in simplified]))

            if "inequality" in relation_type:
                is_greater = any(rel in plot["rel"] for rel in [">", ">="])
                z_min, z_max = np.min(Z), np.max(Z)
                levels =  [0, max(1.0, z_max + 1)] if is_greater else [min(-1.0, z_min - 1), 0]

                cf = plt.contourf(X, Y, Z, levels=levels)
                for path in cf.get_paths():
                    for poly in path.to_polygons():
                        if len(poly) > 2:
                            poly_list = [tuple(p) for p in poly]
                            simplified = rdp(poly_list, epsilon=0.05)
                            plot["fill_polygons"].append(" -- ".join([f"({vx:.2f},{vy:.2f})" for vx, vy in simplified]))

            plt.close()

def compute_linear_graph(plot, xmin, xmax, ymin, ymax):
    x, y = sympy.symbols('x y')
    expr = sympy.sympify(plot["safe_expr"])

    A = float(sympy.diff(expr, x))
    B = float(sympy.diff(expr, y))
    C = float(expr.subs({x: 0, y: 0}))

    intersections = []

    if B != 0:
        y_left = -(A * xmin + C) / B
        if ymin <= y_left <= ymax: intersections.append((xmin, y_left))

        y_right = -(A * xmax + C) / B
        if ymin <= y_right <= ymax: intersections.append((xmax, y_right))

    if A != 0:
        x_bottom = -(B * ymin + C) / A
        if xmin <= x_bottom <= xmax: intersections.append((x_bottom, ymin))

        x_top = -(B * ymax + C) / A
        if xmin <= x_top <= xmax: intersections.append((x_top, ymax))

    intersections = list(set([(round(px, 3), round(py, 3)) for px, py in intersections]))

    unique_intersections = []
    for p in intersections:
        if not any(np.allclose(p, u, atol=1e-3) for u in unique_intersections):
            unique_intersections.append(p)

    if len(unique_intersections) >= 2:
        p1, p2 = unique_intersections[0], unique_intersections[1]
        plot["computed_paths"].append(f"({p1[0]:.2f},{p1[1]:.2f}) -- ({p2[0]:.2f},{p2[1]:.2f})")

        if "inequality" in plot["relation_type"]:
            import math
            is_greater = any(rel in plot["rel"] for rel in [">", ">="])
            corners = [(xmin, ymin), (xmax, ymin), (xmax, ymax), (xmin, ymax)]
            valid_corners = []

            f_val = lambda cx, cy: A*cx + B*cy + C

            for cx, cy in corners:
                val = f_val(cx, cy)
                if (is_greater and val >= 0) or (not is_greater and val <= 0):
                    valid_corners.append((cx, cy))

            all_pts = list(set([p1, p2] + valid_corners))

            cx_centroid = sum(p[0] for p in all_pts) / len(all_pts)
            cy_centroid = sum(p[1] for p in all_pts) / len(all_pts)
            all_pts.sort(key=lambda p: math.atan2(p[1] - cy_centroid, p[0] - cx_centroid))
            all_pts.append(all_pts[0])

            plot["fill_polygons"].append(" -- ".join([f"({vx:.2f},{vy:.2f})" for vx, vy in all_pts]))
            plt.close()

def distance_from_line(point, start, end):
    px, py = point
    sx, sy = start
    ex, ey = end

    dx = ex - sx
    dy = ey - sy

    if dx == 0 and dy == 0:
        return np.sqrt((px - sx)**2 + (py - sy)**2)

    num = abs(dy * px - dx * py + ex * sy - ey * sx)
    den = np.sqrt(dx**2 + dy**2)

    return num / den

def rdp(points, epsilon):
    """
    Simplifies path of points using Ramer-Douglas-Peucker algorithm.
    epsilon: max distance to allow deviation
    """
    if len(points) < 3: return points

    distances = [distance_from_line(p, points[0], points[-1]) for p in points]
    index = np.argmax(distances)

    if distances[index] > epsilon:
        return rdp(points[:index+1], epsilon)[:-1] + rdp(points[index:], epsilon)
    else:
        return [points[0], points[-1]]
