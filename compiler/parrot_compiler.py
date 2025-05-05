#!/usr/bin/env python3
"""
Parrot Programming Language Compiler
A compiler for the Parrot Programming Language (.prrt)

This compiler translates Parrot code to C as an intermediate representation,
then uses gcc to compile to executable machine code.
"""

import sys
import os
import re
import subprocess
import tempfile
import argparse
from enum import Enum, auto

class TokenType(Enum):
    """Token types for the Parrot language lexer"""
    COMMENT = auto()
    PECK = auto()
    SCRATCH = auto()
    HOP = auto()
    HOPBACK = auto()
    GULP = auto()
    SQUAWK = auto()
    STOMACH = auto()
    DEVOUR = auto()
    REGURGITATE = auto()
    BOWL = auto()
    MIMIC = auto()
    PREEN = auto()
    POOP = auto()
    PERCH = auto()
    CHIRP = auto()
    FLYTO = auto()
    FLAP = auto()
    ADD = auto()
    SUB = auto()
    MUL = auto()
    DIV = auto()
    BOB = auto()
    PERISH = auto()
    IDENTIFIER = auto()
    STRING = auto()
    NUMBER = auto()
    OPERATOR = auto()
    EMPTY = auto()
    INTO = auto()
    CELL_REF = auto()

class Token:
    """A token in the Parrot language"""
    def __init__(self, token_type, value=None, line_number=0):
        self.type = token_type
        self.value = value
        self.line_number = line_number
    
    def __str__(self):
        return f"Token({self.type}, {self.value}, line {self.line_number})"

class ParrotLexer:
    """Lexer for the Parrot Programming Language"""
    
    def __init__(self):
        self.keywords = {
            "peck": TokenType.PECK,
            "scratch": TokenType.SCRATCH,
            "hop": TokenType.HOP,
            "hopback": TokenType.HOPBACK,
            "gulp": TokenType.GULP,
            "squawk": TokenType.SQUAWK,
            "stomach": TokenType.STOMACH,
            "devour": TokenType.DEVOUR,
            "regurgitate": TokenType.REGURGITATE,
            "bowl": TokenType.BOWL,
            "mimic": TokenType.MIMIC,
            "preen": TokenType.PREEN,
            "poop": TokenType.POOP,
            "perch": TokenType.PERCH,
            "chirp": TokenType.CHIRP,
            "flyto": TokenType.FLYTO,
            "flap": TokenType.FLAP,
            "add": TokenType.ADD,
            "sub": TokenType.SUB,
            "mul": TokenType.MUL,
            "div": TokenType.DIV,
            "bob": TokenType.BOB,
            "perish": TokenType.PERISH,
            "into": TokenType.INTO,
            "empty": TokenType.EMPTY
        }
        
        self.operators = {
            ">": ">",
            "<": "<",
            "=": "==",
            "==": "==",
            "!=": "!=",
            ">=": ">=",
            "<=": "<="
        }
    
    def tokenize(self, code):
        """Convert Parrot code string into a list of tokens"""
        lines = code.split('\n')
        tokens = []
        multiline_comment = False
        
        for line_num, line in enumerate(lines, 1):
            # Skip empty lines
            if not line.strip():
                continue
                
            # Handle multiline comments
            if multiline_comment:
                if ":)" in line:
                    multiline_comment = False
                continue
                
            # Check for multiline comment start
            if "(" + ":" in line and not ":)" in line:
                multiline_comment = True
                continue
                
            # Handle single line comments
            if line.strip().startswith(":>"):
                continue
                
            # Count leading spaces for indentation
            indentation = len(line) - len(line.lstrip())
            
            # Process the line
            i = indentation
            line_tokens = []
            
            while i < len(line):
                char = line[i]
                
                # Skip spaces
                if char.isspace():
                    i += 1
                    continue
                
                # Handle string literals
                if char == '"':
                    start = i
                    i += 1
                    while i < len(line) and line[i] != '"':
                        if line[i] == '\\' and i + 1 < len(line):
                            i += 2  # Skip escape sequence
                        else:
                            i += 1
                    if i < len(line):  # Found closing quote
                        string_value = line[start+1:i]
                        line_tokens.append(Token(TokenType.STRING, string_value, line_num))
                        i += 1
                    else:
                        print(f"Error: Unclosed string literal at line {line_num}")
                        sys.exit(1)
                    continue
                
                # Handle numbers
                if char.isdigit():
                    start = i
                    while i < len(line) and line[i].isdigit():
                        i += 1
                    num_value = int(line[start:i])
                    line_tokens.append(Token(TokenType.NUMBER, num_value, line_num))
                    continue
                
                # Handle identifiers and keywords
                if char.isalpha() or char == '_' or char == '#':
                    start = i
                    while i < len(line) and (line[i].isalnum() or line[i] == '_' or line[i] == '#'):
                        i += 1
                    word = line[start:i]
                    
                    # Check if it's a cell reference with #
                    if word.startswith('#'):
                        try:
                            cell_num = int(word[1:])
                            line_tokens.append(Token(TokenType.CELL_REF, cell_num, line_num))
                        except ValueError:
                            print(f"Error: Invalid cell reference '{word}' at line {line_num}")
                            sys.exit(1)
                    # Otherwise check if it's a keyword or identifier
                    elif word in self.keywords:
                        line_tokens.append(Token(self.keywords[word], word, line_num))
                    else:
                        line_tokens.append(Token(TokenType.IDENTIFIER, word, line_num))
                    continue
                
                # Handle operators
                if char in "<>=!":
                    start = i
                    i += 1
                    if i < len(line) and line[i] == '=':
                        i += 1
                    op = line[start:i]
                    if op in self.operators:
                        line_tokens.append(Token(TokenType.OPERATOR, self.operators[op], line_num))
                    else:
                        print(f"Error: Invalid operator '{op}' at line {line_num}")
                        sys.exit(1)
                    continue
                
                # Handle colon for labels
                if char == ':':
                    line_tokens.append(Token(TokenType.IDENTIFIER, ':', line_num))
                    i += 1
                    continue
                
                # Skip other characters
                i += 1
            
            # Add indentation information
            if line_tokens:
                line_tokens[0].indentation = indentation // 4  # Assuming 4 spaces per indentation level
                tokens.extend(line_tokens)
        
        return tokens

