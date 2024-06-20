import subprocess
from subprocess import Popen, PIPE, STDOUT

import sys


def convert_to_llvm(code: str) -> str:
    process = Popen(["clang", "-S", "-emit-llvm", "-Xclang", "-disable-O0-optnone", "-x", "c", "-", "-o", "-"], stdin=PIPE, stdout=PIPE, stderr=STDOUT)
    stdout, stderr = process.communicate(input=code.encode())

    with open("output.ll", "w") as f:
        f.write(stdout.decode())

    print("Running opt to find CFG", file=sys.stderr)
    print(subprocess.run(["opt", "--dot-cfg", "--disable-output", "output.ll"], stdout=PIPE, stderr=STDOUT), file=sys.stderr)
    return stdout.decode()
