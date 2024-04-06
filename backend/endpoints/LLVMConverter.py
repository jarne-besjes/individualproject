import subprocess
from subprocess import Popen, PIPE, STDOUT

def convert_to_llvm(code: str) -> str:
    process = Popen(["clang", "-S", "-emit-llvm", "-x", "c", "-", "-o", "-"], stdin=PIPE, stdout=PIPE, stderr=STDOUT)
    stdout, stderr = process.communicate(input=code.encode())

    print(stdout.decode())

    with open("output.ll", "w") as f:
        f.write(stdout.decode())

    subprocess.run(["opt", "-passes=dot-cfg", "-disable-output", "output.ll"])

    return stdout.decode()
