from core.ast_models import TableBlock

def parse_table(body:str, config: str) -> TableBlock:
    lines = [line.strip() for line in body.split('\n') if line.strip()]
    headers = [h.strip() for h in lines[0].split('|') if h.strip()]
    rows = []
    for line i lines[1:]:
        if '---' in line:
            continue
        rows.append([cell.strip() for cell in line.split('|') if cell.strip()])

    return TableBlock(headers=headers, rows=rows)
