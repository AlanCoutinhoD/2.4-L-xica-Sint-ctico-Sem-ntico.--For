from flask import Flask, request, render_template_string
import ply.lex as lex
import ply.yacc as yacc

app = Flask(__name__)

# Palabras reservadas y tokens
reserved = {
    'for': 'FOR',
    'system.out.println': 'PRINT'
}

tokens = (
    'LPAREN', 'RPAREN', 'SEMICOLON', 'LBRACE', 'RBRACE',
    'ASSIGN', 'NUMBER', 'LE', 'INCREMENT', 'ID'
) + tuple(reserved.values())

# Definición de tokens
t_LPAREN    = r'\('
t_RPAREN    = r'\)'
t_SEMICOLON = r';'
t_LBRACE    = r'\{'
t_RBRACE    = r'\}'
t_ASSIGN    = r'='
t_LE        = r'<='
t_INCREMENT = r'\+\+'

# Definición de identificadores y números
def t_ID(t):
    r'[a-zA-Z_][a-zA-Z_0-9\.]*'
    t.type = reserved.get(t.value.lower(), 'ID')
    return t

def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t

# Ignorar espacios y tabulaciones
t_ignore = ' \t'

# Manejo de errores
def t_error(t):
    print(f"Ilegal character '{t.value[0]}'")
    t.lexer.skip(1)

# Construcción del lexer
lexer = lex.lex()

# Precedencia y asociatividad de operadores
precedence = ()

# Definición de la gramática
def p_program(p):
    '''program : FOR LPAREN init SEMICOLON condition SEMICOLON increment RPAREN LBRACE statement RBRACE'''
    p[0] = f"{p[1]}({p[3]}; {p[5]}; {p[7]}) {{\n{p[9]}\n}}"

def p_init(p):
    '''init : ID ASSIGN NUMBER'''
    p[0] = f"{p[1]} = {p[3]}"

def p_condition(p):
    '''condition : ID LE NUMBER'''
    p[0] = f"{p[1]} <= {p[3]}"

def p_increment(p):
    '''increment : ID INCREMENT'''
    p[0] = f"{p[1]}++"

def p_statement(p):
    '''statement : PRINT LPAREN expression RPAREN SEMICOLON'''
    p[0] = f"{p[1]}({p[3]});"

def p_expression(p):
    '''expression : ID'''
    p[0] = p[1]

# Manejo de errores
def p_error(p):
    if p:
        print(f"Syntax error at '{p.value}'")
        raise SyntaxError(f"Syntax error at '{p.value}'")
    else:
        print("Syntax error at EOF")
        raise SyntaxError("Syntax error at EOF")

# Construcción del parser
parser = yacc.yacc()

@app.route('/', methods=['GET', 'POST'])
def index():
    result = ""
    error = ""
    if request.method == 'POST':
        code = request.form['code']
        lexer.input(code)
        tokens_list = []
        while True:
            tok = lexer.token()
            if not tok:
                break
            tokens_list.append(str(tok))

        try:
            parser.parse(code)
            result = "Compilación exitosa:\n" + "\n".join(tokens_list)
        except SyntaxError as e:
            error = str(e)
        except Exception as e:
            error = "An unexpected error occurred: " + str(e)

    return render_template_string('''
        <!doctype html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Analizador Léxico y Sintáctico</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    background-color: #f2f2f2;
                    margin: 0;
                    padding: 0;
                }
                .container {
                    max-width: 800px;
                    margin: 20px auto;
                    padding: 20px;
                    background-color: #fff;
                    border-radius: 5px;
                    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                }
                h1 {
                    color: #333;
                }
                textarea {
                    width: 100%;
                    height: 200px;
                    border: 1px solid #ccc;
                    border-radius: 5px;
                    padding: 10px;
                    margin-bottom: 10px;
                    font-size: 16px;
                }
                input[type="submit"] {
                    background-color: #4CAF50;
                    color: white;
                    padding: 10px 20px;
                    border: none;
                    border-radius: 5px;
                    cursor: pointer;
                    font-size: 16px;
                }
                input[type="submit"]:hover {
                    background-color: #45a049;
                }
                pre {
                    white-space: pre-wrap;
                    word-wrap: break-word;
                    font-size: 16px;
                }
                .error {
                    color: red;
                    font-weight: bold;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Analizador Léxico, Sintáctico Semantico </h1>
                <form method="post">
                    <textarea name="code" rows="10" placeholder="Introduce tu código aquí..."></textarea><br>
                    <input type="submit" value="Compilar">
                </form>
                {% if result %}
                    <h2>Resultado:</h2>
                    <pre>{{ result }}</pre>
                {% endif %}
                {% if error %}
                    <h2 class="error">Error:</h2>
                    <pre>{{ error }}</pre>
                {% endif %}
            </div>
        </body>
        </html>
    ''', result=result, error=error)

if __name__ == '__main__':
    app.run(debug=True)
