import uuid
from core.ast_models import TableBlock

def render_tex(block: TableBlock) -> str:
    table_id = block.config.get("id", f"tbl_{uuid.uuid4().hex[:6]}")
    col_width = block.config.get("col_width", "2.5em")
    math_mode = block.config.get("math_mode", True)
    
    def format_cell(text, is_header=False):
        text = text.strip()
        if math_mode and text and not (text.startswith('$') and text.endswith('$')):
            if is_header:
                text = f"${text}$"
            else:
                text = f"${text}$"
        return text

    output = []
    output.append("\\begin{center}")
    output.append("\\begin{tikzpicture}[ampersand replacement=\\&, baseline=(current bounding box.center)]")
    
    output.append(f"  \\matrix ({table_id}) [")
    output.append("    matrix of nodes,")
    output.append("    nodes in empty cells,")
    output.append("    column sep=-\\pgflinewidth,")
    output.append("    row sep=-\\pgflinewidth,")
    
       
    output.append("    nodes={")
    output.append("      draw, solid, thin,")
    output.append("      align=center,")
    output.append(f"      text width={col_width},")
    output.append("      text height=1.5ex,")
    output.append("      text depth=0.5ex,")
    output.append("      inner sep=4pt")
    output.append("    }")
    output.append("  ] {")
    
    if block.headers:
        header_cells = [format_cell(h, is_header=True) for h in block.headers]
        output.append("    " + " \\& ".join(header_cells) + " \\\\")
 
    for row in block.rows:
        data_cells = [format_cell(c) for c in row]
        output.append("    " + " \\& ".join(data_cells) + " \\\\")
        
    output.append("  };")

    if block.headers:
        output.append(f"    \\draw ([yshift=.2ex]{table_id}-1-1.south west) -- ([yshift=.2ex]{table_id}-1-{len(block.headers)}.south east);")
    
    deltas = block.config.get("deltas", [])
    if deltas:
        max_row = len(block.rows)
        
        def get_tikz_row(ast_r_str):
            if ast_r_str == "H": return 1
            return int(ast_r_str) + (2 if block.headers else 1)

        for d in deltas:
            start_str = str(d.get('from', ''))
            end_str = str(d.get('to', ''))
            label = format_cell(d.get('label', ''))
            color = d.get('color', 'red!80')
            
            try:
                from_c = int(start_str.split('-')[1])
                to_c = int(end_str.split('-')[1])
                
                tikz_from_r = get_tikz_row(start_str.split('-')[0])
                tikz_to_r = get_tikz_row(end_str.split('-')[0])
                tikz_from_c = from_c + 1
                tikz_to_c = to_c + 1
            except Exception:
                continue
            
            start_node = f"{table_id}-{tikz_from_r}-{tikz_from_c}"
            end_node = f"{table_id}-{tikz_to_r}-{tikz_to_c}"
            
            span = max(abs(tikz_to_r - tikz_from_r), abs(tikz_to_c - tikz_from_c))
            if span == 0: span = 1
            default_looseness = 1.5 * span
            
            anchor_start, anchor_end = d.get('anchor_start'), d.get('anchor_end')
            out_angle, in_angle = d.get('out'), d.get('in')
            looseness = d.get('looseness', str(default_looseness))
            node_pos, shift = d.get('node_pos'), d.get('shift')

            if from_c == to_c:
                if from_c == 0:
                    anchor_start, anchor_end = anchor_start or '.180', anchor_end or '.180'
                    out_angle, in_angle = out_angle or '180', in_angle or '180'
                    node_pos, shift = node_pos or 'left', shift or 'xshift=0.2em'
                else:
                    anchor_start, anchor_end = anchor_start or '.0', anchor_end or '.0'
                    out_angle, in_angle = out_angle or '0', in_angle or '0'
                    node_pos, shift = node_pos or 'right', shift or 'xshift=-0.2em'
                    
            elif tikz_from_r == tikz_to_r:
                if tikz_from_r == 1 or (tikz_from_r == 2 and block.headers):
                    anchor_start, anchor_end = anchor_start or '.90', anchor_end or '.90'
                    out_angle, in_angle = out_angle or '90', in_angle or '90'
                    node_pos, shift = node_pos or 'above', shift or 'yshift=-0.2em'
                else:
                    anchor_start, anchor_end = anchor_start or '.270', anchor_end or '.270'
                    out_angle, in_angle = out_angle or '270', in_angle or '270'
                    node_pos, shift = node_pos or 'below', shift or 'yshift=0.2em'
            else:
                anchor_start, anchor_end = anchor_start or '', anchor_end or ''
                out_angle, in_angle = out_angle or '0', in_angle or '180'
                node_pos, shift = node_pos or 'above', shift or ''

            shift_str = f", {shift}" if shift else ""
            
            output.append(
                f"  \\draw[-{{To}}, {color}] "
                f"({start_node}{anchor_start}) to[out={out_angle}, in={in_angle}, looseness={looseness}] "
                f"node[{node_pos}{shift_str}, font=\\footnotesize] {{{label}}} ({end_node}{anchor_end});"
            )
            
    output.append("\\end{tikzpicture}")
    output.append(f"\\end{{center}}")
    
    return "\n".join(output) + "\n"
