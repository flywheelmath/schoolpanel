import re
from plugins.tasks.parser import parse_task
#from .plugins.graphs import parse_graph
#from .plugins.tables import parse_table

def parse_markdown(raw_chunks: str):
    pattern = re.compile(r":::\s*(\w+)\s*(?:\{(.*?)\})?\s*\n(.*?)\n:::", re.DOTALL)

    ast_nodes = []

    dispatch_map = {
        "tasks": parse_task,
#        "graph": parse_graph,
#        "tables": parse_table
    }

    for match in pattern.finditer(raw_chunks):
        tag, config, body = match.groups()

        if tag in dispatch_map:
            node = dispatch_map[tag](body, config)
            ast_nodes.append(node)
        else:
            print(f"Warning: No parser found for tag: {tag}")

    return ast_nodes
