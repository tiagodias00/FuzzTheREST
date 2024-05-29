import requests
import os
import json
from dotenv import load_dotenv

from FuzzCore.services.mapper_service import convert_http_requests, BasePayload


def initiate_fuzzing(data, base_url, functions_data, ids, scenarios):
    load_dotenv()

    env_url = os.getenv('ALGORITHM_BASE_URL')
    if not env_url:
        raise ValueError("API_URL is not set in the environment variables.")

    url = f"{env_url}/execution"
    headers = {'Content-Type': 'application/json'}


    basepayload = {
        "algorithm_type": data.algorithm_type,
        "base_url": base_url,
        "function": convert_http_requests(functions_data),
        "ids": ids,
        "scenarios": scenarios
    }
    for key, value in data.dict().items():
        if key not in basepayload:
            basepayload[key] = value

    payload = BasePayload(**basepayload)
    payload_json = payload.json()
    requests.post(url, headers=headers, data=payload_json)

    return
