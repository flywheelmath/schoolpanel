from dataclasses import dataclass, field
from typing import List, Optional, Union
from abc import ABC

@dataclass
class EmbeddableBlock(ABC):
    config: dict = field(default_factory=dict)
    raw_body: str = ""

    float_pos: str = "none"
    float_width: str = ""

@dataclass
class GraphBlock(EmbeddableBlock):
    plots: List[dict] = field(default_factory=list)
    points: List[dict] = field(default_factory=list)

@dataclass
class TableBlock(EmbeddableBlock):
    headers: List[str] = field(default_factory=list)
    rows: List[List[str]] = field(default_factory=list)
    deltas: List[List[str]] = field(default_factory=list)

@dataclass
class InfoBlock(ABC):
    config: dict = field(default_factory=dict)
    raw_body: str = ""
    content: str = ""

    row_span: int = 1
    col_span: int = 1

@dataclass
class SupportiveInfoBlock(InfoBlock):
    pass

@dataclass
class ProceduralInfoBlock(InfoBlock):
    pass

@dataclass
class Subtask:
    text: str = ""
    workspace: str = ""
    is_prompt: bool = False

    row_span: int = 1
    col_span: int = 1

    row_tex: int = 0
    col_tex: int = 0
    row_span_tex: int = 1
    col_span_tex: int = 1

    row_vue: int = 0
    col_vue: int = 0
    row_span_vue: int = 1
    col_span_vue: int = 1

    global_idx: int = 0
    subtask_counter_value: int = 1
    label: str = ""
    label_width: float = 0.0

@dataclass
class TaskBlock:
    config: dict = field(default_factory=dict)
    raw_body: str = ""

    processed_subtasks: List[Subtask] = field(default_factory=list)

    subtask_resume_counter: bool = False
    subtask_counter_type: str = "arabic"
    subtask_counter_shape: str = "block"
    subtask_label: str = ""

    rows_per_page_tex: int = 10
    cols_tex: int = 4

    rows_per_slide_vue: int = 1
    cols_vue: int = 2

    is_unnumbered: bool = False
    task_counter_value: int = 1
    label: str = ""
    label_width: float = 0.0

@dataclass
class CompositeBlock:
    children: List[Union[TaskBlock, GraphBlock, TableBlock]] = field(default_factory=list)
