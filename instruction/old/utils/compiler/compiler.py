from core.ast_models import CompositeBlock, GraphBlock, TableBlock, TaskBlock
from core.lexer import lex_markdown
from core.parser import parse_chunks
from core.state import CounterRegistry
from visitors.compute import ComputationVisitor
from visitors.layout import LayoutVisitor
from visitors.numbering import NumberingVisitor
from visitors.table_layout import TableLayoutVisitor

def compile(raw_md: str, is_recursive=False):
    raw_chunks = lex_markdown(raw_md)
    children = parse_chunks(raw_chunks)
    
    if is_recursive:
        return children

    ast = CompositeBlock(children=children)

    registry = CounterRegistry()
    NumberingVisitor(registry).visit(ast)
    LayoutVisitor().visit(ast)
    ComputationVisitor().visit(ast)
    TableLayoutVisitor().visit(ast)

    return ast
