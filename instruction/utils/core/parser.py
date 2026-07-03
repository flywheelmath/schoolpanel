import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Type
from .models import (
    Cell,
    Grid,
    Node,
    GraphEntity,
    PlotData,
    PointData,
    SectionHeadingEntity,
    SubtaskEntity,
    TaskEntity,
    TaskPromptEntity,
    TableEntity,
)


def parse_config(config_str: str) -> dict:
    if not config_str or not config_str.strip(): return {}
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

def parse_inline_config(config_str: str) -> dict:
    if not config_str: return {}
    config_dict = {}
    pairs = re.findall(r'(\w+)\s*=\s*["\']?(.*?)["\']?(?=\s|\s*$)', config_str)
    for key, value in pairs:
        val = value.strip()
        config_dict[key] = int(val) if val.isdigit() else val
    return config_dict

@dataclass
class Token:
    type: str
    tag: str = ""
    config: dict = field(default_factory=dict)
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
    NODE_REGISTRY: Dict[str, Type[Node]] = {
        "grid": Grid,
        "cell": Cell,
        "task": TaskEntity,
        "subtask": SubtaskEntity,
        "graph": GraphEntity,
        "plot": PlotData,
        "point": PointData,
        "table": TableEntity,
        "heading": SectionHeadingEntity,
    }

    CONTEXTUAL_INLINE_REGISTRY: Dict[str, Dict[str, Type[Node]]] = {
        "": {
            "#": SectionHeadingEntity,
        },
        "task": {
            "#": TaskPromptEntity,
            "-": SubtaskEntity,
            "*": SubtaskEntity,
        },
        "grid": {
            "-": Cell,
            "*": Cell,
        }
    }

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
                    current_registry_class = self.NODE_REGISTRY.get(parent_tag)
                    if current_registry_class and issubclass(current_registry_class, Grid) and not isinstance(node, Cell):
                        wrapper = Cell(config=node.config, children=[node])
                        wrapper.col_span = int(node.config.get("col_span", 12))
                        nodes.append(wrapper)
                    else:
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

        inside_shortcode = False
        shortcode_payload = []
        shortcode_base_config = {}

        def commit_current():
            nonlocal current_node, current_content
            if current_node:
                if current_content:
                    current_node.content += "\n" + "\n".join(current_content)
                current_node.content = current_node.content.strip()
                nodes.append(current_node)
            elif current_content:
                content = "\n".join(current_content).strip()
                if content:
                    nodes.append(Node(content=content))
            current_node = None
            current_content = []

        idx = 0
        while idx < len(lines):
            line = lines[idx]
            line_stripped = line.strip()

            if line_stripped.startswith("[graph"):
                inside_shortcod = True
                config_str = line_stripped.lstrip("[graph").rstrip("]").strip()
                shortcode_base_config = parse_inline_config(config_str)
                shortcode_payload = []
                idx += 1
                continue

            if line_stripped.startswith("[/graph]"):
                inside_shortcode = False
                graph_children = self._parse_shortcode_body(shortcode_payload)
                compiled_graph = GraphEntity(config=shortcode_base_config, children=graph_children)

                if current_node:
                    current_node.children.append(compiled_graph)
                elif nodes:
                    if parent_tag == "grid" and isinstance(nodes[-1], Cell) and nodes[-1].children:
                        nodes[-1].children[0].children.append(compiled_graph)
                    else:
                        nodes[-1].children.append(compiled_graph)
                else:
                    if parent_tag == "grid":
                        wrapper_cell = Cell(config={"col_span": 12}, children=[compiled_graph])
                        nodes.append(wrapper_cell)
                    else:
                        nodes.append(compiled_graph)
                idx += 1
                continue

            if inside_shortcode:
                shortcode_payload.append(line)
                idx += 1
                continue
            
            if not line_stripped or line.startswith("  ") or line.startswith("\t"):
                current_content.append(line)
                idx += 1
                continue

            tag_rules = self.CONTEXTUAL_INLINE_REGISTRY.get(parent_tag, {})

            config_match = re.match(r"^([#\-*]\s*)\[([^\]]+)\]\s*(.*)$", line_stripped)
            if config_match:
                prefix_marker = config_match.group(1).strip()
                config_str = config_match.group(2)
                config = parse_config(config_str) if config_str else {}
                line_body = config_match.group(3).strip()

                if prefix_marker in tag_rules:
                    commit_current()
                    target_class = tag_rules[prefix_marker]

                    if target_class == SectionHeadingEntity:
                        current_node = SectionHeadingEntity(config=config, level=len(prefix_marker), content=line_body)
                    elif target_class == TaskPromptEntity:
                        current_node = TaskPromptEntity(
                            config=config, content=line_body.lstrip("#").strip()
                        )
                    elif issubclass(target_class, Cell):
                        current_node = target_class(config=config, col_span=config.get("col_span", 4))
                        current_node.content = line_body
                    else:
                        current_node = target_class(config=config, content=line_body)

                    idx += 1
                    continue

            current_content.append(line)
            idx += 1

        commit_current()
        return nodes

    def _parse_shortcode_body(self, payload_lines: List[str]) -> List[Node]:
        children_nodes = []
        for line in payload_lines:
            line = line.strip()
            if not line or line.startswith("#") or line.startswith("//"):
                continue

            if line.startswith("plot:"):
                match = re.search(r'plot:\s*["\'](.*?)["\']\s*(.*?)', line)
                if match:
                    expr = match.group(1).strip()
                    config_str = match.group(2).strip().strip("{}").strip()
                    config = parse_inline_config(config_str)

                    is_dashed = "<" in expr or ">" in expr
                    style = "dashed" if is_dashed else config.get("line_style", "solid")

                    domain_tuple = None
                    if "domain" in config:
                        try:
                            d_min, d_max = map(float, str(config["domain"]).split(":"))
                            domain_tuple = (d_min, d_max)
                        except ValueError:
                            pass

                    children_nodes.append(PlotData(
                        config=config,
                        original_expr=expr,
                        color=config.get("color", "blue"),
                        line_style=style,
                        domain=domain_tuple,
                        label=config.get("label", ""),
                        label_pos=config.get("label_pos", "below right"),
                    ))

            elif line.startswith("point:"):
                match = re.search(r'point:\s*["\'](.*?)["\']\s*(.*?)', line)
                if match:
                    coord_str = match.group(1).strip()
                    config_str = match.group(2).strip().strip("{}").strip()
                    config = parse_inline_config(config_str)

                    coords = re.findall(r'-?\d+\.?\d*', coord_str)
                    if len(coords) >= 2:
                        children_nodes.append(PointData(
                            config=config,
                            x=float(coords[0]),
                            y=float(coords[1]),
                            color=config.get("color", "blue"),
                            label=config.get("label", ""),
                            label_pos=config.get("label_pos", "above_right")
                        ))
        return children_nodes


    def create_node(
        self, tag: str, children: List[Node], config: Dict[str, Any]
    ) -> Optional[Node]:
        node_class = self.NODE_REGISTRY.get(tag)
        if not node_class:
            return None

        if node_class == Cell:
            col_span = config.get("col_span", 4)
            return Cell(config=config, col_span=col_span, children=children)

        if node_class == SubtaskEntity:
            label = str(config.get("label", ""))
            col_span = int(config.get("col_span", "4"))
            return SubtaskEntity(
                config=config,
                col_span=col_span,
                label=label,
                children=children,
            )

        if issubclass(node_class, Grid):
            normalized_children = []
            for child in children:
                child_type_name = type(child).__name__
 
                if child_type_name in ("Cell", "SubtaskEntity", "TaskPromptEntity"):
                    normalized_children.append(child)
                else:
                    wrapper = Cell(config=child.config, children=[child])
                    wrapper.col_span = int(child.config.get("col_span", 12))
                    normalized_children.append(wrapper)

            return node_class(config=config, children=normalized_children)

        return node_class(config=config, children=children)
