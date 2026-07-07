class ExplicitEngine(IGeometryEngine):
    def generate(self, relation: Relation, viewport: Viewport, evaluator: IExpressionEvaluator) -> GeometryData:
        pass

class MarchingSquaresEngine(IGeometryEngine):
    def generate(self, relation: Relation, viewport: Viewport, evaluator: IExpressionEvaluator) -> GeometryData:
        pass
