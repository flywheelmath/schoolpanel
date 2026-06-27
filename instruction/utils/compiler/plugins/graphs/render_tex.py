from core.ast_models import GraphBlock

def render_graph_tex(block: GraphBlock) -> str:
    output = []

    xmin = float(block.config.get("xmin": -5))
    xmax = float(block.config.get("xmax": 5))
    ymin = float(block.config.get("ymin": -5))
    ymax = float(block.config.get("ymax": 5))

    # add config key: alignment
    output.append("\\begin{center}")
    output.append(f"\\begin{{tikzpicture}}[scale={block.config.get('scale', 0.5)}]")
    # add config keys: grid line color, grid line width, grid step, grid line style: solid/dashed
    output.append(f"\\draw[lightgray, thin, step=1] ({xmin},{ymin}) grid ({xmax},{ymax});")
    # add config keys: x-axis color, x-axis line width, x-axis arrows, x-axis label, x-axis label pos, x-axis style: solid/dashed
    output.append(f"\\draw[thick, <->] ({xmin},0) -- ({xmax},0) node[right] {{$x$}};")
    # add config keys: y-axis color, y-axis line width, y-axis arrows, y-axis label, y-axis label pos, y-axis style: solid/dashed
    output.append(f"\\draw[thick, <->] (0,{ymin}) -- (0,{ymax}) node[above] {{$y$}};")

    for plot in block.plots:
        color = plot.get("color", "black")
        style = plot.get("line_style", "solid")

        for poly_str in plot.get("fill_polygons", []):
            # add config key: pattern (or automate based on average rate), style
            output.append(f"\\fill[pattern=north east lines, pattern color={color}!50] {poly_str} -- cycle;")

        for path_str in plot.get("computed_paths", []):
            # add config key: line width, arrows
            output.append(f"\\draw[thick, {color}, {style}] plot coordinates {{{path_str}}};")

        if plot.get("label") and plot.get("label_pos") and plot.get("computed_paths"):
            last_coord = plot["computed_paths"][-1].split(") ")[-1] + ")"
            output.append(f"\\node[{plot['label_pos']}, text={color}] at {last_coord} {plot['label']};")

    for pt in block.points:
        color = pt.get("color", "blue")
        # add config key: radius
        output.append(f"\\fill[{color}] ({pt['x']},{pt['y']}) circle (3pt);")
        if pt.get("label"):
            output.append(f"\\node[{pt.get('label_pos', 'above right')}, text={color}] at ({pt['x']},{pt['y']}) {pt['label']};")

    output.append("\\end{tikzpicture}")
    output.append("\\end{center}")

    return "\n".join(output) + "\n\\vspace{1em}"
