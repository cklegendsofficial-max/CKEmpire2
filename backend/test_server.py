from fastapi import FastAPI
from routers.finance import router as finance_router

app = FastAPI()
app.include_router(finance_router, prefix="/api/v1")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 