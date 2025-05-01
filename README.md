# Parrot (WIP)
Welcome to the official repository for the Parrot esoteric programming language!

Parrot is a simple, custom, esoteric programming language created for the sole purpose of
understanding how a high-level language will be compiled into lower level code such as assembly and
machine code. Its syntax is designed to mimic the actions of a parrot, meaning it will have limited features
and capabilities. Consequently, it is not flexible enough to be used in creating real-world software projects. It
is also designed to be unconventional and humorous, where the programmer would feel like they're working
with something "bird-brained".

<h2>Details</h2>
<b>Level:</b> High-level</br>
<b>Filename Extension:</b> .prrt</br>
<b>Compile / Execution Type:</b> Compiled to machine code</br>
<b>Platforms:</b> 64-bit Linux & 64-bit Windows</br>
<b>Object Oriented?:</b> NO! >:( </br>

<h2>Features</h2>
●	Memory cells</br>
●	Move pointer between cells</br>
●	Increment / decrement value within cell</br>
●	Can take user input</br>
●	Can print</br>
●	Simple mathematics (addition and subtraction only)</br>
●	Loops</br>
●	Array of cells</br>
●	Conditional statements</br>
●	Jump to defined label</br>
●	Quirky and bird-brained</br>
●	Simple macros</br>

<h2>Memory Model</h2>
●	<b>Tape of memory cells</b>, like Dog and Brainfuck which is infinite to the right</br>
●	<b>Cells</b> (each cell is 1 byte, uint8)</br>
●	<b>Data Pointer</b> starts at cell #0</br>
●	Capable of doing <b>MOV, INC, DEC, READ & WRITE</b></br>

<h2>Code Structure</h2>
●	<b>Indentation-based code blocks:</b> Specify code blocks using Indentation (like Python)</br>
●	No need to specify a 'main' method, the whole code is the main method</br>
●	No OOP, birb too dumb for that</br>
●	<b>Labels (for code blocks)</b> - like a function but not a function, because it isn't a function. It's a label BUT it can function like a function :3</br>
●	<b>Keywords</b>: parrot uses keywords to do it's thing</br>

<h2>Keywords (Commands / Instructions)</h2>
<table border="1" cellpadding="8" cellspacing="0">
  <thead>
    <tr>
      <th>Keyword</th>
      <th>Function</th>
      <th>Similar To</th>
    </tr>
  </thead>
  <tbody>
    <tr><td>:> text here</td><td>Comment a single line</td><td>//</td></tr>
    <tr><td>(: ... :)</td><td>Multiline comment</td><td>/* */</td></tr>
    <tr><td>peck</td><td>Increment current cell</td><td>+</td></tr>
    <tr><td>scratch</td><td>Decrement current cell</td><td>-</td></tr>
    <tr><td>hop</td><td>Move pointer right</td><td>></td></tr>
    <tr><td>hopback</td><td>Move pointer left</td><td><</td></tr>
    <tr><td>gulp</td><td>Read 1 byte of input into the current cell</td><td>,</td></tr>
    <tr><td>squawk</td><td>Output ASCII of current cell (newline)</td><td>.</td></tr>
    <tr><td>stomach</td><td>Create array of memory cells</td><td></td></tr>
    <tr><td>devour</td><td>Read a string into cells</td><td></td></tr>
    <tr><td>regurgitate</td><td>Print devoured string</td><td></td></tr>
    <tr><td>spin</td><td>Start a loop</td><td></td></tr>
    <tr><td>bowl</td><td>Reference current cell</td><td></td></tr>
    <tr><td>mimic "text"</td><td>Print string</td><td>print()</td></tr>
    <tr><td>preen</td><td>Reset pointer to first cell</td><td></td></tr>
    <tr><td>poop</td><td>Clear cell (set to null)</td><td></td></tr>
    <tr><td>perch label:</td><td>Define a label</td><td>label:</td></tr>
    <tr><td>chirp macro:</td><td>Define a macro</td><td></td></tr>
    <tr><td>flyto label</td><td>Jump to label</td><td>JMP</td></tr>
    <tr><td>flap label cell1 op cell2</td><td>Conditional jump</td><td>if / branch</td></tr>
    <tr><td>add cell1 cell2</td><td>Add cell values</td><td></td></tr>
    <tr><td>sub cell1 cell2</td><td>Subtract cell values</td><td></td></tr>
    <tr><td>mul cell1 cell2</td><td>Multiplies (results in SQUAWK!)</td><td></td></tr>
    <tr><td>div cell1 cell2</td><td>Divides (results in SQUAWK!)</td><td></td></tr>
    <tr><td>bob N</td><td>Delay next process by N seconds</td><td></td></tr>
    <tr><td>perish</td><td>End program</td><td></td></tr>
  </tbody>
</table>

<h2>Parrot Language Tutorial</h2>
<a href="https://docs.google.com/document/d/1IgqcnB6-iD6ZBU52MgKmxDRcPYgQp5ntIfE1MP1B4pk/edit?tab=t.0#heading=h.m59wwcb2bhvs">ClICk mEeEEeeeEEEeEEEE!1!!!!!!111!1!!!</a>

<h2>How to Compile on Linux</h2>
<b>Step 1 - Generate intermediate language (Assembly):</b>

<b>NOTE:</b> Do not include the `$` symbol when executing the commands, this is merely to represent the terminal prompt.

<pre>$ python3 prrt_compiler_linux_v1.py parrot_code.prrt parrot_assembly.asm</pre>

* Replace `parrot_code` with the actual filename of your parrot source code and `parrot_assembly` with your desired name for the assembly file.

<b>Step 2 - Assemble with NASM:</b>
<pre>$ nasm -f elf64 parrot_assembly.asm -o parrot_output.o</pre>

<b>Step 3 - Link with </b>`ld`
<pre>$ ld parrot_output.o -o parrot_program_yes</pre>

<b>Step 4 - Run the program:</b>
<pre>$ ./parrot_program_yes</pre>

<h2>How to Compile on Windows</h2>
<b>Step 1 - Generate intermediate language (Assembly):</b>

<b>NOTE:</b> Do not include the `$` symbol when executing the commands, this is merely to represent the terminal prompt.

<pre>$ python3 prrt_compiler_windows_v1.py parrot_code.prrt parrot_assembly.asm</pre>

* Replace `parrot_code` with the actual filename of your parrot source code and `parrot_assembly` with your desired name for the assembly file.

<b>Step 2 - Assemble with NASM:</b>
<pre>$ nasm -f win64 parrot_assembly.asm -o parrot_output.obj</pre>

<b>Step 3 - Linking</b>
<pre>$ link /subsystem:console parrot_output.obj /defaultlib:kernel32.lib /defaultlib:msvcrt.lib /entry:main /out:parrot.exe</pre>

<h3>*Quick method for steps 2 and 3:</h3>

Use the `build.bat` Batch file to quickly assemble and link the program.

<b>NOTE:</b> Your `.asm` file should be named `parrot_assembly` when using `build.bat`)
<pre>build.bat</pre>

<b>Step 4 - Running the program:</b>
<pre>$ parrot.exe</pre>
