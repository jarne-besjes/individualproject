from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

class Code(BaseModel):
    code: str
@router.post("analyze")
async def analyze(code: Code):
    print(code.code)
    return {"code": code.code}