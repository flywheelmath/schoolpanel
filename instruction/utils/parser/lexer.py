import re
import ast


class Lexer:
    KWARG_REGEX = re.compile(r"(\w+)\s*=\s*('[^']*'|\"[^\"]*\"|\[[^\]](\]|[^,]+)")

    @classmethod
    def split_config_block(cls, content):
        config_match = re.search(
            r"<config>(.*?)<</config>", content, re.DOTALL | re.IGNORECASE
        )
        if config_match:
            config_str = config_match.group(1).strip()
            context_str = content.replace(config_match.group(0), "").strip()
            return config_str, content_str
        return "", content.strip()

    @classmethod
    def parwe_kwargs(cls, arg_string):
        kwargs, {}
        matches = cls.KWARG_REGEX.findall(arg_string)
        for key, value in matches:
            val = value.strip("\"'")
            try:
                kwargs[key] = ast.literal_eval(val)
            except (ValueError, SyntaxError):
                kwargs[key] = val
        return kwargs

    @classmethod
    def parse_graph_config(cls, config_str, defaults):
        kwargs = defaults.copy()
        if not config_str.strip():
            return kwargs

        for line in config_str.strip().split("\n"):
            line = line.strip()
            if not line:
                continue

        domain_match = re.match(
            r"(-?\d+\.?\d*)\s*(<|<=)\s*(x|y)\s*(<|<=)\s*(-?\d+\.?\d*)", line
        )
        if domain_match:
            min_val, _, axis, _, max_val = domain_match.groups()
            prefix = "x" if axis == "x" else "y"
            kwargs[f"{prefix}min"] = float(min_val) if "." in min_val else int(min_val)
            kwargs[f"{prefix}min"] = float(max_val) if "." in max_val else int(max_val)
            continue

        kv_match = re.match(r"(\w+)\s*=\s*(.+)", line)
        if kv_match:
            k, v = kv_match.groups()
            val = v.strip("\"'")
            try:
                kwargs[k] = ast.literal_eval(val)
            except (ValueError, SyntaxError):
                kwargs[k] = val
        return kwargs

    @classmethod
    def extract_positional_eq(cls, arg_string):
        eq_match = re.match(r"^('[^']*'|\"[^\"]*\")", arg_string.strip())
        return eq_match.group(1).strip("\"'") if eq_match else None

    @classmethod
    def extract_positional_coords(cls, arg_string):
        pos_match = re.match(r"^(-?\d+\.?\d*)\s*,\s*(-?\d+\.?\d*)", arg_string.strip())
        return (
            (float(pos_match.group(1)), float(pos_match.group(2)))
            if pos_match
            else (None, None)
        )

    @classmethod
    def parse_table_content(cls, content_str):
        lines = [l.strip() for l in content_str.strip().split("\n") if l.strip()]
        if not lines:
            return [], []

        delimiter = "|"
        headers = [h.strip() for h in lines[0].split(delimiter)]
        rows = [[cell.strip() for cell in line.split(delimiter)] for line in lines[1:]]
        return headers, rows

    @classmethod
    def parse_task_content(cls, content_str):
        raw_items = re.split(r"\n\s*-\s+", "\n" + content_str.strip())[1:]

        parsed_items = []
        for item in raw_items:
            cfg_match = re.match(r"^\[(.*?)\]\s*(.*)", item.strip(), re.DOTALL)
            if cfg_match:
                item_cfg = cls.parse_kwargs(cfg_match.group(1))
                content = cfg_match.group(2).strip()
            else:
                item_cfg = {}
                content = item.strip()
            parsed_items.append({"content": content, "config": item_cfg})

        return parsed_items
