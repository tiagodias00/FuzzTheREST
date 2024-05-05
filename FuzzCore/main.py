from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from controllers import openAPIController, orchestratorController

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8001", "http://localhost:8002"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(openAPIController.router)
app.include_router(orchestratorController.router)


@app.get("/")
async def root():
    return {"message": "Helkjjuhyyyylo World"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