class ParrotParser:
    """Parser for the Parrot Programming Language"""
    
    def __init__(self, tokens):
        self.tokens = tokens
        self.current = 0
        self.indent_stack = [0]
        self.labels = set()
        self.chirps = {}
        self.stomachs = {}
    
    def parse(self):
        """Parse the tokens into an AST or intermediate representation"""
        code_blocks = []
        self.first_pass()  # Collect all labels and macro definitions
        
        while not self.is_at_end():
            statement = self.parse_statement()
            if statement:
                code_blocks.append(statement)
        
        return code_blocks
    
    def first_pass(self):
        """First pass to collect all labels and chirp (macro) definitions"""
        i = 0
        while i < len(self.tokens):
            token = self.tokens[i]
            
            # Collect perch (label) declarations
            if token.type == TokenType.PERCH:
                if i + 1 < len(self.tokens) and self.tokens[i + 1].type == TokenType.IDENTIFIER:
                    label_name = self.tokens[i + 1].value
                    if label_name.endswith(':'):
                        label_name = label_name[:-1]
                    self.labels.add(label_name)
                i += 2  # Skip perch and label name
            
            # Collect chirp (macro) definitions
            elif token.type == TokenType.CHIRP:
                if i + 1 < len(self.tokens) and self.tokens[i + 1].type == TokenType.IDENTIFIER:
                    chirp_name = self.tokens[i + 1].value
                    if chirp_name.endswith(':'):
                        chirp_name = chirp_name[:-1]
                    
                    # Collect the chirp body
                    chirp_body = []
                    i += 2  # Skip chirp and name
                    
                    # TODO: Proper indentation handling for chirp bodies
                    # For now, just collect statements until we hit another top-level declaration
                    while i < len(self.tokens) and not (self.tokens[i].type in [TokenType.PERCH, TokenType.CHIRP] and 
                                                       getattr(self.tokens[i], 'indentation', 0) == 0):
                        chirp_body.append(self.tokens[i])
                        i += 1
                    
                    self.chirps[chirp_name] = chirp_body
                    continue  # We've already incremented i
            
            # Collect stomach (array) declarations
            elif token.type == TokenType.STOMACH:
                if i + 1 < len(self.tokens):
                    size = None
                    name = None
                    
                    # Check if the next token is a number (size)
                    if self.tokens[i + 1].type == TokenType.NUMBER:
                        size = self.tokens[i + 1].value
                        if i + 2 < len(self.tokens) and self.tokens[i + 2].type == TokenType.IDENTIFIER:
                            name = self.tokens[i + 2].value
                    # If not, it's just the name
                    elif self.tokens[i + 1].type == TokenType.IDENTIFIER:
                        name = self.tokens[i + 1].value
                    
                    if name:
                        self.stomachs[name] = size  # Size might be None
            
            i += 1
    
    def is_at_end(self):
        """Check if we've reached the end of the tokens"""
        return self.current >= len(self.tokens)
    
    def advance(self):
        """Advance to the next token"""
        if not self.is_at_end():
            self.current += 1
        return self.previous()
    
    def previous(self):
        """Get the previous token"""
        return self.tokens[self.current - 1]
    
    def peek(self):
        """Look at the current token without advancing"""
        if self.is_at_end():
            return None
        return self.tokens[self.current]
    
    def check(self, token_type):
        """Check if the current token is of the given type"""
        if self.is_at_end():
            return False
        return self.peek().type == token_type
    
    def match(self, *token_types):
        """Match the current token against the given types"""
        for token_type in token_types:
            if self.check(token_type):
                self.advance()
                return True
        return False
    
    def consume(self, token_type, error_message):
        """Consume a token of the expected type or throw an error"""
        if self.check(token_type):
            return self.advance()
        
        token = self.peek()
        line = token.line_number if token else "unknown"
        print(f"Parser error at line {line}: {error_message}")
        sys.exit(1)
    
    def parse_statement(self):
        """Parse a statement"""
        token = self.peek()
        if not token:
            return None
        
        if token.type == TokenType.PECK:
            self.advance()
            return {"type": "peck"}
        
        elif token.type == TokenType.SCRATCH:
            self.advance()
            return {"type": "scratch"}
        
        elif token.type == TokenType.HOP:
            self.advance()
            return {"type": "hop"}
        
        elif token.type == TokenType.HOPBACK:
            self.advance()
            return {"type": "hopback"}
        
        elif token.type == TokenType.GULP:
            self.advance()
            args = []
            # Check for optional prompt or direct value
            if not self.is_at_end() and (self.peek().type == TokenType.STRING or self.peek().type == TokenType.NUMBER):
                args.append(self.advance().value)
            return {"type": "gulp", "args": args}
        
        elif token.type == TokenType.SQUAWK:
            self.advance()
            return {"type": "squawk"}
        
        elif token.type == TokenType.STOMACH:
            self.advance()
            size = None
            name = None
            
            # Check for size
            if not self.is_at_end() and self.peek().type == TokenType.NUMBER:
                size = self.advance().value
            
            # Get stomach name
            if not self.is_at_end() and self.peek().type == TokenType.IDENTIFIER:
                name = self.advance().value
            else:
                print(f"Error at line {token.line_number}: Expected stomach name")
                sys.exit(1)
            
            return {"type": "stomach", "name": name, "size": size}
        
        elif token.type == TokenType.DEVOUR:
            self.advance()
            target = None
            content = None
            
            # Check for "into" keyword
            if not self.is_at_end() and self.peek().type == TokenType.INTO:
                self.advance()  # Consume "into"
                
                # Get target (stomach name or cell number)
                if not self.is_at_end():
                    if self.peek().type == TokenType.IDENTIFIER:
                        target = self.advance().value
                    elif self.peek().type == TokenType.NUMBER:
                        target = self.advance().value
            
            # Check for direct string content
            if not self.is_at_end() and self.peek().type == TokenType.STRING:
                content = self.advance().value
            
            return {"type": "devour", "target": target, "content": content}
        
        elif token.type == TokenType.REGURGITATE:
            self.advance()
            target = None
            
            # Check for stomach name
            if not self.is_at_end() and self.peek().type == TokenType.IDENTIFIER:
                target = self.advance().value
            
            return {"type": "regurgitate", "target": target}
        
        elif token.type == TokenType.MIMIC:
            self.advance()
            text = None
            
            # Get the string to mimic
            if not self.is_at_end() and self.peek().type == TokenType.STRING:
                text = self.advance().value
            else:
                print(f"Error at line {token.line_number}: Expected string after mimic")
                sys.exit(1)
            
            return {"type": "mimic", "text": text}
        
        elif token.type == TokenType.PREEN:
            self.advance()
            return {"type": "preen"}
        
        elif token.type == TokenType.POOP:
            self.advance()
            return {"type": "poop"}
        
        elif token.type == TokenType.PERCH:
            self.advance()
            name = None
            
            # Get label name
            if not self.is_at_end() and self.peek().type == TokenType.IDENTIFIER:
                name = self.advance().value
                if name.endswith(':'):
                    name = name[:-1]  # Remove trailing colon
            
            return {"type": "perch", "name": name}
        
        elif token.type == TokenType.FLYTO:
            self.advance()
            target = None
            
            # Get label to fly to
            if not self.is_at_end() and self.peek().type == TokenType.IDENTIFIER:
                target = self.advance().value
            
            return {"type": "flyto", "target": target}
        
        elif token.type == TokenType.FLAP:
            self.advance()
            target = None
            left = None
            op = None
            right = None
            
            # Get target label
            if not self.is_at_end() and self.peek().type == TokenType.IDENTIFIER:
                target = self.advance().value
            
            # Get left operand
            if not self.is_at_end():
                if self.peek().type == TokenType.BOWL:
                    left = "bowl"
                    self.advance()
                elif self.peek().type == TokenType.NUMBER:
                    left = self.advance().value
            
            # Get operator
            if not self.is_at_end() and self.peek().type == TokenType.OPERATOR:
                op = self.advance().value
            
            # Get right operand
            if not self.is_at_end():
                if self.peek().type == TokenType.EMPTY:
                    right = "empty"
                    self.advance()
                elif self.peek().type == TokenType.NUMBER:
                    right = self.advance().value
                elif self.peek().type == TokenType.BOWL:
                    right = "bowl"
                    self.advance()
            
            return {"type": "flap", "target": target, "left": left, "op": op, "right": right}
        
        elif token.type == TokenType.ADD or token.type == TokenType.SUB:
            op_type = "add" if token.type == TokenType.ADD else "sub"
            self.advance()
            left = None
            left_is_cell = False
            right = None
            right_is_cell = False
            
            # Get left operand
            if not self.is_at_end():
                if self.peek().type == TokenType.BOWL:
                    left = "bowl"
                    self.advance()
                elif self.peek().type == TokenType.NUMBER:
                    left = self.advance().value
                elif self.peek().type == TokenType.CELL_REF:
                    left = self.advance().value
                    left_is_cell = True
            
            # Get right operand
            if not self.is_at_end():
                if self.peek().type == TokenType.NUMBER:
                    right = self.advance().value
                elif self.peek().type == TokenType.BOWL:
                    right = "bowl"
                    self.advance()
                elif self.peek().type == TokenType.CELL_REF:
                    right = self.advance().value
                    right_is_cell = True
            
            return { "type": op_type, "left": left, "right": right, "left_is_cell": left_is_cell, "right_is_cell": right_is_cell}
        
        elif token.type == TokenType.MUL or token.type == TokenType.DIV:
            op_type = "mul" if token.type == TokenType.MUL else "div"
            self.advance()
            # These are "useless" but still supported
            return {"type": op_type}
        
        elif token.type == TokenType.BOB:
            self.advance()
            count = None
            
            # Get bob count
            if not self.is_at_end() and self.peek().type == TokenType.NUMBER:
                count = self.advance().value
            
            return {"type": "bob", "count": count}
        
        elif token.type == TokenType.PERISH:
            self.advance()
            return {"type": "perish"}
        
        elif token.type == TokenType.IDENTIFIER:
            # This could be a chirp (macro) call
            name = self.advance().value
            if name in self.chirps:
                return {"type": "chirp_call", "name": name}
        
        else:
            # Skip unknown token
            self.advance()
        
        return None

