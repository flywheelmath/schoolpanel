import re

def lex_markdown(content: str):
    pattern = re.compile(
        r":::\s*(\w*)\s*(?:\{(.*?)\})?\s*\n(.*?)\n:::",
        re.DOTALL
    )

    chunks = []
    for match in pattern.finditer(content):
        tag, config, body = match.groups()
        chunks.append({
            "tag": tag,
            "config": config,
            "body": body.strip()
        })
    return chunks
