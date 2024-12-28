import os
import sys
import re
import subprocess

# Keywords and their mappings to C++
KEYWORDS = {
    "fick": "void",  # Function keyword
    "dumb": "auto",  # Variable declaration
    "maybe": "if",   # Conditional
    "bruh": "return",  # Return statement
    "do-it-again": "for",  # Loop keyword
    "throw": "std::cout <<"  # Print statement
}

# Map variable types for susScript
TYPES = {
    "int": "int",  # Integer type
    "float": "float",  # Floating-point type
    "string": "std::string",  # String type
    "bool": "bool"  # Boolean type
}

def lex(source_code):
    """Tokenizes the source code."""
    tokens = []
    token_spec = [
        ("NUMBER", r"\d+(\.\d+)?"),  # Numeric literals
        ("STRING", r'"[^"]*"'),  # String literals
        ("IDENTIFIER", r"[a-zA-Z_]\w*"),  # Identifiers
        ("ASSIGN", r"="),  # Assignment operator
        ("SEMI", r";"),  # Semicolon
        ("LPAREN", r"\("),  # Left parenthesis
        ("RPAREN", r"\)"),  # Right parenthesis
        ("LBRACE", r"\{"),  # Left brace
        ("RBRACE", r"\}"),  # Right brace
        ("SKIP", r"[ \t]+"),  # Skip over spaces and tabs
        ("MISMATCH", r"."),  # Any other character
    ]
    tok_regex = "|".join(f"(?P<{pair[0]}>{pair[1]})" for pair in token_spec)
    for mo in re.finditer(tok_regex, source_code):
        kind = mo.lastgroup
        value = mo.group()
        if kind == "NUMBER":
            value = float(value) if '.' in value else int(value)
        elif kind == "IDENTIFIER" and value in KEYWORDS:
            kind = value.upper()
        elif kind == "SKIP":
            continue
        elif kind == "MISMATCH":
            raise RuntimeError(f"{value!r} unexpected")
        tokens.append((kind, value))
    return tokens

def parse(tokens):
    """Parses tokens into an Abstract Syntax Tree (AST)."""
    ast = []
    i = 0


    def parse_expression():
        """Parses an expression, including function calls and arithmetic."""
        nonlocal i
        expr = []
        
        while i < len(tokens):
            token = tokens[i]
            
            if token["type"] == "IDENTIFIER":
                # Check if it's a function call (like add())
                if tokens[i]["value"] in KEYWORDS:  # Match for function names like 'fick'
                    func_name = tokens[i]["value"]
                    i += 1  # Skip the function name
                    if tokens[i]["type"] == "LPAREN":
                        args = []
                        i += 1  # Skip '('
                        while tokens[i]["type"] != "RPAREN":
                            args.append(parse_expression())  # Parse arguments as expressions
                            if tokens[i]["type"] == "COMMA":
                                i += 1  # Skip comma
                        i += 1  # Skip ')'
                        expr.append(f'{func_name}({", ".join(args)})')  # Build the function call expression
                        continue  # Skip to the next token
                else:
                    expr.append(token["value"])  # Regular identifier (like a variable)
            
            elif token["type"] == "NUMBER":
                expr.append(token["value"])  # Handle numbers
            elif token["type"] == "STRING":
                expr.append(token["value"])  # Handle strings
            elif token["type"] == "OP":
                expr.append(token["value"])  # Handle operators
            else:
                break  # Stop parsing when we hit something unexpected
            
            i += 1
            if tokens[i]["type"] in {"SEMI", "COMMA", "RPAREN"}:
                break  # End of expression
            
        return " ".join(expr)  # Return the expression as a single string

    def parse_variable_declaration():
        """Parses a variable declaration."""
        nonlocal i
        var_type = tokens[i]["value"]  # Get the variable type (like 'dumb')
        i += 1
        var_name = tokens[i]["value"]  # Get the variable name (like 'result')
        i += 1
        value = None
        if tokens[i]["type"] == "ASSIGN":
            value = parse_expression()  # Parse the expression (e.g., function call like add(5, 10))
        if tokens[i]["type"] != "SEMI":
            raise SyntaxError(f"Missing ';' after variable declaration for {var_name}")
        i += 1
        return {"type": "VariableDeclaration", "var_type": var_type, "name": var_name, "value": value}



    def parse_function_declaration():
        nonlocal i
        i += 1  # Skip 'fick'
        func_name = tokens[i]["value"]  # Get function name
        i += 1
        if tokens[i]["type"] != "LPAREN":
            raise SyntaxError("Expected '(' after function name")
        i += 1
        params = []
        while tokens[i]["type"] != "RPAREN":
            if tokens[i]["type"] == "IDENTIFIER" and tokens[i]["value"] == "dumb":
                # Parse parameter type and name
                param_type = tokens[i]["value"]  # Get 'dumb'
                i += 1
                param_name = tokens[i]["value"]  # Get parameter name
                params.append({"type": param_type, "name": param_name})
                i += 1
                if tokens[i]["type"] == "COMMA":
                    i += 1  # Skip the comma to continue parsing next parameter
            else:
                raise SyntaxError("Invalid parameter in function declaration")
        i += 1  # Skip ')'
        if tokens[i]["type"] != "LBRACE":
            raise SyntaxError("Expected '{' after function declaration")
        i += 1
        body = []
        while tokens[i]["type"] != "RBRACE":
            body.append(parse_statement())  # Parse function body
        i += 1
        return {"type": "FunctionDeclaration", "name": func_name, "params": params, "body": body}

    def parse_function_call():
        nonlocal i
        func_name = tokens[i]["value"]  # Get the function name
        i += 1
        if tokens[i]["type"] != "LPAREN":
            raise SyntaxError(f"Expected '(' after function name: {func_name}")
        i += 1
        args = []
        while tokens[i]["type"] != "RPAREN":
            if tokens[i]["type"] == "IDENTIFIER":
                args.append(tokens[i]["value"])  # Capture argument name or value
                i += 1
                if tokens[i]["type"] == "COMMA":
                    i += 1  # Skip comma
            else:
                raise SyntaxError("Invalid argument in function call")
        i += 1  # Skip ')'
        return {"type": "FunctionCall", "name": func_name, "args": args}

    def parse_statement():
        nonlocal i
        if tokens[i]["type"] == "IDENTIFIER" and tokens[i]["value"] == "dumb":
            return parse_variable_declaration()
        elif tokens[i]["type"] == "IDENTIFIER" and tokens[i]["value"] == "throw":
            i += 1
            value = tokens[i]["value"]  # Get value to print
            i += 1
            if tokens[i]["type"] != "SEMI":
                raise SyntaxError("Missing ';' after throw statement")
            i += 1
            return {"type": "PrintStatement", "value": value}
        elif tokens[i]["type"] == "IDENTIFIER" and tokens[i]["value"] == "fick":
            return parse_function_declaration()
        elif tokens[i]["type"] == "IDENTIFIER" and tokens[i]["value"] != "bruh":
            return parse_function_call()  # Detect and parse function calls
        elif tokens[i]["type"] == "IDENTIFIER" and tokens[i]["value"] == "bruh":
            i += 1
            value = parse_expression()  # Handle return expressions
            if tokens[i]["type"] != "SEMI":
                raise SyntaxError("Missing ';' after return statement")
            i += 1
            return {"type": "ReturnStatement", "value": value}
        else:
            raise SyntaxError(f"Unknown statement: {tokens[i]['value']}")

    while i < len(tokens):
        ast.append(parse_statement())  # Parse each statement into the AST

    return ast

