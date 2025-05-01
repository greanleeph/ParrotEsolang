# Parrot Windows Compiler

import re
import sys

class ParrotCompiler:
    def __init__(self):
        # Internal state
        self.source = ""
        self.tokens = []
        self.ast = []
        self.labels = {}
        self.macros = {}
        self.label_count = 0
        self.asm_lines = []
        self.ir = []

    ##############################
    # Phase 1: Lexical Analysis
    ##############################
    def lex(self, code):
        self.source = code
        lines = code.splitlines()
        self.tokens = [line.rstrip() for line in lines if line.strip() and not line.strip().startswith(":>")]

    ##############################
    # Phase 2: Syntax Analysis
    ##############################
    def parse(self):
        indent_stack = [0]
        current_block = []
        self.ast = []
        current_macro = None

        for line in self.tokens:
            indent = len(line) - len(line.lstrip())
            content = line.strip()
            parts = content.split()
            instr = parts[0]
            args = parts[1:]

            if instr == "chirp":
                macro_name = args[0].rstrip(":")
                current_macro = macro_name
                self.macros[macro_name] = []
                indent_stack.append(indent)
                current_block = self.macros[macro_name]
                continue

            if instr == "perch":
                label = args[0].rstrip(":")
                self.labels[label] = len(self.ast)

            node = {"instr": instr, "args": args}

            if indent > indent_stack[-1]:
                indent_stack.append(indent)
            elif indent < indent_stack[-1]:
                while indent < indent_stack[-1]:
                    indent_stack.pop()
                current_macro = None
                current_block = self.ast

            if current_macro and indent >= indent_stack[-1]:
                self.macros[current_macro].append(node)
            else:
                self.ast.append(node)

    ##############################
    # Phase 3: Semantic Analysis
    ##############################
    def semantic_check(self):
        for node in self.ast:
            if node["instr"] == "flyto" and not node["args"]:
                raise SyntaxError(f"Missing label in flyto: {node}")

    ##############################
    # Phase 4: Intermediate Code Generation
    ##############################
    def generate_ir(self):
        self.ir = []
        for node in self.ast:
            if node["instr"] in self.macros:
                self.ir.extend(self.macros[node["instr"]])
            else:
                self.ir.append(node)

    ##############################
    # Phase 5: Code Optimization (optional)
    ##############################
    def optimize(self):
        # add optimizer here
        pass # no optimizations, proceed to def generate_asm

    ####################################################
    # Phase 6: Target Code Generation (Windows NASM x64)
    ####################################################
    def generate_asm(self, output_file="output.asm"):
        self.asm_lines = [
            "extern ExitProcess",
            "extern printf",
            "extern scanf",
            "section .data",
            "newline db 10, 0",
            "fmt_in db \"%c\", 0",
            "fmt_out db \"%c\", 0",
            "input_buffer db 128 dup(0)",
            "section .bss",
            "tape resb 30000",
            "section .text",
            "global main",
            "main:",
            "    mov rsi, tape"
        ]

        for node in self.ir:
            instr, args = node["instr"], node["args"]

            if instr == "peck":
                self.asm_lines.append("    inc byte [rsi]")
            elif instr == "scratch":
                self.asm_lines.append("    dec byte [rsi]")
            elif instr == "hop":
                self.asm_lines.append("    inc rsi")
            elif instr == "hopback":
                self.asm_lines.append("    dec rsi")
            elif instr == "squawk":
                self.asm_lines += [
                    "    movzx rcx, byte [rsi]",
                    "    lea rdx, [fmt_out]",
                    "    call printf"
                ]
            elif instr == "mimic":
                label = f"str_{self.label_count}"
                string = " ".join(args).strip('"')
                self.asm_lines.insert(4, f"{label} db \"{string}\", 10, 0")
                self.asm_lines += [
                    f"    lea rcx, [{label}]",
                    f"    call printf"
                ]
                self.label_count += 1
            elif instr == "gulp":
                self.asm_lines += [
                    "    lea rdx, [fmt_in]",
                    "    mov rcx, rsi",
                    "    call scanf"
                ]
            elif instr == "devour":
                # Read entire line is complex — simplified gulp loop would be better in real impl
                self.asm_lines += [
                    "    ; simplified devour -> scanf",
                    "    lea rdx, [fmt_in]",
                    "    mov rcx, rsi",
                    "    call scanf"
                ]
            elif instr == "regurgitate":
                self.asm_lines += [
                    "reg_loop:",
                    "    mov al, [rsi]",
                    "    cmp al, 0",
                    "    je reg_end",
                    "    movzx rcx, al",
                    "    lea rdx, [fmt_out]",
                    "    call printf",
                    "    inc rsi",
                    "    jmp reg_loop",
                    "reg_end:"
                ]
            elif instr == "flyto":
                self.asm_lines.append(f"    jmp .{args[0]}")
            elif instr == "perch":
                self.asm_lines.append(f".{args[0]}:")
            elif instr == "flap":
                label, left, op, right = args
                left = "byte [rsi]" if left == "bowl" else left
                right = "0" if right == "empty" else ("byte [rsi]" if right == "bowl" else right)
                jmp_op = {
                    "==": "je", "!=" : "jne",
                    ">": "jg", "<": "jl",
                    ">=": "jge", "<=": "jle"
                }[op]
                self.asm_lines += [
                    f"    movzx rax, {left}",
                    f"    cmp rax, {right}",
                    f"    {jmp_op} .{label}"
                ]
            elif instr == "add":
                dest, val = args
                if dest == "bowl":
                    self.asm_lines.append(f"    add byte [rsi], {val}")
            elif instr == "sub":
                dest, val = args
                if dest == "bowl":
                    self.asm_lines.append(f"    sub byte [rsi], {val}")
            elif instr == "bob":
                self.asm_lines.append(f"    ; bob pause placeholder: {args[0]} seconds")
            elif instr == "preen":
                self.asm_lines.append("    mov rsi, tape")
            elif instr == "poop":
                self.asm_lines.append("    mov byte [rsi], 0")
            elif instr == "perish":
                self.asm_lines += [
                    "    xor rcx, rcx",
                    "    call ExitProcess"
                ]

        with open(output_file, "w") as f:
            f.write("\n".join(self.asm_lines))
        print(f"Windows-compatible assembly written to {output_file}")

##############################
# Entry Point
##############################
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python prrt_compiler.py <input_file>.prrt [output_file.asm]")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else "output.asm"

    with open(input_file, "r") as f:
        source = f.read()

    compiler = ParrotCompiler()
    compiler.lex(source)
    compiler.parse()
    compiler.semantic_check()
    compiler.generate_ir()
    compiler.optimize()
    compiler.generate_asm(output_file)

