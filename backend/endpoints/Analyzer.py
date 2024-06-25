import os
import sys

import llvmlite.binding as ll_binding
from fastapi import APIRouter
from pydantic import BaseModel

from .LLVMConverter import convert_to_llvm
from .Loops import LoopAnalyzer
from .Parser import Parser
from .DotExporter import DotExporter
from .Rec import RecursiveCalls
from .WCET import WCETAnalyser

router = APIRouter()


class Code(BaseModel):
    code: str


@router.post("/analyze")
async def analyze(code: Code):
    llvm_code = convert_to_llvm(code.code)
    # llvm = ll_binding.parse_assembly(llvm_code)

    with open("input.c", "w") as f:
        f.write(code.code)

    ast = Parser.parse("input.c")
    DotExporter.export(ast, "output")

    loop_analyzer = LoopAnalyzer(ast)
    loop_analyzer.analyze(ast)

    rec_analyzer = RecursiveCalls(llvm_code, ast)
    rec_calls = rec_analyzer.get_recursive_calls()
    rec_functions_execs = rec_analyzer.nr_function_execs
    rec_termination = rec_analyzer.check_termination()

    wcet_analyzer = WCETAnalyser(llvm_code, rec_calls, rec_functions_execs, loop_analyzer.loop_max_iterations)
    wcet_analyzer.get_wcet_of_functions()
    wcet_analyzer.get_wcet_of_loops()
    total_wcet = wcet_analyzer.get_total_wcet()

    os.remove("input.c")
    os.remove("output.ll")
    os.remove("output")

    # Remove all files ending with .dot (CFG files)
    """
    for file in os.listdir():
        if file.endswith(".dot"):
            os.remove(file)
            
    """

    return {
        "llvm": str(llvm_code),
        "infinite_loops": str(loop_analyzer.loop_infinity),
        "recursive_calls": rec_calls,
        "termination": rec_termination,
        "wcet_functions": wcet_analyzer.functions_wcet,
        "wcet_total": total_wcet,
    }
