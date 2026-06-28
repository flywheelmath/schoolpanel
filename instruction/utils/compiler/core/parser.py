from plugins.graphs.parser import parse_graph
from plugins.tables.parser import parse_table
from plugins.tasks.parser import parse_task

def parse_chunks(raw_chunks: list):
    from plugins.composite.parser import parse_composite

    ast_nodes = []
    dispatch_map = {
        "task": parse_task,
        "graph": parse_graph,
        "table": parse_table,
        "composite": parse_composite
    }

    for chunk in raw_chunks:
        tag = chunk.get("tag")
        if tag in dispatch_map:
            node = dispatch_map[tag](chunk["body"], chunk["config"])
            ast_nodes.append(node)
        else:
            print(f"Warning: No parser found for tag: {tag}")

    return ast_nodes
