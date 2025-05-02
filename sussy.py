import os
import sys
import re
import subprocess
from termcolor import cprint


# Keywords and their mappings to C++
KEYWORDS = {
    "func": "void",  # Function keyword
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
        ("DOT", r"\."),  # Dot operator (for object access)
        ("OP", r"[+\-*/<>]"),  # Added '<' and '>' here
        ("SKIP", r"[ \t]+"),  # Skip over spaces and tabs
        ("MISMATCH", r"."),  # Any other character (for error handling)
    ]


    tok_regex = "|".join(f"(?P<{pair[0]}>{pair[1]})" for pair in token_spec)
    for mo in re.finditer(tok_regex, source_code):
        kind = mo.lastgroup
        value = mo.group()
        if kind == "NUMBER":
            value = float(value) if '.' in value else int(value)
        elif kind == "IDENTIFIER" and value in KEYWORDS:
            pass  # Skip keywords   
        elif kind == "SKIP":
            continue
        elif kind == "MISMATCH":
            raise RuntimeError(f"{value!r} unexpected")
        tokens.append({"type": kind, "value": value}) 
    return tokens

def parse(tokens):
    """Parses tokens into an Abstract Syntax Tree (AST)."""
    ast = []
    i = 0


    def parse_expression(start):
        """Parses identifiers, numbers, strings, function calls, and dot access."""
        i = start

        if i >= len(tokens):
            raise SyntaxError("Unexpected end of input in expression")

        tok = tokens[i]

        # Handle identifiers and potential function calls or dotted access
        if tok["type"] == "IDENTIFIER":
            name_parts = [tok["value"]]
            i += 1

            # Handle dotted identifiers like math.sqrt
            while i < len(tokens) and tokens[i]["type"] == "DOT":
                i += 1  # skip '.'
                if i < len(tokens) and tokens[i]["type"] == "IDENTIFIER":
                    name_parts.append(tokens[i]["value"])
                    i += 1
                else:
                    raise SyntaxError("Expected identifier after '.'")

            # Handle function calls: math.sqrt(...)
            if i < len(tokens) and tokens[i]["type"] == "LPAREN":
                i += 1  # skip '('
                args = []
                while i < len(tokens) and tokens[i]["type"] != "RPAREN":
                    arg, i = parse_expression(i)
                    args.append(str(arg))
                    if i < len(tokens) and tokens[i]["type"] == "COMMA":
                        i += 1  # skip comma
                if i >= len(tokens) or tokens[i]["type"] != "RPAREN":
                    raise SyntaxError("Missing ')' in function call")
                i += 1  # skip ')'
                return (f'{".".join(name_parts)}({", ".join(args)})', i)
            else:
                return (".".join(name_parts), i)

        # Handle number literals
        elif tok["type"] == "NUMBER":
            i += 1
            return (tok["value"], i)

        # Handle string literals
        elif tok["type"] == "STRING":
            i += 1
            return (f'"{tok["value"]}"', i)

        else:
            raise SyntaxError(f"Unexpected token in expression: {tok['value']}")

    def parse_variable_declaration():
        """Parses a variable declaration."""
        nonlocal i
        var_type = tokens[i]["value"]  # Get the variable type (like 'dumb')
        i += 1
        var_name = tokens[i]["value"]  # Get the variable name (like 'result')
        i += 1
        value = None
        if tokens[i]["type"] == "ASSIGN":
            value = parse_expression(i)  # Parse the expression (e.g., function call like add(5, 10))
        if tokens[i]["type"] != "SEMI":
            raise SyntaxError(f"Missing ';' after variable declaration for {var_name}")
        i += 1
        return {"type": "VariableDeclaration", "var_type": var_type, "name": var_name, "value": value}



    def parse_function_declaration():
        """Parse a function declaration."""
        nonlocal i
        if tokens[i]["value"] == "func":
            i += 1  # Skip the 'func' keyword
            if tokens[i]["type"] != "IDENTIFIER":
                raise SyntaxError("Function name expected")
            func_name = tokens[i]["value"]
            i += 1
        
        # Ensure the next token is '(' for function parameters
        if tokens[i]["type"] != "LPAREN":
            raise SyntaxError("Expected '(' after function name")
        i += 1
        
        params = []
        while tokens[i]["type"] != "RPAREN":
            if tokens[i]["type"] != "IDENTIFIER":
                raise SyntaxError("Invalid parameter in function declaration")
            params.append(tokens[i]["value"])
            i += 1
            if tokens[i]["type"] == "COMMA":
                i += 1  # Skip the comma if there are multiple params
        
        if tokens[i]["type"] != "RPAREN":
            raise SyntaxError("Expected closing parenthesis in function declaration")
        i += 1  # Skip the closing parenthesis
        
        if tokens[i]["type"] != "LBRACE":
            raise SyntaxError("Expected '{' after function parameters")
        i += 1  # Skip the opening brace
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
            value,new_i = parse_expression(i)  # Accept full expression (e.g., sqrt(25))
            i = new_i  # Update index to the position after the expression
            if tokens[i]["type"] != "SEMI":
                cprint("SyntaxError: Missing ';' after throw statement", "red")
                sys.exit(1)
            i += 1
            return {"type": "PrintStatement", "value": value}

        elif tokens[i]["type"] == "IDENTIFIER" and tokens[i]["value"] == "func":
            return parse_function_declaration()
        
        elif tokens[i]["type"] == "IDENTIFIER" and tokens[i]["value"] == "bruh":
            i += 1
            value = parse_expression(i)  # Handle return expressions
            if tokens[i]["type"] != "SEMI":
                raise SyntaxError("Missing ';' after return statement")
            i += 1
            return {"type": "ReturnStatement", "value": value}
        elif tokens[i]["type"] == "IDENTIFIER" and tokens[i]["value"] == "import":
            i += 1
            if i >= len(tokens) or tokens[i]["type"] != "IDENTIFIER":
                cprint("ImportError: Expected package name after 'import'", "red")
                sys.exit(1)
            package_name = tokens[i]["value"]
            i += 1
            if i >= len(tokens) or tokens[i]["type"] != "SEMI":
                cprint("ImportError: Missing ';' after import statement", "red")
                sys.exit(1)
            i += 1

            # Compile the package if not already compiled
            package_path = f"packages/{package_name}.suspkg"
            if not os.path.exists(package_path):
                cprint(f"ImportError: Package '{package_name}' not found", "red")
                sys.exit(1)

            subprocess.run(["python", "sussy.py", package_path, "--as-lib"], check=True)

        elif tokens[i]["type"] == "IDENTIFIER" and tokens[i]["value"] != "bruh":
            return parse_function_call()  # Detect and parse function calls
        else:
            raise SyntaxError(f"Unknown statement: {tokens[i]['value']}")

    while i < len(tokens):
        ast.append(parse_statement())
    return ast

