from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get("/")
def root():
    return {"message": "CKEmpire API", "status": "running"}

@app.get("/health")
def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    print("🚀 Starting CKEmpire Minimal Server...")
    print("📍 URL: http://127.0.0.1:8009")
    uvicorn.run(app, host="127.0.0.1", port=8009) 