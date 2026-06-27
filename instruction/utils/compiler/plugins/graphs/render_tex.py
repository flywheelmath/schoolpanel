from core.ast_models import GraphBlock

def render_tex(block: GraphBlock) -> str:
    output = []

    xmin = float(block.config.get("xmin", -5))
    xmax = float(block.config.get("xmax", 5))
    ymin = float(block.config.get("ymin", -5))
    ymax = float(block.config.get("ymax", 5))

    output.append("\\begin{center}")
    output.append(f"\\begin{{tikzpicture}}[scale={block.config.get('scale', 0.5)}]")
    
    output.append(f"\\draw[lightgray, thin, step=1] ({xmin},{ymin}) grid ({xmax},{ymax});")
    output.append(f"\\draw[thick, <->] ({xmin},0) -- ({xmax},0) node[right] {{\\(x\\)}};")
    output.append(f"\\draw[thick, <->] (0,{ymin}) -- (0,{ymax}) node[above] {{\\(y\\)}};")

    output.append(f"\\begin{{scope}}")
    output.append(f"\\clip ({xmin},{ymin}) rectangle ({xmax},{ymax});")

    for plot in block.plots:
        color = plot.get("color", "black")
        style = "dashed" if plot.get("dashed") else plot.get("line_style", "solid")
        pattern = "north west lines"
        if plot.get("computed_paths"):
            pts = plot["computed_paths"][0].replace("(", "").replace(")", "").split(" -- ")
            if len(pts) >= 2:
                y0 = float(pts[0].split(",")[1])
                y1 = float(pts[-1].split(",")[1])
                if y0 > y1:
                    pattern = "north east lines"

        for poly_str in plot.get("fill_polygons", []):
            output.append(f"\\fill[pattern={pattern}, pattern color={color}!40] {poly_str} -- cycle;")

        for path_str in plot.get("computed_paths", []):
            output.append(f"\\draw[thick, {color}, {style}] {{{path_str}}};")

    output.append(f"\\end{{scope}}")

    for pt in block.points:
        color = pt.get("color", "blue")
        output.append(f"\\fill[{color}] ({pt['x']},{pt['y']}) circle (3pt);")
        if pt.get("label"):
            output.append(f"\\node[{pt.get('label_pos', 'above right')}, text={color}] at ({pt['x']},{pt['y']}) {{\\text{{{pt['label']}}}}};")

    output.append("\\end{tikzpicture}")
    output.append("\\end{center}")

    return "\n".join(output) + "\n\\vspace{1em}"
