from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from FuzzAlgorithm.services.FuzzAlgorithmService import FuzzAlgorithmService

router = APIRouter()


class InitializationData(BaseModel):
    base_url: str
    function: dict
    ids: dict
    max_steps_per_episode: int
    exploration_rate: float
    num_episodes: int


def getFuzzService():
    return FuzzAlgorithmService()


@router.post("/execution")
async def initialize(data: InitializationData, service=Depends(getFuzzService)):
    result = service.fuzz(data)
    if(result is None):
        raise HTTPException(status_code=404, detail="Error initializing FuzzAlgorithm")
    return {
        "message": "FuzzAlgorithm initialized"}
