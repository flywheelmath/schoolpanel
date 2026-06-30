# test_text_engine.py
from core.parser import Tokenizer, Parser
from visitors.tex import RenderTeXVisitor

test_md = r"""
# Section 1

::: task {label="3."}
Here is a comprehensive test of the **Text Rendering Engine**.

<v-click>This sentence should appear, but the Slidev tags should vanish.</v-click>

Let's test special characters outside of math mode:
Fifty % of the time, it works 100% of the time!
We know that A & B are sets, and #1 is the best.
Watch out for underscores_outside_math and {curly braces}.

But inside math mode, these exact same characters must remain untouched:
Let \(x_1\) be a variable, and consider the matrix:
\[
\begin{bmatrix}
a & b \\
c & d_{2}
\end{bmatrix}
\]

## Don't go chasing waterfalls

*Here* is an italicized word, and ==here is a highlighted word==.

### test this out
not sure

We're #1 or are we.

> This is a scaffolding hint blockquote.
> So is this.

Here is a list of things to remember:
- First item with inline math \(y_2\)
- Second item with **bold text**
* Third item using an asterisk
testing

testing2

Here is a numbered list:
1. option A

> test
test

1. option B
2. option C
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
