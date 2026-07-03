from dataclasses import dataclass, field
from typing import Any, Dict, List, Tuple


@dataclass
class Node:
    config: Dict[str, Any] = field(default_factory=dict)
    children: List['Node'] = field(default_factory=list)
    content: str = ""


@dataclass
class Grid(Node):
    pass


@dataclass
class Cell(Node):
    col_span: int = 1


@dataclass
class TaskEntity(Grid):
    pass


@dataclass
class TaskPromptEntity(Node):
    pass


@dataclass
class SubtaskEntity(Cell):
    label: str = ""


@dataclass
class GraphEntity(Node):
    pass

@dataclass
class PointData(Node):
    x: float = 0.0
    y: float = 0.0
    color: str = "blue"
    label: str = ""
    label_pos: str = "above right"
    radiusPts: float = 2.5

@dataclass
class PlotData(Node):
    original_expr: str = ""
    safe_expr: str = ""
    color: str = "blue"
    line_style: str = "solid"
    relation_type: str = "function"
    domain: Tuple[float, float] = None
    label: str = ""
    label_pos: str = "below right"
    computed_paths: List[List[Tuple[float, float]]] = field(default_factory=list)
    fill_polygons: List[List[Tuple[float, float]]] = field(default_factory=list)


@dataclass
class TableEntity(Node):
    pass
