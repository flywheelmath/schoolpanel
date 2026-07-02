import re
from dataclasses import dataclass
from .models import (
    Cell,
    Grid,
    Node,
    GraphEntity,
    SubtaskEntity,
    TaskEntity,
    TaskPromptEntity,
    TableEntity,
    TextEntity,
)


def parse_config(config_str: str) -> dict:
    if not config_str or not config_str.strip():
        return {}
    config_dict = {}
    pairs = config_str.split(",")
    for pair in pairs:
        if "=" in pair:
            key, value = pair.split("=", 1)
        elif ":" in pair:
            key, value = pair.split(":", 1)
        if key is not None and value is not None:
            val = value.strip()
            val = val.strip('"').strip("'")
            config_dict[key.strip()] = int(val) if val.isdigit() else val
    return config_dict


@dataclass
class Token:
    type: str
    tag: str = ""
    config: dict = None
    value: str = ""


class Tokenizer:
    def __init__(self, content: str):
        self.content = content

    def tokenize(self) -> list[Token]:
        tokens = []
        pattern = re.compile(r":::\s*(\w+)?\s*(?:\{(.*?)\})?\s*\n?")

        last_end = 0
        for match in pattern.finditer(self.content):
            start, end = match.span()

            text_segment = self.content[last_end:start].strip()
            if text_segment:
                tokens.append(Token(type="TEXT", value=text_segment))

            tag = match.group(1)
            config_str = match.group(2)

            if tag:
                tokens.append(
                    Token(
                        type="OPEN",
                        tag=tag.lower(),
                        config=parse_config(config_str),
                    )
                )
            else:
                tokens.append(Token(type="CLOSE"))

            last_end = end

        remaining_text = self.content[last_end:].strip()
        if remaining_text:
            tokens.append(Token(type="TEXT", value=remaining_text))

        return tokens


class Parser:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.pos = 0

    def parse(self, parent_tag: str = "") -> list[Node]:
        nodes = []
        while self.pos < len(self.tokens):
            token = self.tokens[self.pos]

            if token.type == "OPEN":
                self.pos += 1
                children = self.parse(parent_tag=token.tag)
                node = self.create_node(token.tag, children, token.config)
                if node:
                    nodes.append(node)

            elif token.type == "TEXT":
                self.pos += 1
                extracted_nodes = self.parse_text_blocks(token.value, parent_tag)
                nodes.extend(extracted_nodes)

            elif token.type == "CLOSE":
                self.pos += 1
                break

        return nodes

    def parse_text_blocks(self, text: str, parent_tag: str) -> list[Node]:
        nodes = []
        lines = text.split("\n")

        current_node = None
        current_content = []

        def commit_current():
            if current_node:
                if current_content:
                    current_node.content += "\n" + "\n".join(current_content)
                current_node.content = current_node.content.strip()
                nodes.append(current_node)
            elif current_content:
                content = "\n".join(current_content).strip()
                if content:
                    nodes.append(TextEntity(content=content))

        for line in lines:
            line_stripped = line.strip()
            if not line_stripped:
                current_content.append(line)
                continue

            if line.startswith("  ") or line.startswith("\t"):
                current_content.append(line)
                continue

            config_match = re.match(r'^([#\-*]\s*)\[([^\]]+)\]\s*(.*)$', line_stripped)

            if config_match and parent_tag == "task":
                prefix_marker = config_match.group(1).strip()
                config = parse_config(config_match.group(2))
                line_body = config_match.group(3).strip()

                if prefix_marker == "#":
                    commit_current()
                    content = line_body.lstrip("#").strip()
                    current_node = TaskPromptEntity(config=config, content=content)
                    current_content = []
                    continue

                if prefix_marker in ("-", "*"):
                    commit_current()
                    current_node = SubtaskEntity(config=config, content=line_body)
                    current_content = []
                    continue

            current_content.append(line)

        commit_current()
        return nodes

    def create_node(self, tag, children, config):
        if tag == "grid":
            return Grid(config=config, children=children)

        elif tag == "cell":
            col_span = config.get("col_span", 1)
            return Cell(config=config, col_span=col_span, children=children)

        elif tag == "task":
            label = str(config.get("label", ""))
            return TaskEntity(
                config=config,
                label=label,
                content="",
                children=children,
            )

        elif tag == "subtask":
            label = str(config.get("label", ""))
            return SubtaskEntity(
                config=config,
                label=label,
                content="",
                children=children,
            )

        elif tag == "graph":
            text_parts = [c.content for c in children if isinstance(c, TextEntity)]
            return GraphEntity(config=config, raw_body="\n".join(text_parts).strip())

        elif tag == "table":
            text_parts = [c.content for c in children if isinstance(c, TextEntity)]
            return TableEntity(config=config, raw_body="\n".join(text_parts).strip())

        return None
