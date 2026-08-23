from parser import NumberNode, IdentifierNode, BinaryOpNode, StringNode, CharNode

# --------------------------
# Symbol Table
# --------------------------
class SymbolTable:
    def __init__(self):
        self.symbols = {}  # name -> {'type': dtype, 'value': val}

    def define(self, name, value=None, dtype=None):
        self.symbols[name] = {'type': dtype, 'value': value}

    def exists(self, name):
        return name in self.symbols

    def get(self, name):
        if not self.exists(name):
            raise NameError(f"Variable '{name}' is not defined.")
        return self.symbols[name]['value']

    def get_type(self, name):
        if not self.exists(name):
            raise NameError(f"Variable '{name}' is not defined.")
        return self.symbols[name]['type']

    def set(self, name, value):
        if not self.exists(name):
            raise NameError(f"Variable '{name}' is not defined.")
        self.symbols[name]['value'] = value


# --------------------------
# Semantic Analyzer
# --------------------------
NUMERIC_TYPES = {"int", "float", "double", "long"}
OTHER_TYPES = {"char", "string", "bool"}

class SemanticAnalyzer:
    def __init__(self, symbol_table):
        self.symbol_table = symbol_table

    def analyze(self, node):
        # If node knows its type (literals), prefer that
        if isinstance(node, NumberNode):
            return node.type_name
        if isinstance(node, StringNode):
            return node.type_name
        if isinstance(node, CharNode):
            return node.type_name

        if isinstance(node, IdentifierNode):
            dtype = self.symbol_table.get_type(node.name)
            return dtype

        if isinstance(node, BinaryOpNode):
            left_type = self.analyze(node.left)
            right_type = self.analyze(node.right)
            op = node.op

            # Arithmetic
            if op in {'+', '-', '*', '/'}:
                if left_type not in NUMERIC_TYPES or right_type not in NUMERIC_TYPES:
                    raise TypeError(f"Arithmetic '{op}' requires numeric types, got {left_type} and {right_type}")

                # ---- Special rule: division always produces a floating type ----
                if op == '/':
                    # If either side is double -> double; otherwise float
                    if "double" in (left_type, right_type):
                        return "double"
                    else:
                        return "float"

                # ---- Other arithmetic ops: usual promotion ----
                if "double" in (left_type, right_type):
                    return "double"
                elif "float" in (left_type, right_type):
                    return "float"
                elif "long" in (left_type, right_type):
                    return "long"
                else:
                    return "int"

            # Comparison
            elif op in {'<', '<=', '>', '>=', '==', '!='}:
                # If left is a comparison (chained)
                if isinstance(node.left, BinaryOpNode) and node.left.op in {'<', '<=', '>', '>=', '==', '!='}:
                    left_type = self.analyze(node.left)   # capture left type
                    right_type = self.analyze(node.right)
                    if right_type not in NUMERIC_TYPES:
                        raise TypeError(f"Cannot compare numeric to {right_type}")
                    return "bool"
                else:
                    left_type = self.analyze(node.left)
                    right_type = self.analyze(node.right)
                    # numeric-numeric comparisons
                    if left_type in NUMERIC_TYPES and right_type in NUMERIC_TYPES:
                        return "bool"
                    # same-type comparisons for strings/chars/bools
                    elif left_type == right_type:
                        return "bool"
                    else:
                        raise TypeError(f"Cannot compare different types: {left_type} {op} {right_type}")

        raise TypeError(f"Unsupported node type for semantic analysis: {type(node)}")
