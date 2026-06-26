from core.ast_models import Subtask, TaskBlock
from core.state import CounterRegistry

class NumberingVisitor:
    def __init__(self, registry: CounterRegistry):
        self.registry = registry

    def visit(self, ast_nodes: list):
        for node in ast_nodes:
            self._dispatch(node)

    def _dispatch(self, node):
        if isinstance(node, TaskBlock):
            self.visit_task_block(node)

    def visit_task_block(self, block: TaskBlock):
        is_unnumbered = block.config.get("unnumbered", False)

        resume = block.config.get("resume", False)
        self.registry.reset_for_block("subtask", block.config, resume=resume)

        for subtask in block.processed_subtasks:
            if not subtask.is_prompt:
                metadata = self.registry.counters["subtask"].get_counter_metadata()
                subtask.label = metadata["text"]
                subtask.label_width = metadata["style"]["min_width"]
                self.registry.increment("subtask")
