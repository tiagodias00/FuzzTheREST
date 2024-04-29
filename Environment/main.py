from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import redis
import os
import environment
import numpy as np

import utils

app = FastAPI(title="Environment Service")

dotenv_path = 'C:\\Users\\franc\\Documents\\FuzzTheREST\\env.env'
load_dotenv(dotenv_path=dotenv_path)

redisDB = redis.Redis(host=os.getenv('REDIS_HOST'), port=int(os.getenv('REDIS_PORT')),
                      password=os.getenv('REDIS_PASSWORD'), db=0, decode_responses=False)


class InitializationData(BaseModel):
    base_url: str
    function: dict



class ActionData(BaseModel):
    env_id: str
    action: List[int]

class EnvData(BaseModel):
    env_id: str


@app.post("/initialize")
async def initialize(data: InitializationData):
    env = environment.initialize_environment(data.base_url, data.function, utils.mutation_methods)
    save_env_to_redis(env.id, env)
    return {"env_id": env.id,
            "message": "Environment initialized"}


@app.post("/step")
async def step(data: ActionData):
    env = load_env_from_redis(data.env_id)
    if env is None:
        raise HTTPException(status_code=404, detail="Environment not found")

    action_array = np.array(data.action)
    state, reward, done = env.step(action_array)
    save_env_to_redis(data.env_id, env)

    return {"state": state, "reward": reward, "done": done}


@app.post("/reset")
async def reset(data: EnvData):
    env = load_env_from_redis(data.env_id)
    if env is None:
        raise HTTPException(status_code=404, detail="Environment not initialized")

    state = env.reset()
    save_env_to_redis(data.env_id, env)  # Save the reset state back to Redis

    return {"state": state}

@app.post("/testRedis")
async def testRedis():
    redisDB.set("test", "test")
    return {"message": "Test successful"}
def save_env_to_redis(key, env):
    try:
        serialized_obj = env.serialize()
        redisDB.set(key, serialized_obj)
        return True
    except Exception as e:
        print(f"Error saving object to Redis: {e}")
        return False


def load_env_from_redis(key):
    try:

        serialized_obj = redisDB.get(key)
        if serialized_obj:

            env = environment.deserialize(serialized_obj)
            return env
        else:
            print("No data found for this key.")
            return None
    except Exception as e:
        print(f"Error loading object from Redis: {e}")
        return None


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)
