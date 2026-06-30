import re
from core.ast_models import TableBlock
from plugins.tasks.parser import parse_config

def parse_table(body: str, config_str: str) -> TableBlock:
    config = parse_config(config_str)
    lines = [line.strip() for line in body.split('\n') if line.strip()]
    
    headers = []
    rows = []
    
    if "deltas" not in config:
        config["deltas"] = []
        
    delta_pattern = re.compile(r'\[([vh])(?:,\s*(\d+))?\s*:\s*(.*?)\]')

    def extract_deltas(cell_content, row_idx, col_idx, has_headers):
        matches = delta_pattern.findall(cell_content)
        clean_content = delta_pattern.sub('', cell_content).strip()
        
        for direction, span_str, label in matches:
            span = int(span_str) if span_str else 1
            
            if direction == 'v':
                source_r = row_idx - span
                if has_headers:
                    source_r = max(-1, source_r)
                    source_row_str = "H" if source_r == -1 else str(source_r)
                else:
                    source_r = max(0, source_r)
                    source_row_str = str(source_r)
                    
                config["deltas"].append({
                    "from": f"{source_row_str}-{col_idx}",
                    "to": f"{row_idx}-{col_idx}",
                    "label": label.strip()
                })
            elif direction == 'h':
                source_c = max(0, col_idx - span)
                config["deltas"].append({
                    "from": f"{row_idx}-{source_c}",
                    "to": f"{row_idx}-{col_idx}",
                    "label": label.strip()
                })
        return clean_content

    if not lines:
        return TableBlock(config=config, raw_body=body)

    has_headers = False
    if '|' in lines[0]:
        headers = [h.strip() for h in lines[0].split('|') if h.strip()]
        lines = lines[1:]
        has_headers = True

    data_row_idx = 0
    for line in lines:
        if '---' in line:
            continue
        
        raw_cells = [cell.strip() for cell in line.split('|') if cell.strip()]
        clean_cells = []
        for col_idx, cell in enumerate(raw_cells):
            clean_cell = extract_deltas(cell, data_row_idx, col_idx, has_headers)
            clean_cells.append(clean_cell)
        
        rows.append(clean_cells)
        data_row_idx += 1

    return TableBlock(
        config=config,
        headers=headers,
        rows=rows,
        raw_body=body
    )
