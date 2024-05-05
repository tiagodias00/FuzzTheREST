from fastapi import APIRouter
from pydantic import BaseModel

from FuzzCore.services.Orchestration_service import initiate_fuzzing
from FuzzCore.services.parser_service import parse_OpenApi_file

router = APIRouter()


class Request(BaseModel):
    file_path: str
    max_steps_per_episode: int
    exploration_rate: float
    num_episodes: int


@router.post('/fuzz')
async def get_openapi_spec(request: Request):
    openApi_data = parse_OpenApi_file(request.file_path)
    possible_scenarios_options = list(openApi_data['functions'].keys())
    scenarios = [
        ["addPet", "updatePet", "getPetById", "findPetsByStatus", "findPetsByTags", "uploadFile", "updatePetWithForm",
         "deletePet"], ["createUser", "loginUser", "updateUser", "logoutUser", "getUserByName", "deleteUser"],
        ["placeOrder", "getOrderById", "getInventory", "deleteOrder"]]  #scenarios for testing
    for scenario_functions in scenarios:
        for function in scenario_functions:
            initiate_fuzzing(request, openApi_data['base_url'], openApi_data['functions'][function],openApi_data['ids'])
    return
