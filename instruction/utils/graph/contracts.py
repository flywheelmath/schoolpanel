from dataclasses import dataclass
from typing import List, Optional, Tuple
import abc

@dataclass
class Viewport:
    xmin: float
    xmax: float
    ymin: float
    ymax: float

@dataclass
class AxisConfig:
    x_step: float
    y_step: float
    x_label_step: float
    y_label_step: float
    x_title: str
    y_title: str
    arrows: str

@dataclass
class PlotStyle:
    color: str = "blue"
    width: float
    pattern: str
    opacity: float

@dataclass
class PointStyle:
    color: str
    radius: float = 3.0
    shape: str = "circle"

@dataclass
class GeometryData:
    paths: List[List[Tuple[float, float]]]
    fills: List[List[Tuple[float, float]]]

@dataclass
class Relation:
    relation: str
    is_explicit: bool
    explicit_relation: Optional[str]
    implicit_relation: str

@dataclass
class PlotData:
    geometry: GeometryData
    style: PlotStyle
    label: Optional[str] = None
    label_position: float = 0.8
    label_placement: str = "below right"

@dataclass
class PointData:
    x: float
    y: float
    label: Optional[str] = None
    label_position: str = "above right"
    style: PointStyle = field(default_factory=PointStyle)

class IGridFactory(abc.ABC):
    @abc.abstractmethod
    def build_viewport(self, config: dict) -> Viewport:
        pass

    @abc.abstractmethod
    def build_axis_config(self, config: dict) -> AxisConfig:
        pass

class IStyleParser(abc.ABC):
    @abc.abstractmethod
    def parse_plot_style(self, config: dict) -> PlotStyle:
        pass

    @abc.abstractmethod
    def parse_point_style(self, config: dict) -> PointStyle:
        pass

clas ICoordinateTransformer(abc.ABC):
    @abc.abstractmethod
    def transform_x(self, x: float) -> float:
        pass

    @abc.abstractmethod
    def transform_y(self, y: float) -> float:
        pass

class IRelationParser(abc.ABC):
    @abc.abstractmethod
    def parse_relation(self, raw_string: str) -> Relation:
        pass

class IExpressionEvaluator(abc.ABC):
    @abc.abstractmethod
    def evaluate_1d(self, expr: str, x: float) -> float:
        pass

    @abc.abstractmethod
    def evaluate_2d(self, expr: str, x: float, y: float) -> float:
        pass

class IGeometryEngine(abc.ABC):
    @abc.abstractmethod
    def generate_geometry(self, relation: Relation, viewport: Viewport, evaluator: IExpressionEvaluator) -> GeometryData:
        pass

class IPathOptimizer(abc.ABC):
    @abc.abstractmethod
    def optimize_geometry(self, geometry: GeometryData, epsilon: float) -> GeometryData:
        pass

class IPlotRenderer(abc.ABC):
    @abc.abstractmethod
    def draw_viewport(self, viewport: Viewport, axis: AxisConfig, transformer: ICoordinateTransformer) -> None:
        pass

    @abc.abstractmethod
    def draw_plot(self, plot_data: PlotData, transformer: ICoordinateTransformer) -> None:
        pass

    @abc.abstractmethod
    def draw_point(self, point_data: PointData, transformer: ICoordinateTransformer) -> None:
        pass

