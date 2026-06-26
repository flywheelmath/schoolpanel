import re
from core.ast_models import Subtask, TaskBlock

def parse_task(body: str, config: str) -> TaskBlock:
    config_dict = {}

    normalized_body = re.sub(r'^\s*[-*]\s+', '*', body, flags=re.MULTILINE)

    raw_subtasks = body.split('\n*')
    processed_subtasks = [Subtask(text=s.strip()) for s in raw_subtasks]

    return TaskBlock(config=config_dict, processed_subtasks=processed_subtasks)
