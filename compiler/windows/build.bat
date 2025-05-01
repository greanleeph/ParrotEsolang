@echo off
REM Assemble the Parrot assembly to object code
nasm -f win64 parrot_assembly.asm -o parrot_output.obj
if errorlevel 1 exit /b

REM Link the object file into an executable
link /subsystem:console parrot_output.obj /defaultlib:kernel32.lib /defaultlib:msvcrt.lib /entry:main /out:parrot.exe
