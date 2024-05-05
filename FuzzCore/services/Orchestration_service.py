import json

import requests
import os
from dotenv import load_dotenv


def initiate_fuzzing(data, base_url, function_data,ids):
    env_path = 'C:\\Users\\franc\\Documents\\FuzzTheREST\\env.env'
    load_dotenv(dotenv_path=env_path)

    env_url = os.getenv('ALGORITHM_BASE_URL')
    if not env_url:
        raise ValueError("API_URL is not set in the environment variables.")
    url = f"{env_url}/execution"
    headers = {'Content-Type': 'application/json'}
    payload = {
        "base_url": base_url,
        "function": function_data,
        "ids": ids,
        "max_steps_per_episode": data.max_steps_per_episode,
        "exploration_rate": data.exploration_rate,
        "num_episodes": data.num_episodes
    }
    payload_json = json.dumps(payload)

    response = requests.post(url, headers=headers, data=payload_json)

    return response
