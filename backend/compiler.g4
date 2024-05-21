grammar compiler;

WS: [ \t\n\r]+ -> skip; // toss out whitespace
/** The start rule; begin parsing here. */
prog: (stat | include)+;

LINE_COMMENT: '//' ~[\r\n]*;
COMMENT: '/*' .*? '*/';

stat:
	expr SEMI
	| enumstat SEMI
	| struct SEMI
	| main
	| switch
	| newVariable SEMI
    | array_decl_assignment SEMI
	| assignment SEMI
	| LINE_COMMENT
	| if
	| while
	| for
	| COMMENT
	| typedef
	| define
	| function
	| function_decl
	| scope;

typedef: TYPEDEF TYPE typedefname SEMI;
typedefname: ID | TYPE;

expr:
	expr ('*') expr
	| expr ('/') expr
	| expr '%' expr
	| expr ('+' | '-') expr
	| ('!' | '-' | '+') expr
	| expr ('<' | '>') expr
	| expr '||' expr
	| expr '==' expr
	| expr ('<=' | '>=' | '!=') expr
	| literal
	| struct_decl
	| struct_access
	| printf
	| scanf
	| functioncall
	| pointer
	| continue
	| break
	| RETURN expr
	| address
	| variable
	| LPAREN expr RPAREN
	| unaryminusminus
	| unaryplusplus
	| expr '&&' expr
	| expr LSHIFT expr
	| expr RSHIFT expr
	| expr AMPERSAND expr
	| expr BITOR expr
	| expr BITXOR expr
	| BITNOT expr
	| array_declaration
	| array_decl_elements
	| array_access
	| enum;

struct: STRUCT ID LBRACKET struct_entry* RBRACKET;
struct_entry: (TYPE ID SEMI) | array_declaration SEMI;
struct_decl: STRUCT ID ID;
struct_access: ID '.' ID;

array_declaration: TYPE ID ('[' INT ']')+;
array_decl_assignment: TYPE ID ('[' INT ']')+ '=' (array_decl_elements | STRING);
array_decl_elements: '{' expr (COMMA expr)* '}';
array_access: ID ('[' expr ']')+;


include: INCLUDE (STRING | '<' (.)*? '>');

define: DEFINE (ID | TYPE) (TYPE | ID | expr);

function: TYPE ID LPAREN (CONST? TYPE ID (COMMA CONST? TYPE ID)*)? RPAREN scope;
function_decl: TYPE ID LPAREN (CONST? TYPE ID (COMMA CONST? TYPE ID)*)? RPAREN SEMI;
functioncall: ID LPAREN (expr (COMMA expr)*)? RPAREN;

switch: SWITCH LPAREN expr RPAREN LBRACKET case_stat* default_stat? RBRACKET;
enumstat: ENUM ID ID '=' ID;

enum: ENUM ID LBRACKET (enumentry COMMA)* enumentry RBRACKET;
enumentry: ID ('=' INT)?;
case_stat: CASE expr COLON stat+;

default_stat: DEFAULT COLON stat+;

scope: LBRACKET stat* RBRACKET;


if: IF LPAREN expr RPAREN scope elif? else?;
elif:
	ELIF LPAREN expr RPAREN scope elif? else?;
else: ELSE scope;

while: WHILE LPAREN expr RPAREN scope;
break: BREAK;
continue: CONTINUE;

for: FOR LPAREN (assignment | newVariable) SEMI expr SEMI expr RPAREN scope;

unaryplusplus: PLUSPLUS (variable | literal) | (variable | literal) PLUSPLUS;

unaryminusminus: MINUSMINUS (variable | literal) | (variable | literal) MINUSMINUS;

variable: ID;


scanf: SCANF LPAREN STRING (COMMA expr)* RPAREN;
printf: PRINTF LPAREN STRING (COMMA expr)* RPAREN;

main: TYPE 'main' LPAREN RPAREN scope;

newVariable:
	CONST* (TYPE | ID) ('(' TYPE ')')? variable
	| CONST* (TYPE | ID) variable '=' ('(' TYPE ')')? expr
	| CONST* (TYPE | ID) pointer '=' address
	| CONST* (TYPE | ID) pointer '=' expr;

pointer: POINTER+ variable;

address: AMPERSAND ID;

assignment:
	ID '=' ('(' TYPE ')')? expr
	| expr '=' ('(' TYPE ')')? expr
	| array_access '=' ('(' TYPE ')')? expr;

literal: FLOAT | INT | CHAR | STRING | BOOL;
TYPE: 'int' | 'float' | 'char' | 'string' | 'bool' | 'void';


INCLUDE: '#include';
DEFINE: '#define';
SCANF: 'scanf';
PRINTF: 'printf';
RETURN: 'return';
BREAK: 'break';
CONTINUE: 'continue';
STRUCT: 'struct';
FOR: 'for';
SEMI: ';';
COMMA: ',';
IF: 'if';
WHILE: 'while';
TYPEDEF: 'typedef';
ENUM: 'enum';
ELIF: 'else if';
ELSE: 'else';
LBRACKET: '{';
RBRACKET: '}';
LPAREN: '(';
RPAREN: ')';
CONST: 'const';
SWITCH: 'switch';
CASE: 'case';
DEFAULT: 'default';
COLON: ':';
ID: [_a-zA-Z][_a-zA-Z0-9]*;
POINTER: '*';
PLUSPLUS: '++';
MINUSMINUS: '--';
SQUOTE: ['];
DQUOTE: ["];
DSLASH: '/' '/';
CHAR: SQUOTE . SQUOTE | SQUOTE '\\' . SQUOTE;
BOOL: 'true' | 'false';
FLOAT: [-]? [0-9]* '.' [0-9]*;
INT: [0] | [1-9][0-9]*; // TODO: handle '+' before an integer
STRING: ["] .*? ["];
LSHIFT: '<<';
RSHIFT: '>>';
AMPERSAND: '&';
BITOR: '|';
BITXOR: '^';
BITNOT: '~';
WILDCARD: [a-zA-Z0-9_]+;
