from plugins.tasks.parser import parse_task
#from .plugins.graphs import parse_graph
#from .plugins.tables import parse_table

def parse_chunks(raw_chunks: list):
    ast_nodes = []

    dispatch_map = {
        "tasks": parse_task,
#        "graph": parse_graph,
#        "tables": parse_table
    }

    for chunk in raw_chunks:
        tag = chunk.get("tag")
        if tag in dispatch_map:
            node = dispatch_map[tag](chunk["body"], chunk["config"])
            ast_nodes.append(node)
        else:
            print(f"Warning: No parser found for tag: {tag}")

    return ast_nodes
