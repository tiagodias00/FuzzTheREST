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

dotenv_path = 'C:\\Users\\franc\\Documents\\FuzzTheREST\\env.env'
load_dotenv(dotenv_path=dotenv_path)

redisDB = redis.Redis(host=os.getenv('REDIS_HOST'), port=int(os.getenv('REDIS_PORT')),
                      password=os.getenv('REDIS_PASSWORD'), db=0, decode_responses=False)

app.include_router(fuzzingController.router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)
