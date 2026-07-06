from typing import Any, Dict

class GraphConfigAdapter:
    def __init__(self, config: Dict[str, Any]):
        self.xmin = float(config.get("xmin", -6))
        self.xmax = float(config.get("xmax", 6))
        self.ymin = float(config.get("ymin", -6))
        self.ymax = float(config.get("ymax", 6))

        self.xstep = float(config.get("xstep", 1.0))
        self.ystep = float(config.get("ystep", 1.0))

        self.xlabelstep = float(config.get("xlabelstep", 2.0))
        self.ylabelstep = float(config.get("ylabelstep", 2.0))

        self.xlabel = str(config.get("xlabel", "x"))
        self.ylabel = str(config.get("ylabel", "y"))
        self.arrows = str(config.get("arrows", "->"))
