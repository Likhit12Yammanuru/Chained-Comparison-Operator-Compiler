import subprocess
import json
from lexer import tokenize
from parser import Parser
from semantic import SymbolTable, SemanticAnalyzer
from codegen import CodeGenerator
import re

# --------------------------
# JS Runner
# --------------------------
def run_js(js_code, plain_symbols):
    """
    plain_symbols: dict mapping name -> raw python value (int/float/str/bool/None)
    We use json.dumps to safely serialize values into JS literals (true/false/null, numbers, strings).
    """
    vars_code_lines = []
    for k, v in plain_symbols.items():
        # json.dumps gives valid JS literals: true/false/null, numbers, and quoted strings
        js_literal = json.dumps(v)
        vars_code_lines.append(f"let {k} = {js_literal};")
    vars_code = "\n".join(vars_code_lines)

    full_code = vars_code + f"\nconsole.log({js_code});"
    try:
        result = subprocess.run(
            ["node", "-e", full_code],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        # return stderr to help debugging
        return f"JS Runtime Error: {e.stderr.strip()}"

# --------------------------
# REPL
# --------------------------
def main():
    print("=== Chained Comparison Compiler REPL ===")
    print("Supports assignments like x = 20")
    print("Type 'exit' to quit.\n")

    sym_table = SymbolTable()
    # Define some initial variables with types so analyzer can use them
    sym_table.define("x", 5, "int")
    sym_table.define("y", 10, "int")
    sym_table.define("a", 2, "int")
    sym_table.define("b", 3, "int")

    while True:
        try:
            expr = input(">>> ").strip()
            if expr.lower() == "exit":
                print("Exiting REPL...")
                break

            # Handle variable assignment
            assignment_match = re.match(r'^(?:(int|float|double|long|char|string|bool)\s+)?(\w+)\s*=\s*(.+)$', expr)
            if assignment_match:
                dtype = assignment_match.group(1)  # optional explicit dtype (may be None)
                var_name = assignment_match.group(2)
                value_expr = assignment_match.group(3)

                # Parse the value expression
                tokens = tokenize(value_expr)
                parser = Parser(tokens)
                ast = parser.parse()

                analyzer = SemanticAnalyzer(sym_table)
                result_type = analyzer.analyze(ast)

                # If user provided an explicit dtype, prefer it (basic check)
                if dtype:
                    result_type = dtype

                generator = CodeGenerator(ast)
                py_code = generator.to_python()

                # Prepare plain runtime environment for eval: name -> raw value
                runtime_env = {k: v['value'] for k, v in sym_table.symbols.items()}

                try:
                    value = eval(py_code, {}, runtime_env)
                except Exception as e:
                    print(f"Python Runtime Error evaluating assignment expression: {e}")
                    continue

                # Store into symbol table with both value and inferred/declared type
                sym_table.define(var_name, value, result_type)
                print(f"{var_name} = {value} ({result_type})")
                continue

            # Otherwise, normal expression evaluation
            tokens = tokenize(expr)
            parser = Parser(tokens)
            ast = parser.parse()

            analyzer = SemanticAnalyzer(sym_table)
            result_type = analyzer.analyze(ast)

            generator = CodeGenerator(ast)
            py_code = generator.to_python()
            js_code = generator.to_javascript()

            # Prepare plain runtime environment for eval and JS runner
            runtime_env = {k: v['value'] for k, v in sym_table.symbols.items()}

            # Evaluate Python
            try:
                py_result = eval(py_code, {}, runtime_env)
            except Exception as e:
                py_result = f"Python Runtime Error: {e}"

            # Evaluate JS (pass plain values)
            js_result = run_js(js_code, runtime_env)

            print(f"AST: {ast}")
            print(f"Python code: {py_code}")
            print(f"Python result: {py_result} (type: {result_type})")
            print(f"JavaScript code: {js_code}")
            print(f"JavaScript result: {js_result}")

        except Exception as e:
            print(f"Error: {e}")
    

if __name__ == "__main__":
    main()
