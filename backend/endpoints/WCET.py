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
    def __init__(self, llvm_code: str, rec_functions, rec_functions_execs) -> None:
        self.llvm_code = llvm_code
        self.rec_functions = rec_functions
        self.functions_wcet = {}
        self.rec_functions_execs: dict[str, dict[TreeNode, int]] = rec_functions_execs

    def get_total_wcet(self) -> int:
        wcet = 0
        for key, cpuexecs in self.functions_wcet.items():
            print("function: ", key, file=sys.stderr)
            print("rec_functions: ", self.rec_functions, file=sys.stderr)
            recursive_function = False
            rec_value = None
            for rec_key, rec_value in self.rec_functions:
                if key == rec_key:
                    recursive_function = True
            if recursive_function:
                nr_iterations = 0
                print(self.rec_functions_execs, file=sys.stderr)
                for rec_key, rec_value in self.rec_functions_execs.items():

                    print("key:", key, file=sys.stderr)
                    print("rec_key: ", rec_key, file=sys.stderr)

                    if key == rec_key:
                        print("inside if: ", rec_value, file=sys.stderr)
                        for _, value in rec_value.items():
                            nr_iterations += value
                print("nr_iterations: ", nr_iterations, file=sys.stderr)
                wcet += cpuexecs * nr_iterations
            else:
                wcet += cpuexecs
        return wcet

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
                    print("No wcet found for (this might be normal): ", line, file=sys.stderr)
