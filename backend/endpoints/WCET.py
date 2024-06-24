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
        brackets = 0
        for line in self.llvm_code.split("\n"):
            if "define" in line:
                function_name = line.split("@")[1].split("(")[0]
                brackets = 0
                wcet = 0
                started = True

            if "{" in line:
                brackets += 1
            if "}" in line:
                brackets -= 1
                if brackets == 0:
                    started = False
                    self.functions_wcet[function_name] = wcet

            if started:
                added = False
                for key, value in llvmstatement_cycles.items():
                    if key in line:
                        wcet += value
                        added = True
                if not added:
                    print("No wcet found for: ", line, file=sys.stderr)
