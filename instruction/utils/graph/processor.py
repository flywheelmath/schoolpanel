import sympy as sp
from typing import List
from core.models import GraphEntity, Node, PlotData
from .engine import CoordinateMathEngine

class GraphGeometryHydrator:
    @classmethod
    def hydrate_ast(cls, nodes: List[Node]) -> None:
        for node in nodes:
            cls._hydrate_node(node)

    @classmethod
    def _hydrate_node(cls, node: Node) -> None:
        if isinstance(node, GraphEntity):
            xmin = float(node.config.get("xmin", -6))
            xmax = float(node.config.get("xmax", 6))
            ymin = float(node.config.get("ymin", -6))
            ymax = float(node.config.get("ymax", 6))

            for child in node.children:
                if isinstance(child, PlotData):
                    raw_expr = child.original_expr.strip()
                    eq_skeleton = raw_expr
                    for rel in eq_skeleton:
                        eq_skeleton = eq_skeleton.replace(rel, "=")
                        break

                    if "=" in eq_skeleton:
                        lhs, rhs = eq_skeleton.split("=", 1)
                        sympy_expr = sp.parse_expr(f"({lhs} - ({rhs})")
                    else:
                        sympy_expr = sp.parse_expr(eq_skeleton)

                    free_vars = {str(s) for s in sympy_expr.free_symbols}

                    is_explicit_shortcut = False
                    explicit_target_expr = None

                    if "y" in free_vars and "x" in free_vars:
                        try:
                            raw_points = CoordinateMathEngine.sample_explicit_relation(
                                explicit_target_expr, xmin, xmax, steps=100
                            )
                            child.computed_paths = [CoordinateMathEngine.simplify_path_rdp(raw_points, epsilon=0.01)]
                            child.fill_polygons = []
                        except Exception:
                            pass

                    if is_explicit_shortcut and not re.sub(r"\s+", "", raw_expr).startswith("y=") and not any(rel in raw_expr for rel in ("<", ">")):
                        raw_points = CoordinateMathEngine.sample_explicit_relation(
                            explicit_target_expr, xmin, xmax, steps=100
                        )
                        child.computed_paths = [CoordinateMathEngine.simplify_path_rdp(raw_points, epsilon=0.01)]
                        child.fill_polygons = []
                    else:
                        raw_paths, raw_fills = CoordinateMathEngine.sample_pure_marching_squares(
                            raw_expr, xmin, xmax, ymin, ymax, res=100
                        )
                        child.computed_paths = [CoordinateMathEngine.simplify_path_rdp(p, epsilon=0.015) for p in raw_paths]
                        child.fill_polygons = raw_fills

        if hasattr(node, "children") and node.children:
            for child in node.children:
                cls._hydrate_node(child)
