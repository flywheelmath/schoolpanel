from core.lexer import lex_markdown
from core.parser import parse_chunks

def compile(raw_md: str):
    raw_chunks = lex_markdown(raw_md)
    ast = parse_chunks(raw_chunks)

    return ast

