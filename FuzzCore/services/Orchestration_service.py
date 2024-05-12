import requests
import os
import json
from dotenv import load_dotenv


def initiate_fuzzing(data, base_url, functions_data, ids, possible_scenarios):
    env_path = 'C:\\Users\\franc\\Documents\\FuzzTheREST\\env.env'
    load_dotenv(dotenv_path=env_path)

    env_url = os.getenv('ALGORITHM_BASE_URL')
    if not env_url:
        raise ValueError("API_URL is not set in the environment variables.")

    url = f"{env_url}/execution"
    headers = {'Content-Type': 'application/json'}

    scenarios = [
        ["addPet", "updatePet", "getPetById", "findPetsByStatus", "findPetsByTags", "uploadFile", "updatePetWithForm",
         "deletePet"],
        ["createUser", "loginUser", "updateUser", "logoutUser", "getUserByName", "deleteUser"],
        ["placeOrder", "getOrderById", "getInventory", "deleteOrder"]
    ]
    basepayload = {
        "algorithm_type": data.algorithm_type,
        "base_url": base_url,
        "ids": ids,
    }
    for key, value in data.dict().items():
        if key not in basepayload:
            basepayload[key] = value

    for scenario_functions in scenarios:
        for function in scenario_functions:
            basepayload['function'] = functions_data[function]

            payload_json = json.dumps(basepayload)
            requests.post(url, headers=headers, data=payload_json)

    return
