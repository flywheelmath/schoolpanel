def lex_markdown(content: str):
    lines = content.splitlines()
    chunks = []

    depth = 0
    current_block = None

    for line in lines:
        stripped = line.strip()

        is_opening = stripped.startswith(":::") and len(stripped) > 3
        is_closing = stripped == ":::"

        if is_opening:
            if depth == 0:
                parts = stripped.split(" ", 2)
                current_block = {
                    "tag": parts[1],
                    "config": parts[2].replace("{", "").replace("}", "") if len(parts) > 2 else "",
                    "body": []
                }
            else:
                current_block["body"].append(line)
            depth += 1

        elif is_closing:
            depth -= 1
            if depth == 0 and current_block:
                current_block["body"] = "\n".join(current_block["body"])
                chunks.append(current_block)
                current_block = None
            elif current_block:
                current_block["body"].append(line)

        elif current_block is not None:
            current_block["body"].append(line)

    return chunks
