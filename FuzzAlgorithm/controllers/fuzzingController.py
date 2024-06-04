from typing import Tuple, List

from fastapi import APIRouter, Depends, HTTPException, Body
from pydantic import BaseModel, create_model

from FuzzAlgorithm.services.IfuzzAlgorithmService import IFuzzingService
from FuzzAlgorithm.services.ParsingService import parse_http_request, parse_http_requests
from FuzzAlgorithm.services.QlearningService import QlearningService

router = APIRouter()

generic_fields = {
    'algorithm_type': (str, ...),
    'base_url': (str, ...),
    'function': (dict, ...),
    'ids': (dict, ...),
    'scenarios': (List[List[str]],...)
}

algorithm_fields = {
    'Qlearning': {
        'max_steps_per_episode': (int, ...),
        'exploration_rate': (float, ...),
        'num_episodes': (int, ...),
    },
    'default': {}
}


def create_algorithm_data(data: dict):
    algorithm_type = data.get('algorithm_type', 'default')
    fields = generic_fields.copy()
    fields.update(algorithm_fields.get(algorithm_type, {}))
    dynamicModel = create_model(f'{algorithm_type}DataModel', **fields)
    return dynamicModel(**data)


async def getFuzzService(data: dict) -> Tuple[IFuzzingService, BaseModel]:
    data_model = create_algorithm_data(data)
    algorithm_type = data_model.algorithm_type
    if algorithm_type == "Qlearning":
        return QlearningService(), data_model
    else:
        raise HTTPException(status_code=400, detail="Unsupported algorithm type")


@router.post("/execution")
async def initialize(data: dict = Body(...), service_data_model=Depends(getFuzzService)):
    service, data_model = service_data_model
    data_model.function = parse_http_requests(data['function'])
    result = await service.fuzz(data_model)
    if result is None:
        raise HTTPException(status_code=404, detail="Error initializing FuzzAlgorithm")
    return {
        "result": result
    }
