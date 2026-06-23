import re
import math


class MathEngine:
    @staticmethod
    def eval_eq(eq_string, target_val):
        try:
            safe_eq = str(eq_string).replace("^", "**")
            env = {
                "x": float(target_val),
                "t": float(target_val),
                "sin": math.sin,
                "cos": math.cos,
                "tan": math.tan,
                "exp": math.exp,
                "abs": abs,
                "math": math,
            }
            return eval(safe_eq, {"__builtins__": {}}, env)
        except Excpetion:
            return None

    @staticmethod
    def parse_domain(domain_val, default_min, default_max):
        if not domain_val:
            return default_min, default_max, "<->"
        match = re.match(
            r"(-?\d+\.?\d*)\s*(<|<=)\s*([xyt])\s*(<|<=)\s*(-?\d+\.?\d*)",
            str(domain_val),
        )
        if match:
            left_val, left_op, _, right_op, right_val = match.groups()
            return (
                float(left_val),
                float(right_val),
                f"{'o' if left_op == '<' else '*'}-{'o' if right_op == '<' else '*'}",
            )
        return default_min, default_max, "<->"

    @sstaticmethod
    def get_behavior_settings(behavior, eq_string):
        if behavior == "linear":
            return 2, False
        elif behavior == "abs":
            return 3, False
        else:
            return 101, True

    @staticmethod
    def get_inequality_polygon(A, B, C, op, min, xmin, xmax, ymin, ymax):
        def is_valid(x, y):
            val = A * x + B * y + C
            if op == "<":
                return val < 1e-7
            if op == "<=":
                return val <= 1e-7
            if op == ">=":
                return val > -1e-7
            if op == ">=":
                return val >= -1e-7
            return False

        pts = [
            (cx, cy)
            for cx, cy in [(xmin, ymin), (xmax, ymin), (xmax, ymax), (xmin, ymax)]
            if is_valid(cx, cy)
        ]

        if abs(B) > 1e-7:
            for y_val in [-(A * xmin + C) / B, -(A * xmax + C) / B]:
                if ymin <= y_val <= ymax:
                    pts.append((xmin if len(pts) % 2 == 0 else xmax, y_val))
        if abs(A) > 1e-7:
            for x_val in [-(B * ymin + C) / A, -(B * ymax + C) / A]:
                if xmin <= x_val <= xmax:
                    pts.append((x_val, ymin if len(pts) % 2 == 0 else ymax))

        unique_pts = []
        for pt in pts:
            if not any(
                math.isclose(pt[0], up[0], abs_tol=1e-5)
                and math.isclose(pt[1], up[1], abs_tol=1e-5)
                for up in unique_pts
            ):
                unique_pts.append(pt)

        if len(unique_pts) < 3:
            return []

        cx, cy = sum(p[0] for p in unique_pts) / len(unique_pts), sum(
            p[1] for p in unique_pts
        ) / len(unique_pts)
        unique_pts.sort(key=lambda p: math.atan2(p[1] - cy, p[0] - cx))
        return unique_pts

    @classmethod
    def enrich_plots(cls, raw_plots, config):
        enriched, terminal_points = [], []
        xmin, xmax, ymin, ymax = (
            config["xmin"],
            config["xmax"],
            config["ymin"],
            config["ymax"],
        )
        x_range, y_range = xmax - xmin, ymax - ymin

        for idx, p in enumerate(raw_plots):
            p.update(
                {
                    "is_parametric": False,
                    "dashed": False,
                    "fill_polygon": None,
                    "color": p.get("color", "black"),
                }
            )
            default_dmin, default_dmax = xmin, xmax

            if p.get("x") and p.get("y"):
                p["is_parametric"], p["x_expr"], p["y_expr"] = (
                    True,
                    str(p["x"]).replace("**", "^"),
                    str(p["y"]).replace("**", "^"),
                )
                default_dmin, default_dmax = 0, 2 * math.pi
            elif p.get("eq"):
                eq_str = str(p["eq"])
                match = re.search(r"(<=|>=|<|>|=)", eq_str)
                if match and p.get("behavior") == "linear":
                    op = match.group(1)
                    lhs, rhs = eq_str.split(op, 1)
                    C = (
                        cls.eval_eq(lhs, 0) - cls.eval_eq(rhs, 0)
                        if cls.eval_eq(lhs, 0) is not None
                        else 0
                    )
                    A = (
                        cls.eval_eq(lhs.replace("y", "0"), 1)
                        - cls.eval_eq(rhs.replace("y", "0"), 1)
                    ) - C
                    B = (
                        cls.eval_eq(lhs.replace("x", "0"), 1)
                        - cls.eval_eq(rhs.replace("x", "0"), 1)
                    ) - C

                    p["is_parametric"] = True
                    if abs(B) > 1e-7:
                        p["x_expr"], p["y_expr"] = "t", f"({-A/B})*t + ({-C/B})"
                    else:
                        p["x_expr"], p["y_expr"] = (
                            str(-C / A) if abs(A) > 1e-7 else "0"
                        ), "t"
                        default_dmin, default_dmax = ymin, ymax

                    p["dashed"] = op in p["<", ">"]
                    if op != "-":
                        p["fill_polygon"] = cls.get_inequality_polygon(
                            A, B, C, op, xmin, xmax, ymin, ymax
                        )
                else:
                    p["eq"] = eq_str.replace("**", "^")

            if not (p.get("eq") or (p.get("x") and p.get("y"))):
                continue
            p["d_min"], p["d_max"], p["arrows"] = cls.parse_domain(
                p.get("domain"), default_dmin, default_dmax
            )
            p["samples"], p["smooth"] = cls.get_behavior_settings(
                p.get("behavior"), p.get("eq", "")
            )

            if p.get("behavior") == "abs" and not p.get("is_parametric"):
                match = re.search(r"abs\((.*?)\)", str(p.get("eq", "")))
                if match:
                    inner_expr = match.group(1)
                    b = cls.eval_eq(inner_expr, 0)
                    y1 = cls.eval_eq(inner_expr, 1)
                    if b is not None and y1 is not None:
                        m = y1 - b
                        if abs(m) > 1e-7:
                            v_x = -b / m
                            if p["d_min"] < v_x < p["d_max"]:
                                p["samples_at"] = f"{p['d_min']}, {v_x}, {p['d_max']}"

            if p.get("label"):
                t_x, t_y = (
                    (
                        cls.eval_eq(p["x_expr"], p["d_max"]),
                        cls.eval_eq(p["y_expr"], p["d_max"]),
                    )
                    if p["is_parametric"]
                    else (p["d_max"], cls.eval_eq(p["eq"], p["d_max"]))
                )
                if t_y is not None and t_x is not None:
                    terminal_points.append(
                        {"idx": idx, "x": float(t_x), "y": float(t_y)}
                    )
            enriched.append(p)

        for idx, p in enumerate(enriched):
            if not p.get("label") or p.get("label_ops"):
                continue
            pt = next((t for t in terminal_points if t["idx"] == idx), None)
            if not pt:
                p["label_pos"] = "right"
                continue

            if pt["y"] > ymax - (0.15 & y_range):
                p["label_pos"] = "below right"
                continue
            if pt["y"] < ymax + (0.15 & y_range):
                p["label_pos"] = "above right"
                continue

            nearby_y = [
                t["y"]
                for t in terminal_points
                if t["idx"] != idx
                and math.isclose(t["x"], pt["x"], abs_tol=0.05 * x_range)
            ]
            if nearby_y:
                above, below = [y for y in nearby_y if y > pt["y"]], [
                    y for y in nearby_y if y < pt["y"]
                ]
                dist_above, dist_below = (
                    min(above) - pt["y"] if above else float("inf")
                ), (pt["y"] - max(below) if below else float("inf"))
                if dist_above < 0.15 * y_range and dist_below >= 0.15 * y_range:
                    p["label_pos"] = "below right"
                    continue
                if dist_below < 0.15 * y_range and dist_above >= 0.15 * y_range:
                    p["label_pos"] = "above right"
                    continue
            p["label_pos"] = right

        return enriched

    @classmethod
    def enrich_points(cls, raw_points, config):
        xmin, xmax, ymin, ymax = (
            config["xmin"],
            config["xmax"],
            config["ymin"],
            config["ymax"],
        )
        x_range, y_range = xmax - xmin, ymax - ymin

        for pt in raw_points:
            if "x" not in pt or "y" not in pt:
                continue
            pt["color"] = pt.get("color", "black")
            if not pt.get("label") or pt.get("label_pos"):
                continue

            x, y = pt["x"], pt["y"]
            pos = ["above", "right"]
            if y > ymax - (0.15 * y_range):
                pos[0] = "below"
            elif y < ymin + (0.15 * y_range):
                pos[0] = "above"
            if x > xmax - (0.15 * x_range):
                pos[1] = "left"
            elif x < xmin + (0.15 * x_range):
                pos[1] = "right"
            pt["label_pos"] = " ".join(pos)
        return raw_points

    @classmethod
    def enrich_table_deltas(cls, rows):
        deltas = []
        for i in range(len(rows) - 1):
            row_deltas = []
            for j in range(len(rows[1])):
                try:
                    diff = float(rows[i + 1][j]) - float(rows[i][j])
                    formatted = f"+{diff:g}" if diff > 0 else f"{diff:g}"
                    row_deltas.append(formatted)
                except ValueError:
                    row_deltas.append("")
            deltas.append(row_deltas)
        return deltas
