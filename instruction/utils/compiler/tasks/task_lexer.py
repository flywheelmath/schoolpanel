import re
import ast
from abc import ABC
from dataclasses import dataclass, field
from typing import Union, List

@dataclass
class Subtask:
    text: str = ""
    is_prompt: bool = False
    width: int = 1
    height: int = 1
    workspace: str = "4cm"

    row_tex: int = 0
    col_tex: int = 0

    row_vue: int = 0
    col_vue: int = 0

    fit_width_tex: int = 1
    fit_width_vue: int = 1

    global_idx: int = 0

@dataclass
class TaskBlock:
    config: dict = field(default_factory=dict)
    raw_body: str = ""
    parsed_prompt: str = ""
    parsed_subtasks: list[str] = field(default_factory=list)
    processed_subtasks: list[Subtask] = field(default_factory=list)

    cols_tex: int = 4
    cols_vue: int = 2

    max_rows_tex: int = 10
    max_rows_vue: int = 2

    rows_tex: int = 0
    rows_vue: int = 0
    scale_factor: float = 1.0

    default_workspace: str = "4cm"
    default_prompt_workspace: str = "0.5cm"

@dataclass
class InfoBlock:
    config: dict = field(default_factory=dict)
    raw_body: str = ""
    content: str = ""

    width: int = 1
    height: int = 1

@dataclass
class SupportiveInfoBlock(InfoBlock):
    pass

@dataclass
class ProceduralInfoBlock(InfoBlock):
    pass

@dataclass
class LayoutNode:
    col: int
    row: int
    width: int
    height: int

    subtask: Subtask | None = None
    children: list['LayoutNode'] = field(default_factory=list)
    split_direction: str = "horizontal"



class TaskLexer:
    @staticmethod
    def lex(raw_md: str) -> list[TaskBlock]:
        pattern = re.compile(r"^[ \t]*:::\s*tasks\s*\{?(.*?)\}?\s*\n(.*?)\n[ \t]*:::", re.MULTILINE | re.DOTALL)
        lexed_blocks = []

        for match in pattern.finditer(raw_md):
            config_str = match.group(1).strip()
            content = match.group(2).strip()

            bullet_match = re.search(r"^[ \t]*[*[-]\s+", content, re.MULTILINE)
            if bullet_match:
                prompt = content[:bullet_match.start()].strip()
                items_str = content[bullet_match.start():]
                raw_items = re.split(r"^[ \t]*[*[-]\s+", "\n" + items_str, flags=re.MULTILINE)[1:]
            else:
                prompt = content
                raw_items = []

            block = TaskBlock(
                raw_body=match.group(0),
                parsed_prompt=prompt,
                parsed_subtasks=[t.strip() for t in raw_items if t.strip()]
            )

            kwargs = {}
            for pair in config_str.split(","):
                if ":" in pair:
                    k, v = pair.split(":", 1)
                    kwargs[k.strip()] = v.strip()
                elif "=" in pair:
                    k, v = pair.split("=", 1)
                    kwargs[k.strip()] = v.strip()
            block.config = kwargs
            lexed_blocks.append(block)

        return lexed_blocks
