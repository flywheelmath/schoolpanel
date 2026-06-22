import re
import ast


class MathMacroParser:
    MACRO_REGEX = re.compile(r"graph\((.*?)\)", re.DOTALL)

    KWARG_CHECK = re.compile(r"(\w+)\s*=\s*('[^']*'|\"[^\"]*\"|\[[^\]]*\]|]^,]+)")

    DEFAULT_CONSTRAINTS = {
        "xmin": -10,
        "xmax": 10,
        "ymin": -10,
        "ymax": 10,
        "xstep": 1,
        "ystep": 1,
        "color": '"black"',
        "domain": None,
        "show_triangle": "False",
    }
