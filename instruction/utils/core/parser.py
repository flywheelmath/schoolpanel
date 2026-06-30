import re
from dataclasses import dataclass
from .models import (
    Grid,
    Cell,
    TaskEntity,
    SubtaskEntity,
    TextEntity,
    GraphEntity,
    TableEntity,
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
    def __init__(self, content: str):
        self.tokens = Tokenizer(content).tokenize()
        self.pos = 0

    def parse(self) -> list:
        return self._parse_block()

    def _parse_block(self) -> list:
        nodes = []
        while self.pos < len(self.tokens):
            token = self.tokens[self.pos]

            if token.type == "CLOSE":
                self.pos += 1
                break

            elif token.type == "OPEN":
                self.pos += 1
                children = self._parse_block()
                node = self.create_node(token.tag, children, token.config)
                if node:
                    nodes.append(node)

            elif token.type == "TEXT":
                self.pos += 1
                nodes.append(TextEntity(content=token.value))

        return nodes

    def create_node(self, tag, children, config):
        if tag == "grid":
            return Grid(config=config, children=children)

        elif tag == "cell":
            col_span = config.get("col_span", 1)
            return Cell(config=config, col_span=col_span, children=children)

        elif tag == "task":
            label = str(config.get("label", ""))
            text_parts = [c.content for c in children if isinstance(c, TextEntity)]
            content_str = "\n".join(text_parts).strip()
            non_text_children = [c for c in children if not isinstance(c, TextEntity)]
            return TaskEntity(
                config=config,
                label=label,
                content=content_str,
                children=non_text_children,
            )

        elif tag == "subtask":
            label = str(config.get("label", ""))
            text_parts = [c.content for c in children if isinstance(c, TextEntity)]
            content_str = "\n".join(text_parts).strip()
            non_text_children = [c for c in children if not isinstance(c, TextEntity)]
            return SubtaskEntity(
                config=config,
                label=label,
                content=content_str,
                children=non_text_children,
            )

        elif tag == "graph":
            text_parts = [c.content for c in children if isinstance(c, TextEntity)]
            return GraphEntity(config=config, raw_body="\n".join(text_parts).strip())

        elif tag == "table":
            text_parts = [c.content for c in children if isinstance(c, TextEntity)]
            return TableEntity(config=config, raw_body="\n".join(text_parts).strip())

        return None
