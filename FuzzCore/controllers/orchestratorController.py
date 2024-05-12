from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Extra

from FuzzCore.services.Orchestration_service import initiate_fuzzing
from FuzzCore.services.parser_service import parse_OpenApi_file

router = APIRouter()


class BaseAlgorithm(BaseModel):
    file_path: str
    algorithm_type: str

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


@router.post('/fuzz')
async def StartFuzzing(request: BaseAlgorithm):
    params = create_algorithm_params(**request.model_dump())

    openApi_data = parse_OpenApi_file(request.file_path)

    possible_scenarios_options = list(openApi_data['functions'].keys())

    initiate_fuzzing(params, openApi_data['base_url'], openApi_data['functions'],
                     openApi_data['ids'], possible_scenarios_options)

    return
