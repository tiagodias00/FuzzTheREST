from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import redis
import os

import numpy as np
from fastapi.middleware.cors import CORSMiddleware
import utils
from FuzzAlgorithm.controllers import fuzzingController

app = FastAPI(title="FuzzAlgorithm Service")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8000", "http://localhost:8002"],
    allow_methods=["*"],
    allow_headers=["*"],
)


load_dotenv()



app.include_router(fuzzingController.router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)
