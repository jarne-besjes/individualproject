import os
import sys

import llvmlite.binding as ll_binding
from fastapi import APIRouter
from pydantic import BaseModel

from .LLVMConverter import convert_to_llvm
from .Loops import fold_loops
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

    loops = Parser.check_const_loops(ast, ast)

    rec_analyzer = RecursiveCalls(llvm_code, ast)
    rec_calls = rec_analyzer.get_recursive_calls()
    rec_termination = rec_analyzer.check_termination()

    wcet_analyzer = WCETAnalyser(llvm_code, rec_calls)
    wcet_analyzer.get_wcet_of_functions()
    print(wcet_analyzer.functions_wcet, file=sys.stderr)



    os.remove("input.c")
    os.remove("output.ll")
    os.remove("output")

    # Remove all files ending with .dot (CFG files)
    """
    for file in os.listdir():
        if file.endswith(".dot"):
            os.remove(file)
            
    """

    return {"llvm": str(llvm_code), "infinite_loops": str(loops), "Recursive Calls": rec_calls, "Termination": rec_termination}
