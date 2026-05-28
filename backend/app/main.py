from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
 return {"message": "Backend is running successfully"}

@app.get("/health")
async def health():
 return {"status": "healthy"}