class CodeGenerator:
    """Generate C code from the parsed Parrot code"""
    
    def __init__(self, ast, stomachs):
        self.ast = ast
        self.stomachs = stomachs
        self.code = []
        self.indent_level = 0
    
    def generate(self):
        """Generate C code from the AST"""
        # Add standard C headers and setup
        self.code.append("""
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
""")

        # Add platform-specific headers
        if os.name == 'nt':
            self.code.append("""
#include <windows.h>
#define sleep(x) Sleep((x) * 1000)
""")
        else:
            self.code.append("""
#include <unistd.h>
""")

        self.code.append("""
#include <stdint.h>

#define TAPE_SIZE 30000
#define MAX_INPUT 1024

// Globals
uint8_t tape[TAPE_SIZE] = {0};
int ptr = 0;
char input_buffer[MAX_INPUT];

// Forward declarations
void squawk();
void gulp(int direct_val, char direct_char);
""")

        # Define stomach arrays
        for name, size in self.stomachs.items():
            size_val = size if size is not None else 1024  # Default size
            self.code.append(f"uint8_t stomach_{name}[{size_val}] = {{0}};")
        
        self.code.append("""
// Helper functions
void squawk() {
    printf("%c\\n", tape[ptr]);
}

void gulp(int direct_val, char direct_char) {
    if (direct_val != -1) {
        tape[ptr] = direct_val;
        return;
    }
    
    if (direct_char != 0) {
        tape[ptr] = direct_char;
        return;
    }
    
    printf("Feed the birb: ");
    fflush(stdout);
    
    int ch = getchar();
    if (ch == EOF || ch == '\\n') {
        tape[ptr] = 0;  // Set to empty on EOF or newline
    } else {
        tape[ptr] = ch;
        // Eat up rest of the line
        while ((ch = getchar()) != '\\n' && ch != EOF);
    }
}

void devour(uint8_t *target, const char *content) {
    if (content != NULL) {
        // Direct content provided
        int i = 0;
        while (content[i] != '\\0') {
            target[i] = content[i];
            i++;
        }
        target[i] = 0;  // Null-terminate
    } else {
        // User input
        printf("birb opens wide: ");
        fflush(stdout);
        
        fgets(input_buffer, MAX_INPUT, stdin);
        size_t len = strlen(input_buffer);
        
        // Remove trailing newline if present
        if (len > 0 && input_buffer[len-1] == '\\n') {
            input_buffer[len-1] = '\\0';
            len--;
        }
        
        // Copy to target
        for (size_t i = 0; i < len; i++) {
            target[i] = input_buffer[i];
        }
        target[len] = 0;  // Null-terminate
    }
}

void regurgitate(uint8_t *source) {
    int i = 0;
    while (source[i] != 0) {
        putchar(source[i]);
        i++;
    }
    printf("\\n");
}

int main() {
""")
        
        # Generate code for the AST
        self.indent_level = 1
        for node in self.ast:
            self.generate_node(node)
        
        # Close main function and return 0
        self.code.append("    return 0;\n}")
        
        return "\n".join(self.code)
    
    def indent(self):
        """Return the current indentation as a string"""
        return "    " * self.indent_level
    
    def generate_node(self, node):
        """Generate C code for a specific AST node"""
        if not node:
            return
        
        node_type = node.get("type", "")
        
        if node_type == "peck":
            self.code.append(f"{self.indent()}tape[ptr]++;")
        
        elif node_type == "scratch":
            self.code.append(f"{self.indent()}tape[ptr]--;")
        
        elif node_type == "hop":
            self.code.append(f"{self.indent()}ptr++;")
        
        elif node_type == "hopback":
            self.code.append(f"{self.indent()}ptr--;")
        
        elif node_type == "gulp":
            args = node.get("args", [])
            if args and isinstance(args[0], int):
                self.code.append(f"{self.indent()}gulp({args[0]}, 0);")
            elif args and isinstance(args[0], str):
                self.code.append(f"{self.indent()}gulp(-1, '{args[0]}');")
            else:
                self.code.append(f"{self.indent()}gulp(-1, 0);")
        
        elif node_type == "squawk":
            self.code.append(f"{self.indent()}squawk();")
        
        elif node_type == "mimic":
            text = node.get("text", "")
            self.code.append(f'{self.indent()}printf("{text}\\n");')
        
        elif node_type == "preen":
            self.code.append(f"{self.indent()}ptr = 0;")
        
        elif node_type == "poop":
            self.code.append(f"{self.indent()}tape[ptr] = 0;")
            self.code.append(f'{self.indent()}printf("Birb relieved itself on cell %d\\n", ptr);')
        
        elif node_type == "perch":
            name = node.get("name", "")
            self.code.append(f"{self.indent()[:-4]}{name}:")
        
        elif node_type == "flyto":
            target = node.get("target", "")
            self.code.append(f"{self.indent()}goto {target};")
        
        elif node_type == "flap":
            target = node.get("target", "")
            left = node.get("left", "")
            op = node.get("op", "")
            right = node.get("right", "")
            
            left_expr = "tape[ptr]" if left == "bowl" else str(left)
            
            if right == "empty":
                right_expr = "0"
            elif right == "bowl":
                right_expr = "tape[ptr]"
            else:
                right_expr = str(right)
            
            self.code.append(f"{self.indent()}if ({left_expr} {op} {right_expr}) {{")
            self.code.append(f"{self.indent()}    goto {target};")
            self.code.append(f"{self.indent()}}}")
        
        elif node_type == "add":
            left = node.get("left", "")
            right = node.get("right", "")
            left_is_cell = node.get("left_is_cell", False)
            right_is_cell = node.get("right_is_cell", False)
            
            # determine left operand expression
            if left == "bowl":
                left_expr = "tape[ptr]"
            elif left_is_cell:
                left_expr = f"tape[{left}]"
            else:
                left_expr = f"tape[{left}]"

            # determine right operand expression
            if right == "bowl":
                right_expr = "tape[ptr]"
            elif right_is_cell:
                right_expr = f"tape[{right}]"
            else:
                right_expr = str(right) #direct number value
            
            self.code.append(f"{self.indent()}{left_expr} += {right_expr};")
        
        elif node_type == "sub":
            left = node.get("left", "")
            right = node.get("right", "")
            left_is_cell = node.get("left_is_cell", False)
            right_is_cell = node.get("right_is_cell", False)
            
            # Determine left operand expression
            if left == "bowl":
                left_expr = "tape[ptr]"
            elif left_is_cell:
                left_expr = f"tape[{left}]" 
            else:
                left_expr = f"tape[{left}]"  # Default to treating as cell index
            
            # Handle right operand based on its type
            if right == "bowl":
                right_expr = "tape[ptr]"
            elif right_is_cell:
                right_expr = f"tape[{right}]"
            else:
                right_expr = str(right)  # Direct number value
            
            self.code.append(f"{self.indent()}{left_expr} -= {right_expr};")
        
        elif node_type == "mul" or node_type == "div":
            self.code.append(f'{self.indent()}printf("SQUAWK!\\n");')
        
        elif node_type == "bob":
            count = node.get("count", 1)
            self.code.append(f'{self.indent()}printf("birb bobs head {count} times...\\n");')
            self.code.append(f"{self.indent()}sleep({count});")
        
        elif node_type == "perish":
            self.code.append(f'{self.indent()}printf("birb has perished ;-;\\n");')
            self.code.append(f"{self.indent()}return 0;")
        
        elif node_type == "stomach":
            # Already declared in the globals section
            pass
        
        elif node_type == "devour":
            target = node.get("target", None)
            content = node.get("content", None)
            
            # Determine target array
            if target is None:
                target_expr = "tape + ptr"
            elif isinstance(target, str) and target in self.stomachs:
                target_expr = f"stomach_{target}"
            else:
                target_expr = f"tape + {target}"
            
            # Handle content
            content_expr = f"\"{content}\"" if content is not None else "NULL"
            
            self.code.append(f"{self.indent()}devour({target_expr}, {content_expr});")
        
        elif node_type == "regurgitate":
            target = node.get("target", None)
            
            # Determine source array
            if target is None:
                source_expr = "tape + ptr"
            elif target in self.stomachs:
                source_expr = f"stomach_{target}"
            else:
                source_expr = "tape + ptr"  # Default to current position
            
            self.code.append(f"{self.indent()}regurgitate({source_expr});")
        
        elif node_type == "chirp_call":
            # We would need to expand macro calls here
            name = node.get("name", "")
            self.code.append(f"{self.indent()}// Chirp call: {name}")
            # In a real implementation, we would insert the macro body here

