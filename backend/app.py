from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
import endpoints.analyzer as analyzer

app = FastAPI(
    title="Code Analyzer",
    description="A simple code analyzer",
    version="0.1.0",
    docs_url="/docs",
)

origins = [
    "http://localhost",
    "http://localhost:3000",
    "*"  # Allow all origins
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(analyzer.router, prefix="/api")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