TYPES = {
    "number": "double",
    "string": "std::string",
    "auto": "auto"
}

def generate_cpp_from_node(node, indent="    "):
    if node["type"] == "VariableDeclaration":
        code = f'{indent}{TYPES.get(node["var_type"], "auto")} {node["name"]}'
        if node["value"] is not None:
            code += f' = {node["value"]}'
        return code + ";\n"

    elif node["type"] == "PrintStatement":
        return f'std::cout << {node["value"][1:-1]} << std::endl;\n'

    elif node["type"] == "FunctionCall":
        args = ", ".join(node["args"])
        return f'{indent}{node["name"]}({args});\n'

    elif node["type"] == "ReturnStatement":
        return f'{indent}return {node["value"]};\n'

    elif node["type"] == "ThrowStatement":
        value = node["value"]
        if value.startswith('"') and value.endswith('"'):
            value = value[1:-1]  # remove outer quotes
        value = value.replace('"', '\\"')  # escape inner quotes
        return f'{indent}throw std::runtime_error("{value}");\n'


    elif node["type"] == "ForLoop":
        code = f'{indent}for ({node["init"]}; {node["condition"]}; {node["increment"]}) {{\n'
        for stmt in node["body"]:
            code += generate_cpp_from_node(stmt, indent + "    ")
        code += f'{indent}}}\n'
        return code

    else:
        return f'{indent}// Unknown node type: {node["type"]}\n'

