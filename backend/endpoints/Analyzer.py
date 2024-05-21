import os
import llvmlite.binding as ll_binding
from fastapi import APIRouter
from pydantic import BaseModel

from .LLVMConverter import convert_to_llvm
from .Loops import fold_loops
from .Parser import Parser
from .DotExporter import DotExporter

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

    os.remove("input.c")
    os.remove("output.ll")
    os.remove("output")

    return {"llvm": str(llvm_code)}
