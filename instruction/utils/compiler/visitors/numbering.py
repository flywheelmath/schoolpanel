from .base import BaseVisitor
from core.ast_models import Subtask, TaskBlock
from core.state import CounterRegistry

class NumberingVisitor(BaseVisitor):
    def __init__(self, registry: CounterRegistry):
        self.registry = registry

    def generic_visit(self, node):
        pass

    def visit_taskblock(self, block: TaskBlock):
        is_unnumbered = block.config.get("unnumbered", False)

        resume = block.config.get("resume", False)
        self.registry.reset_for_block("subtask", block.config, resume=resume)

        for subtask in block.processed_subtasks:
            if not subtask.is_prompt:
                metadata = self.registry.counters["subtask"].get_counter_metadata()
                subtask.label = metadata["text"]
                subtask.label_width = metadata["style"]["min_width"]
                self.registry.increment("subtask")
