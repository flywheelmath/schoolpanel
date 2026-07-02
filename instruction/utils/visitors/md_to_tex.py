import re

def process_md_lists_to_tex(text: str) -> str:
    if not text or not text.strip():
        return ""

    math_blocks = []
    def mask_math(match):
        placeholder = f"XXXMATHBLOCKXXX{len(math_blocks)}"
        math_blocks.append(match.group(0))
        return placeholder

    masked_text = re.sub(r'(\$.*?\$|\\\(.*?\\\))', mask_math, text)

    lines = masked_text.split('\n')
    formatted_lines = []
    env_stack = []

    for line in lines:
        stripped = line.strip()
        if not stripped:
            formatted_lines.append("")
            continue

        bullet_match = re.match(r'(\s*)([-*])\s+(.*)$', line)
        num_match = re.match(r'(\s*)([0-9a-zA-Z]+[\.)])\s+(.*)$', line)
        quote_match = re.match(r'^(\s*)>\s*(.*)$', line)
        active_match = bullet_match or num_match

        if active_match:
            leading_whitespace = len(active_match.group(1))

            if bullet_match:
                target_env = "itemize"
                content_body = bullet_match.group(3)
            elif num_match:
                target_env = "enumerate"
                content_body = num_match.group(3)
            elif quote_match:
                target_env = "quote"
                content_body = quote_match.group(3)
                print("quote")
                print(content_body)
    
            if not env_stack or leading_whitespace > env_stack[-1][0]:
                formatted_lines.append(f"{' ' * (len(env_stack)*2)}  \\begin{{{target_env}}}")
                env_stack.append((leading_whitespace, target_env))
    
            elif env_stack and leading_whitespace < env_stack[-1][0]:
                while env_stack and leading_whitespace < env_stack[-1][0]:
                    _, old_env = env_stack.pop()
                    formatted_lines.append(f"{' ' * (len(env_stack)*2)}  \\end{{{old_env}}}")
    
            indent_spaces = " " * (len(env_stack) * 2)
            if target_env == "quote":
                formatted_lines.append(f"{indent_spaces} {content_body}")
            else:
                formatted_lines.append(f"{indent_spaces}  \\item {content_body}")
        else:
            if env_stack:
                indent_spaces = " " * (len(env_stack) * 2)
                formatted_lines.append(f"{indent_spaces}    {line.strip()}")
            else:
                formatted_lines.append(line)

    while env_stack:
        _, old_env = env_stack.pop()
        formatted_lines.append(f"{' ' * (len(env_stack)*2)}  \\end{{{old_env}}}")

    final_tex = "\n".join(formatted_lines)

    for idx, raw_math in enumerate(math_blocks):
        final_tex = final_tex.replace(f"XXXMATHBLOCKXXX{idx}", raw_math)

    return final_tex

def process_md_to_tex(content: str) -> str:
    parts = re.split(r"(\\\[.*?\\\]|\\\(.*?\\\))", content, flags=re.DOTALL)

    # Special LaTeX characters

    for i in range(len(parts)):
        if i % 2 == 0:
            text = parts[i]
            if not text:
                continue

            text = re.sub(r"</?v-click>", "", text)
            text = re.sub(r"(?m)^---\s*$", r"\n\n", text)

            code_blocks = []

            def shield_code(match):
                code_blocks.append(match.group(1))
                return f"CODEPLACEHOLDER{len(code_blocks)-1}"

            text = re.sub(r"`([^`]+)`", shield_code, text)

            text = text.replace("\\", "\\textbackslash ")
            text = re.sub(r"([&%$_{}])", r"\\\1", text)

            text = re.sub(r"\*\*(.*?)\*\*", r"\\textbf{\1}", text)
            text = re.sub(r"\*(.*?)\*", r"\\textit{\1}", text)
            text = re.sub(r"==(.*?)==", r"\\colorbox{red}{\1}", text)

            text = re.sub(r"(?m)^###\s+(.*)$", r"\\subsubsection*{\1}", text)
            text = re.sub(r"(?m)^##\s+(.*)$", r"\\subsection*{\1}", text)
            text = re.sub(r"(?m)^#\s+(.*)$", r"\\section*{\1}", text)

            text = re.sub(r"(#)", r"\\\1", text)
            text = text.replace("~", "\\textasciitilde{}")
            text = text.replace("^", "\\textasciicircum{}")

            def handle_markdown_links(match):
                display_text = match.group(1)
                address_target = match.group(2)
                clean_address = address_target.replace("\\", "")
                return f"\\href{{{clean_address}}}{{{display_text}}}"

            text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", handle_markdown_links, text)

            def handle_bare_url(match):
                target = match.group(1)
                clean_target = target.replace("\\", "")
                return f"\\url{{{clean_target}}}"

            text = re.sub(r"(?m)(?<!\{)(https?://[^\s<]+)", handle_bare_url, text)

            text = re.sub(r'"([^"]*)"', r"``\1''", text)
            text = text.replace("--", "---")
            text = text.replace("[Blank]", r"\blank")

            for idx, raw_code in enumerate(code_blocks):
                escaped_code = (
                    raw_code.replace("&", "\\&")
                    .replace("%", "\\%")
                    .replace("$", "\\$")
                    .replace("_", "\\_")
                    .replace("#", "\\#")
                    .replace("{", "\\{")
                    .replace("}", "\\}")
                )
                text = text.replace(
                    f"CODEPLACEHOLDER{idx}", f"\\texttt{{{escaped_code}}}"
                )

            parts[i] = text

    assembled = "".join(parts)

    # Markdown lists

    assembled = process_md_lists_to_tex(assembled)


    return assembled 
