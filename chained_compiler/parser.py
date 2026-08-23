from lexer import tokenize

# --------------------------
# AST Node Classes
# --------------------------

class NumberNode:
    def __init__(self, value, type_name="int"):
        # value is Python int or float
        self.value = value
        self.type_name = type_name  # 'int' or 'double' (treat double as float)
    def __repr__(self):
        return f"NumberNode({self.value!r}, {self.type_name})"

class IdentifierNode:
    def __init__(self, name):
        self.name = name
    def __repr__(self):
        return f"IdentifierNode({self.name})"

class StringNode:
    def __init__(self, value, type_name="string"):
        self.value = value  # Python str
        self.type_name = type_name
    def __repr__(self):
        return f"StringNode({self.value!r}, {self.type_name})"

class CharNode:
    def __init__(self, value, type_name="char"):
        self.value = value  # single-character Python str
        self.type_name = type_name
    def __repr__(self):
        return f"CharNode({self.value!r}, {self.type_name})"

class BinaryOpNode:
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right
    def __repr__(self):
        return f"BinaryOpNode({self.left}, '{self.op}', {self.right})"

# --------------------------
# Parser
# --------------------------

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    # peek at the current token
    def peek(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    # consume the current token and move to next
    def consume(self):
        token = self.peek()
        if token:
            self.pos += 1
        return token

    # Entry point for parsing expressions
    def parse(self):
        return self.parse_comparison()

    # Parse comparison chains: 1 < x < 5
    def parse_comparison(self):
        left = self.parse_arith()
        comparisons = []

        while self.peek() and self.peek()[0] in {'LT','LE','GT','GE','EQ','NE'}:
            op = self.consume()[1]
            right = self.parse_arith()
            comparisons.append((op, right))

        if comparisons:
            node = left
            for op, right in comparisons:
                node = BinaryOpNode(node, op, right)
            return node
        return left

    # Parse arithmetic expressions: +, -
    def parse_arith(self):
        node = self.parse_term()
        while self.peek() and self.peek()[0] in {'PLUS','MINUS'}:
            op = self.consume()[1]
            right = self.parse_term()
            node = BinaryOpNode(node, op, right)
        return node

    # Parse terms: *, /
    def parse_term(self):
        node = self.parse_factor()
        while self.peek() and self.peek()[0] in {'MUL','DIV'}:
            op = self.consume()[1]
            right = self.parse_factor()
            node = BinaryOpNode(node, op, right)
        return node

    # Parse numbers, identifiers, parentheses, strings, chars
    def parse_factor(self):
        token = self.consume()
        if token is None:
            raise SyntaxError("Unexpected end of input")

        tok_type, tok_value = token

        # NUMBER: token value from lexer is the matched substring (digits or digits with dot)
        if tok_type == 'NUMBER':
            # Check for suffix
            suffix = ''
            if tok_value[-1] in 'fFlL':
                suffix = tok_value[-1]
                tok_value = tok_value[:-1]  # strip suffix

            if '.' in tok_value:
                val = float(tok_value)
                type_name = "float" if suffix.lower() == 'f' else "double"
            else:
                val = int(tok_value)
                type_name = "long" if suffix.lower() == 'l' else "int"

            return NumberNode(val, type_name)

        elif tok_type == 'CHAR':
            # tok_value like: "'a'". Strip surrounding single quotes
            if len(tok_value) >= 3 and tok_value[0] == "'" and tok_value[-1] == "'":
                ch = tok_value[1:-1]
                if len(ch) != 1:
                    raise SyntaxError("CHAR token must be a single character")
                return CharNode(ch, "char")
            else:
                raise SyntaxError("Malformed CHAR token")

        elif tok_type == 'STRING':
            # tok_value like: '"hello"'. Strip surrounding double quotes
            if len(tok_value) >= 2 and tok_value[0] == '"' and tok_value[-1] == '"':
                s = tok_value[1:-1]
                return StringNode(s, "string")
            else:
                raise SyntaxError("Malformed STRING token")

        elif tok_type == 'ID':
            return IdentifierNode(tok_value)

        elif tok_type == 'LPAREN':
            node = self.parse_comparison()
            if self.peek() and self.peek()[0] == 'RPAREN':
                self.consume()
                return node
            else:
                raise SyntaxError("Expected closing parenthesis")
        else:
            raise SyntaxError(f"Unexpected token: {token}")

# --------------------------
# Test Section
# --------------------------

if __name__ == "__main__":
    # Example expressions
    examples = [
        "1 < x < 5",
        "a + 2 < b * 3",
        "(x + 3) <= 15",
        "x / 2 + y > 7",
        "x = 'a'",
        's = "hello"'
    ]

    for expr in examples:
        print("\nExpression:", expr)
        tokens = tokenize(expr)
        print("Tokens:", tokens)
        parser = Parser(tokens)
        ast = parser.parse()
        print("AST:", ast)
