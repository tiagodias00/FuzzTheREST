import json
from datetime import datetime
from typing import List, Dict, Any


from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Extra

from FuzzCore.services.Orchestration_service import initiate_fuzzing
from FuzzCore.services.MongoDB_service import MongoDBService
from FuzzCore.services.parser_service import parse_OpenApi_file

router = APIRouter()


class BaseAlgorithm(BaseModel):
    file_path: str
    algorithm_type: str
    ids: Any
    scenarios: Any

    class Config:
        extra = Extra.allow


class Qlearning(BaseAlgorithm):
    max_steps_per_episode: int
    exploration_rate: float
    num_episodes: int


def create_algorithm_params(**kwargs):
    algorithm_type = kwargs.get("algorithm_type")
    if algorithm_type == "Qlearning":
        return Qlearning(**kwargs)
    else:
        raise ValueError(f"Unsupported algorithm type: {algorithm_type}")


def get_MongoDB_service():
    return MongoDBService()


@router.post('/fuzz')
async def StartFuzzing(request: BaseAlgorithm, mongoDBService=Depends(get_MongoDB_service)):
    params = create_algorithm_params(**request.model_dump())
    params.ids = json.loads(params.ids)
    openApi_data = parse_OpenApi_file(request.file_path, params.ids)

    params.scenarios = json.loads(params.scenarios)

    metrics = initiate_fuzzing(params, openApi_data['base_url'], openApi_data['httpRequests'],
                               openApi_data['ids'], params.scenarios)

    if (metrics is None):
        raise HTTPException(status_code=500, detail="Error in Fuzzing")

    timestamp = datetime.now().strftime("%Y-%m-%d-%H:%M:%S")
    key = f"fuzzing_metrics:{params.algorithm_type}:{timestamp}"
    jsonMetrics = json.dumps(metrics['result'])
    saved = mongoDBService.save_metrics(key, jsonMetrics)
    if not saved:
        raise HTTPException(status_code=500, detail="Error in saving metrics")
    return {"message": "Fuzzing process saved with success"}
