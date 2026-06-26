from dataclasses import dataclass, field
from typing import Any, Dict

@dataclass
class LabelCounter:
    counter_type: str = "arabic"
    shape: str = "block"
    prefix: str = ""
    current_value: int = 1

    def increment(self):
        self.current_value += 1

    def get_roman(self, num):
        values = [1000, 900, 500, 400, 100, 90, 50, 40, 10, 9, 5, 4, 1]
        symbols = [
            "M",
            "CM",
            "D",
            "CD",
            "C",
            "XC",
            "L",
            "XL",
            "X",
            "IX",
            "V",
            "IV",
            "I",
        ]
        result = ""
        i = 0
        while num > 0:
            for _ in range(num // values[i]):
                result += symbols[i]
                num -= values[i]
            i += 1
        return result

    def get_counter_str(self, index, counter_type):
        match counter_type:
            case "arabic":
                return str(index)
            case "alph":
                return chr(96 + index)
            case "Alph":
                return chr(64 + index)
            case "roman":
                return self.get_roman(index).lower()
            case "Roman":
                return self.get_roman(index)
            case _:
                return chr(96 + index)


    def get_counter_metadata(self) -> Dict[str, Any]:
        return {
            "text": self.get_counter_str(self.current_value, self.counter_type),
            "style": {
                "shape": self.shape,
                "prefix": self.prefix,
                "min_width": "1.5em"
            }
        }

class CounterRegistry:
    def __init__(self):
        self.counters: Dict[str, LabelCounter] = {}

    def get_current_value(self, key: str) -> int:
        if key not in self.counters:
            return 1
        return self.counters[key].current_value

    def increment(self, key: str):
        if key in self.counters:
            self.counters[key].increment()

    def reset_for_block(self, key: str, config: dict, resume: bool = False):
        if not resume or key not in self.counters:
            self.counters[key] = LabelCounter(
                counter_type=config.get("counter_type", "arabic"),
                shape=config.get("shape", "parens"),
                prefix=config.get("prefix", ""),
                current_value=config.get("start", 1),
            )

    def format(self, key: str) -> str:
        if key not in self.counters:
            return ""
        return self.counters[key].format()

@dataclass
class CompilerContext:
    target: str = "tex"
    scale_factor: float = 1.0
    retistry: CounterRegistry = field(default_factory=CounterRegistry)
    metadata: Dict[str, Any] = field(default_factory=dict)
