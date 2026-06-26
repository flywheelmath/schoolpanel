import re
from core.ast_models import GraphBlock
from plugins.tasks.parser import parse_config

def parse_graph(body: str, config_str: str) -> GraphBlock:
    config = parse_config(config_str)
    
    config.setdefault("xmin", -5)
    config.setdefault("xmax", 5)
    config.setdefault("ymin", -5)
    config.setdefault("ymax", 5)
    config.setdefault("x_step", 1)
    config.setdefault("y_step", 1)

    plots = []
    points = []

    for line in body.split('\n'):
        line = line.strip()
        if line.startswith('plot'):
            match = re.search(r'plot:\s*["\'](.*?)["\']\s*(?:\{(.*?)\})?', line)
            if match:
                expr = match.group(1).strip()
                plot_config_str = match.group(2)
                plot_config = parse_config(plot_config_str) if plot_config_str else {}

                plot_data = {
                    "original_expr": expr,
                    "color": plot_config.get("color", "blue"),
                    "domain": plot_config.get("domain", ""),
                    "label_pos": plot_config.get("label_pos", ""),
                    "label": plot_config.get("label", "")
                }

                if re.search(r'(<=|>=|<|>)', expr):
                    plot_data["type"] = "inequality"
                    plot_data["dashed"] = bool(re.search(r'[^=]=[^=]', expr) is None and "=" not in expr)
                elif "=" in expr:
                    plot_data["type"] = "implicit"
                else:
                    plot_data["type"] = "function"

                plots.append(plot_data)

        elif line.startswith("point"):
            match = re.search(r'point:\s*["\'](.*?)["\']\s*(?:\{(.*?)\})?', line)
            if match:
                coord_str = match.group(1).strip()
                point_config_str = match.group(2)
                point_config = parse_config(point_config_str) if point_config_str else {}

                coords = re.findall(r'-?\d+\.?\d*', coord_str)
                if len(coords) >= 2:
                    points.append({
                        "x": float(coords[0]),
                        "y": float(coords[1]),
                        "color": point_config.get("color", "black"),
                        "label": point_config.get("label", ""),
                        "label_pos": point_config.get("label_pos", ""),
                    })

    return GraphBlock(config=config, raw_body=body, plots=plots, points=points)
