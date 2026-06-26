import re
from core.ast_models import Subtask, TaskBlock

def parse_config(config_str: str) -> dict:
    if not config_str:
        return {}
    config_dict = {}
    pairs = re.findall(r'(\w+)\s*:\s*(?:["\'](.*?)["\']|([^,]+))', config_str)
    for key, quoted_val, unquoted_val in pairs:
        val = quoted_val if quoted_val else unquoted_val.strip()
        if isinstance(val, str):
            if val.lower() == 'true': val = True
            elif val.lower() == 'false': val = False
            elif val.isdigit(): val = int(val)
        config_dict[key] = val
    return config_dict

def parse_task(body: str, config_str: str) -> TaskBlock:
    config = parse_config(config_str)

    raw_subtasks = re.split(r'(?:^|\n)\s*[-*]\s+', body.strip())

    subtasks = []
    for text in raw_subtasks:
        if not text.strip():
            continue
        subtasks.append(Subtask(text=text.strip()))

    return TaskBlock(config=config, processed_subtasks=subtasks)
