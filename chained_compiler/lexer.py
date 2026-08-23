import re
from typing import List, Tuple

# A token is represented as a tuple (TYPE, VALUE)
Token = Tuple[str, str]

# Define token patterns for our mini language
TOKEN_SPEC = [
    ("TYPE",     r"\b(int|float|double|long|char|string|bool)\b"),  # new
    ("NUMBER",   r"\d+(\.\d+)?([fFlL])?"),          # Integer or decimal number
    ("CHAR",     r"'.'"),          # single character
    ("STRING",   r'"[^"]*"'),      # string literal
    ("ASSIGN",   r"="),                    # Assignment =
    ("LE",       r"<="),                   # Less than or equal
    ("GE",       r">="),                   # Greater than or equal
    ("EQ",       r"=="),                   # Equal
    ("NE",       r"!="),                   # Not equal
    ("LT",       r"<"),                    # Less than
    ("GT",       r">"),                    # Greater than
    ("PLUS",     r"\+"),                   # Addition +
    ("MINUS",    r"-"),                    # Subtraction -
    ("MUL",      r"\*"),                   # Multiplication *
    ("DIV",      r"/"),                    # Division /
    ("LPAREN",   r"\("),                   # Left parenthesis (
    ("RPAREN",   r"\)"),                   # Right parenthesis )
    ("ID",       r"[A-Za-z_][A-Za-z0-9_]*"),  # Identifier (variables)
    ("SKIP",     r"[ \t]+"),               # Skip spaces and tabs
    ("NEWLINE",  r"[\r\n]+"),              # Newlines
    ("MISMATCH", r"."),                    # Any other character (error)
]

# Build a combined regex
token_regex = "|".join(f"(?P<{name}>{pattern})" for name, pattern in TOKEN_SPEC)
master_pat = re.compile(token_regex)

def tokenize(code: str) -> List[Token]:
    """Convert input code string into a list of tokens."""
    tokens: List[Token] = []

    for mo in master_pat.finditer(code):
        kind = mo.lastgroup
        value = mo.group()

        if kind in {"SKIP", "NEWLINE"}:
            continue
        elif kind == "MISMATCH":
            raise SyntaxError(f"Unexpected character {value!r}")
        else:
            tokens.append((kind, value))

    return tokens


# Example usage
if __name__ == "__main__":
    sample_code = """
    x = 5
    1 < x < 10 + y
    (x + 3) <= 15
    """

    print("Input code:")
    print(sample_code)
    print("\nTokens:")
    for token in tokenize(sample_code):
        print(token)
