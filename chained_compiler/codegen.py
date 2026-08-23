import json
from parser import NumberNode, IdentifierNode, BinaryOpNode, StringNode, CharNode

# --------------------------
# Helper function to map values/types for Python and JS
# --------------------------
def format_value(value, dtype, target="js"):
    # value is a Python native (int/float/str/bool)
    if target == "js":
        # json.dumps safely encodes strings, booleans, null, numbers
        return json.dumps(value)
    else:  # python
        # repr produces valid Python literal for strings and numbers
        return repr(value)

# --------------------------
# Code Generator Class
# --------------------------

class CodeGenerator:
    def __init__(self, ast):
        self.ast = ast

    # Generate Python code
    def to_python(self, node=None):
        if node is None:
            node = self.ast

        if isinstance(node, BinaryOpNode) and node.op in {'<','>','<=','>=','==','!='}:
            # Flatten chained comparisons
            exprs = []

            def flatten_chain(n):
                if isinstance(n.left, BinaryOpNode) and n.left.op in {'<','>','<=','>=','==','!='}:
                    flatten_chain(n.left)
                    exprs.append(f"{self.to_python(n.left.right)} {n.op} {self.to_python(n.right)}")
                else:
                    exprs.append(f"{self.to_python(n.left)} {n.op} {self.to_python(n.right)}")

            flatten_chain(node)
            return " and ".join(f"({e})" for e in exprs)

        elif isinstance(node, NumberNode):
            return format_value(node.value, node.type_name, target="py")

        elif isinstance(node, StringNode):
            return format_value(node.value, node.type_name, target="py")

        elif isinstance(node, CharNode):
            return format_value(node.value, node.type_name, target="py")

        elif isinstance(node, IdentifierNode):
            return node.name

        else:
            # Arithmetic operations
            left_code = self.to_python(node.left)
            right_code = self.to_python(node.right)
            return f"({left_code} {node.op} {right_code})"

    # Generate JS code with proper chained comparisons
    def to_javascript(self, node=None):
        if node is None:
            node = self.ast

        if isinstance(node, BinaryOpNode):
            if node.op in {'<','>','<=','>=','==','!='}:
                # Flatten all chained comparisons into JS && form
                exprs = []

                def flatten_chain(n):
                    if isinstance(n.left, BinaryOpNode) and n.left.op in {'<','>','<=','>=','==','!='}:
                        flatten_chain(n.left)
                        exprs.append(f"{self.to_javascript(n.left.right)} {n.op} {self.to_javascript(n.right)}")
                    else:
                        exprs.append(f"{self.to_javascript(n.left)} {n.op} {self.to_javascript(n.right)}")

                flatten_chain(node)
                return " && ".join(f"({e})" for e in exprs)

            else:
                # Arithmetic
                left_code = self.to_javascript(node.left)
                right_code = self.to_javascript(node.right)
                return f"({left_code} {node.op} {right_code})"

        elif isinstance(node, NumberNode):
            # JS numeric literal (ints/floats)
            return format_value(node.value, node.type_name, target="js")
        elif isinstance(node, StringNode):
            return format_value(node.value, node.type_name, target="js")
        elif isinstance(node, CharNode):
            return format_value(node.value, node.type_name, target="js")
        elif isinstance(node, IdentifierNode):
            return node.name
        else:
            raise TypeError(f"Unknown AST node type: {type(node)}")


# --------------------------
# Test Section
# --------------------------
if __name__ == "__main__":
    from lexer import tokenize
    from parser import Parser

    examples = [
        "1 < x < 5",
        "a + 2 < b * 3",
        "(x + 3) <= y",
        "x / 2 + y > 7",
        "'a' == c",
        '"hello" == name'
    ]

    for expr in examples:
        print("\nExpression:", expr)
        tokens = tokenize(expr)
        parser = Parser(tokens)
        ast = parser.parse()
        print("AST:", ast)

        generator = CodeGenerator(ast)
        py_code = generator.to_python()
        js_code = generator.to_javascript()
        print("Python code:", py_code)
        print("JavaScript code:", js_code)
