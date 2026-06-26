from core.lexer import lex_markdown
from core.parser import parse_chunks
from core.state import CounterRegistry
from visitors.layout import LayoutVisitor
from visitors.numbering import NumberingVisitor

def compile(raw_md: str):
    raw_chunks = lex_markdown(raw_md)
    ast = parse_chunks(raw_chunks)

    registry = CounterRegistry()

    NumberingVisitor(registry).visit(ast)
    LayoutVisitor().visit(ast)

    return ast
