from .TreeNode import *
from dataclasses import dataclass
import sys

llvmstatement_cycles = {
    "add": 1,
    "sub": 1,
    "mul": 15,
    "div": 15,
    "icmp": 1,
    "fcmp": 1,
    "and": 1,
    "or": 1,
    "xor": 1,
    " j ": 17,
    "alloca": 1,
    "load": 1,
    "store": 1,
    "getelementptr": 1,
    "call": 17,
    "ret": 1,
    "br": 1,
    "switch": 1,
    "indirectbr": 1,
}


class WCETAnalyser:
    def __init__(self, llvm_code: str, rec_functions, rec_functions_execs, loop_max_iterations) -> None:
        self.llvm_code = llvm_code
        self.rec_functions = rec_functions
        self.functions_wcet = {}
        self.rec_functions_execs: dict[str, dict[TreeNode, int]] = rec_functions_execs
        self.loops_wcet = []
        self.loops_max_iterations = loop_max_iterations

    def get_total_wcet(self) -> int | str:
        if float("inf") in list(self.loops_max_iterations.values()):
            return "inf"
        wcet = 0
        for key, cpuexecs in self.functions_wcet.items():
            if cpuexecs is float("inf"):
                return "inf"
            recursive_function = False
            rec_value = None
            for rec_key, rec_value in self.rec_functions:
                if key == rec_key:
                    recursive_function = True
            if recursive_function:
                nr_iterations = 0
                for rec_key, rec_value in self.rec_functions_execs.items():
                    if key == rec_key:
                        for _, value in rec_value.items():
                            if value == float("inf"):
                                return "inf"
                            nr_iterations += value
                wcet += cpuexecs * nr_iterations
            else:
                wcet += cpuexecs
        for loop_wcet in self.loops_wcet:
            wcet += loop_wcet
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
                    pass

    def get_wcet_of_loops(self) -> int:
        wcet = 0
        buffer = []
        idx = 0
        for line in self.llvm_code.split("\n"):
            if not "loop" in line:
                buffer.append(line)
            elif "loop" not in line and "br" in line:
                buffer.clear()
            else:
                for buffer_line in buffer:
                    for key, value in llvmstatement_cycles.items():
                        if key in buffer_line:
                            wcet += value
                try:
                    if list(self.loops_max_iterations.values())[idx] == float("inf"):
                        wcet = float("inf")
                        return
                    self.loops_wcet.append(wcet * list(self.loops_max_iterations.values())[idx])
                    idx += 1
                except:
                    pass
