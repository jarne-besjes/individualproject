from subprocess import Popen, PIPE, STDOUT

def convert_to_llvm(code: str) -> str:
    process = Popen(["g++", "-S", "-emit-llvm", "-x", "c", "-", "-o", "-"], stdin=PIPE, stdout=PIPE, stderr=STDOUT)
    stdout, stderr = process.communicate(input=code.encode())

    return stdout.decode()
