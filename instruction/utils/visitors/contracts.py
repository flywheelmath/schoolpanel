import abc
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

@dataclass
class SectionHeading:
    text: str
    level: int
    label: Optional[str] = None

@dataclass
class SubtaskData:
    content: str
    label: str
    col_span: int = 1
    row_span: int = 1

@dataclass
class TaskData:
    prompt_text: str
    subtasks: List[SubtaskData] = field(default_factory=list)
    grid_cols: int = 2
    grid_flow: str = "row"

@dataclass(frozen=True)
class LayoutCell:
    col_span: int
    row_span: int
    content_code: Any

@dataclass(frozen=True)
class LayoutRow:
    cells: List[LayoutCell]
    height: int

class IDocumentStructureParser(abc.ABC):
    @abc.abstractmethod
    def parse_document(self, raw_markdown: str) -> List[Any]:
        pass

class IGridPackingStrategy(abc.ABC):
    @abcabstractmethod
    def compute_layout_rows(self, raw_cells: List[LayoutCell], total_columns: int = 12) -> List[LayoutRow]:
        pass

class IGeneralLayoutRenderer(abc.ABC):
    @abc.abstractmethod
    def open_document(self, metadata: Dict[str, Any]) -> str:
        pass

    @abc.abstractmethod
    def render_heading(self, heading: SectionHeading) -> str:
        pass

    @abc.abstractmethod
    def open_grid(self, class_name: Optional[str] = None) -> str:
        pass

    @abc.abstractmethod
    def render_layout_row(self, row: LayoutRow, cell_render_callback: Any) -> str:
        pass

    @abc.abstractmethod
    def render_task(self, task: TaskData, active_width_fraction: float) -> str:
        pass

    @abc.abstractmethod
    def closed_grid(self) -> str:
        pass

    @abc.abstractmethod
    def close_document(self) -> str:
        pass
