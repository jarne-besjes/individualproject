from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from .LLVMConverter import convert_to_llvm
import llvmlite as ll
import llvmlite.binding as ll_binding
router = APIRouter()

class Code(BaseModel):
    code: str

@router.post("/analyze")
async def analyze(code: Code):
    llvm_code = convert_to_llvm(code.code)
    #llvm = ll_binding.parse_assembly(llvm_code)

    return {"llvm": str(llvm_code)}

