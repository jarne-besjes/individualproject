from .TreeNode import *
from dataclasses import dataclass
import sys

llvmstatement_cycles = {
    "add": 1,
    "sub": 1,
    "mul": 12,
    "div": 12,
    "icmp": 1,
    "fcmp": 1,
    "and": 1,
    "or": 1,
    "xor": 1,
    "alloca": 1,
    "load": 1,
    "store": 1,
    "getelementptr": 1,
    "call": 1,
    "ret": 1,
    "br": 1,
    "switch": 1,
    "indirectbr": 1,
}

class WCETAnalyser:
    def __init__(self, llvm_code: str, rec_functions) -> None:
        self.llvm_code = llvm_code
        self.rec_functions = rec_functions
        self.functions_wcet = {}

    def get_wcet_of_functions(self) -> int:
        started: bool = False
        wcet: int = 0
        for line in self.llvm_code.split("\n"):
            if "define" in line and not started:
                function_name = line.split("@")[1].split("(")[0]
                started = True
            if "define" in line and started:
                self.functions_wcet[function_name] = wcet
                wcet = 0
                started = False
            if started:
                for key, value in llvmstatement_cycles.items():
                    print("Key: ", key)
                    print("Line: ", line)
                    if key in line:
                        print("INSIDE OF IF")
                        wcet += value



