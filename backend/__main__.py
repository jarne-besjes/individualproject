from fastapi import FastAPI, APIRouter
import endpoints.analyzer as analyzer


app = FastAPI(
    title="Code Analyzer",
    description="A simple code analyzer",
    version="0.1.0",
    docs_url="/docs"
)

baserouter = APIRouter()

app.include_router(baserouter, prefix="/api")

baserouter.include_router(analyzer.router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