def generate_block(statements, indent="    "):
    return "".join(generate_cpp_from_node(stmt, indent) for stmt in statements)

def generate_code(ast):
    code = "#include <iostream>\n#include <string>\n#include <stdexcept>\nusing namespace std;\n\n"

    # Step 1: Add function declarations
    for node in ast:
        if node["type"] == "FunctionDeclaration":
            params = ", ".join([f'{TYPES.get(p["type"], "auto")} {p["name"]}' for p in node["params"]])
            code += f'void {node["name"]}({params}) {{\n'
            code += generate_block(node["body"], "    ")
            code += "}\n\n"

    # Step 2: Add main function
    code += "int main() {\n"
    code += "    try {\n"
    main_statements = [n for n in ast if n["type"] != "FunctionDeclaration"]
    code += generate_block(main_statements, "        ")
    code += "    } catch (const std::runtime_error& e) {\n"
    code += "        std::cerr << \"Runtime Error: \" << e.what() << std::endl;\n"
    code += "    }\n"
    code += "    return 0;\n"
    code += "}\n"

    return code

def main():
    # Default values
    input_file = None
    output_file = "output"
    compile = False
    is_lib = False
    show_help = False
    show_version = False

    args = sys.argv[1:]
    i = 0

    while i < len(args):
        arg = args[i]
        if arg in ("-h", "--help", "-?"):
            show_help = True
        elif arg in ("-v", "--version"):
            show_version = True
        elif arg in ("-c", "--compile"):
            compile = True
        elif arg == "--as-lib":
            is_lib = True
        elif arg == "-o":
            i += 1
            if i < len(args):
                output_file = args[i]
            else:
                print("Error: Missing output file name after '-o'")
                sys.exit(1)
        elif arg.endswith(".sus") or arg.endswith(".suspkg"):
            input_file = arg
        else:
            print(f"Unknown option: {arg}")
            sys.exit(1)
        i += 1

    # Handle help/version
    if show_help:
        print("Sussy Compiler v1.1.5-alpha")
        print("A compiler for susScript, a programming language for the sussy generation.")
        print("-------------------------------")
        print("Usage: sussy [options] <input_file.sus>")
        print("-------------------------------")
        print("Options:")
        print("  -h, --help, -?     Show this help message")
        print("  -v, --version      Show version information")
        print("  -c, --compile      Compile to output binary")
        print("  -o <file>          Set output file name")
        print("  -as-lib            Make it a libary")
        print("-------------------------------")
        sys.exit(0)

    if show_version:
        print("Sussy Compiler v1.1.5-alpha")
        sys.exit(0)

    if not input_file:
        print("Error: No input file provided")
        sys.exit(1)

    # Add platform-dependent binary extension
    if compile:
        if os.name == "nt":
            binending = ".exe"
        else:
            binending = ""
        output_file += binending

    with open(input_file, "r") as f:
        source_code = f.read()

    print("Lexing the code...")
    tokens = lex(source_code)

    print("Parsing the tokens...")
    ast = parse(tokens)

    print("Generating code...")
    cpp_code = generate_code(ast)
    if is_lib:
        with open(f"{output_file}.h", "w") as f:
            f.write(cpp_code)

    else:
        with open("output.cpp", "w") as f:
            f.write(cpp_code)

    print("Generated C++ code written to output.cpp")


    print("Compiling the code...")
    result = subprocess.run(
        ["g++", "-o", output_file, "output.cpp"],
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        print("Compilation successful!")
        if compile:
            print("Compiled successfully!")
            print(f"Output file: {output_file}")
            #os.remove("output.cpp")
        else:
            print("Running the executable...")
            os.system("output.exe")
            os.remove("output.cpp")
            os.remove("output.exe")

if __name__ == "__main__":
    main()
