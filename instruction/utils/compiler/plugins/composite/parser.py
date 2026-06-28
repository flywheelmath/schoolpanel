from core.ast_models import CompositeBlock
from core.lexer import lex_markdown
from core.parser import parse_chunks

def parse_composite(body: str, config_str: str) -> CompositeBlock:
    inner_chunks = lex_markdown(body)
    children = parse_chunks(inner_chunks)
    return CompositeBlock(children=children)
