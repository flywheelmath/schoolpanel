from compiler import compile
from visitors.render_tex import RenderTexVisitor

test_markdown = """
::: graph {xmin: -10, xmax: 10, ymin: -10, ymax: 10, scale: 0.5}
plot: "y < 2*x + 1" {color: "green", label: "Linear"}
plot: "y >= x^2 - 5" {color: "blue", label: "Parabola"}
plot: "x > 3.5" {color: "red"}
plot: "x^2 + y^2 <= 9" {color: "red", label: "Circle"}
point: "(2, 2)" {label: "Origin-ish", color: "black"}
point: "(-5, 5)" {label: "Point B", color: "purple"}
plot: "cos(t), sin(t)" {domain: "0 <= t <= 3.14"}
:::
"""

def run_comprehensive_test():
    print("--- Starting Compiler Pipeline ---")
    try:
        ast = compile(test_markdown)
        
        renderer = RenderTexVisitor()
        renderer.visit(ast)
        
        print(renderer.get_result())
        
        result = renderer.get_result()
        if "\\begin{tikzpicture}" in result and "\\fill" in result:
            print("\nSUCCESS: Pipeline generated valid TikZ code.")
        else:
            print("\nFAILURE: Pipeline output is missing key components.")
            
    except Exception as e:
        print(f"\nCRITICAL FAILURE: Pipeline crashed during compilation: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_comprehensive_test()