def generate_code(ast):
    """Generates C++ code from the AST."""
    cpp_code = "#include <iostream>\n#include <string>\nusing namespace std;\n\n"

    # Generate function declarations first (outside of main)
    function_declarations = []
    for node in ast:
        if node["type"] == "FunctionDeclaration":
            params = ", ".join(
                [f'{TYPES.get(p["type"], "auto")} {p["name"]}' for p in node["params"]]
            )
            function_declarations.append(f'void {node["name"]}({params}) {{\n')
            function_declarations.append(generate_code(node["body"]))
            function_declarations.append("}\n")

    # Append function declarations before the main function
    cpp_code += "".join(function_declarations)

    # Main function logic
    cpp_code += "int main() {\n"
    for node in ast:
        if node["type"] == "VariableDeclaration":
            cpp_code += f'{TYPES.get(node["var_type"], "auto")} {node["name"]}'
            if node["value"] is not None:
                cpp_code += f' = {node["value"]}'
            cpp_code += ";\n"
        elif node["type"] == "PrintStatement":
            cpp_code += f'std::cout << {node["value"]} << std::endl;\n'
        elif node["type"] == "FunctionCall":
            args = ", ".join(node["args"])
            cpp_code += f'{node["name"]}({args});\n'
        elif node["type"] == "ReturnStatement":
            cpp_code += f'bruh {node["value"]};\n'
    cpp_code += "return 0;\n}\n"
    return cpp_code

def main():
    if len(sys.argv) != 2:
        print("Usage: python compiler.py <input_file.sus>")
        sys.exit(1)

    input_file = sys.argv[1]
    if not input_file.endswith(".sus"):
        print("Error: Input file must have a .sus extension")
        sys.exit(1)

    with open(input_file, "r") as f:
        source_code = f.read()

    print("Lexing the code...")
    tokens = lex(source_code)

    print("Parsing the tokens...")
    ast = parse(tokens)

    print("Generating code...")
    cpp_code = generate_code(ast)

    with open("output.cpp", "w") as f:
        f.write(cpp_code)

    print("Generated C++ code written to output.cpp")

    print("Compiling the code...")
    result = subprocess.run(
        ["g++", "-o", "output", "output.cpp"],
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        print("Compilation successful!")
        print("Running the executable...")
        os.system("output")
        os.remove("output.cpp")
        os.remove("output.exe")

if __name__ == "__main__":
    main()
