from abc import ABC
from dataclasses import dataclass, field
from typing import List, Union


@dataclass
class Node(ABC):
    pass


@dataclass
class DomainEntity(Node):
    config: dict = field(default_factory=dict)


@dataclass
class TaskEntity(DomainEntity):
    label: str = ""
    content: str = ""
    children: List[DomainEntity] = field(default_factory=list)


@dataclass
class SubtaskEntity(DomainEntity):
    label: str = ""
    content: DomainEntity = None
    children: List[DomainEntity] = field(default_factory=list)


@dataclass
class TextEntity(DomainEntity):
    content: str = ""


@dataclass
class GraphEntity(DomainEntity):
    raw_body: str = ""


@dataclass
class TableEntity(DomainEntity):
    raw_body: str = ""


@dataclass
class LayoutNode(Node):
    config: dict = field(default_factory=dict)
    col_span: int = 1


@dataclass
class Cell(LayoutNode):
    width_fraction: float = 1.0
    children: List[Union[DomainEntity, "Grid"]] = field(default_factory=list)


@dataclass
class Grid(LayoutNode):
    children: List[Cell] = field(default_factory=list)