def compile_parrot(source_file, output_file=None, verbose=False):
    """Compile a Parrot source file to an executable"""
    # Default output file is the source file name without extension
    if not output_file:
        output_file = os.path.splitext(source_file)[0]
        # make .exe for Windows haiyaa...
        if os.name == 'nt' and not output_file.endswith('.exe'):
            output_file += '.exe'
    
    # Read source file
    try:
        with open(source_file, 'r') as f:
            source_code = f.read()
    except FileNotFoundError:
        print(f"Error: Source file '{source_file}' not found")
        return 1
    
    # Create lexer and tokenize
    lexer = ParrotLexer()
    tokens = lexer.tokenize(source_code)
    
    if verbose:
        print("Tokens:")
        for token in tokens:
            print(f"  {token}")
    
    # Parse tokens
    parser = ParrotParser(tokens)
    ast = parser.parse()
    
    if verbose:
        print("\nAST:")
        for node in ast:
            print(f"  {node}")
    
    # Generate C code
    code_gen = CodeGenerator(ast, parser.stomachs)
    c_code = code_gen.generate()
    
    # Write C code to temporary file
    with tempfile.NamedTemporaryFile(suffix='.c', delete=False) as temp_file:
        temp_filename = temp_file.name
        temp_file.write(c_code.encode('utf-8'))
    
    if verbose:
        print(f"\nGenerated C code saved to {temp_filename}")
        print(c_code)
    
    # Compile C code to executable
    try:
        if os.name == 'nt':
            # Windows - check for available compilers
            if shutil.which('gcc'):
                compiler_cmd = ['gcc']
            elif shutil.which('cl'):
                compiler_cmd = ['cl']  # Microsoft Visual C++
            else:
                print("Error: No C compiler found. Please install MinGW or MSVC.")
                return 1
        else:
            # Unix-like systems
            compiler_cmd = ['gcc'] # so much easier...
            
        result = subprocess.run(compiler_cmd + [temp_filename, '-o', output_file], 
                               capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"Error compiling C code: {result.stderr}")
            return 1
        
        # Make executable (skip on Windows)
        if os.name != 'nt':
            os.chmod(output_file, 0o755)
        
        print(f"Successfully compiled {source_file} to {output_file}")
        return 0
    
    except Exception as e:
        print(f"Error during compilation: {e}")
        return 1
    finally:
        # Clean up temporary file
        try:
            os.unlink(temp_filename)
        except:
            pass

def main():
    """Main entry point for the Parrot compiler"""
    parser = argparse.ArgumentParser(description='Parrot Programming Language Compiler')
    parser.add_argument('source', help='Source file (.prrt)')
    parser.add_argument('-o', '--output', help='Output executable file')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    # Check file extension
    if not args.source.endswith('.prrt'):
        print("Warning: Source file doesn't have .prrt extension")
    
    # Compile
    return compile_parrot(args.source, args.output, args.verbose)

if __name__ == "__main__":
    sys.exit(main())
