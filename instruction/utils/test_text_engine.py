# test_text_engine.py
from core.parser import Tokenizer, Parser
from visitors.tex import RenderTeXVisitor

test_md = r"""
::: task {label="4."}
# Advanced Markdown and Special Character Stress Test

Welcome to the ultimate test of the pipeline engine. Here is a baseline horizontal rule:

---

Let's verify that inline verbatim code blocks shield characters from the TeX escaper:
We want `A & B` to have an escaped ampersand, but `x_i` shouldn't get an escaped underscore. 
Even a code block containing **bold** text inside backticks, like `**don't change me**`, should remain unmutated text.

## Link, URL, and Contact Detection Pass
1. Here is a named markdown link: Check out [SchoolPanel](https://schoolpanel.com/dashboard?user=math&dept=lead).
2. Here is a bare URL with active query parameters: https://baltimorecitypublicschools.org/search?q=curriculum&grade=9
3. Drop an email link here to test the mailto wrapper: [contact_department@bcps.edu](mailto:contact_department@bcps.edu) for department questions.

## Multi-line Blockquote and Lazy Continuation Test
> This is the first line of an authoritative instructional rule block.
This second line doesn't have a leading chevron, but it belongs to the blockquote.
And this third line wraps it up nicely before a hard line break.

Back to a baseline text paragraph with standard straight quotes: "The root of a function is where f(x) = 0." We can also use double-dashes to render an em-dash like this--it looks much cleaner on paper.

## Mixed Nested List Continua
* This is an unordered item containing an explicit link [District Portal](http://district.domain/path)
* This is a multi-line bullet item
  and this line continues the same exact bullet item without closing the itemize environment prematurely
* The third bullet concludes the group.

1. Let's swap immediately into an ordered list.
2. Step two contains inline math \( y = mx + b \) and a trailing bare URL: https://desmos.com
   along with an indented lazy continuation line that must remain in the enumerate block.

Final line of text outside all structural containers.
:::
"""

print("=== PARSING & RENDERING ===")
parser = Parser(test_md)
tokens = Tokenizer(test_md).tokenize()
ast = parser.parse()

tex_engine = RenderTeXVisitor()
for node in ast:
    tex_engine.visit(node)

print(tex_engine.get_result())
