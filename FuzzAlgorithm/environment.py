import copy
import hashlib
import traceback

import gym
import requests
from gym.spaces import MultiDiscrete, Discrete

import FuzzCore.Taxonomy
from utils import fill_values
import urllib.parse


class APIFuzzyTestingEnvironment(gym.Env):
    def __init__(self, base_url, function, mutation_methods, ids):
        super(APIFuzzyTestingEnvironment, self).__init__()
        self.function = function
        self.base_url = base_url
        self.response = None
        self.mutation_methods = mutation_methods  # List of mutation methods.
        self.action_space: MultiDiscrete = MultiDiscrete([len(methods) for methods in mutation_methods])
        self.observation_space: Discrete = Discrete(5)  # Possible HTTP error codes.
        self.done = False
        self.ids = ids

    def step(self, action, requests_log, crashes=None, hangs=None):
        # Execute the action on the API and get the response
        mutation_methods = {}
        mutation_methods[int] = self.mutation_methods[0][action[0]]
        mutation_methods[float] = self.mutation_methods[1][action[1]]
        mutation_methods[bool] = self.mutation_methods[2][action[2]]
        mutation_methods[bytes] = self.mutation_methods[3][action[3]]
        mutation_methods[str] = self.mutation_methods[4][action[4]]

        resp = ""
        count = -1

        while type(resp) is str:
            count = count + 1
            if self.function.method == 'POST':
                if count == 5:
                    print("stuck here")
                    self.function = fill_values(self.function, False, mutation_methods, True, self.ids)
                    count = 0
                else:
                    self.function = fill_values(self.function, True, mutation_methods, True, self.ids)
            else:
                if count == 5:
                    self.function = fill_values(self.function, False, mutation_methods, False, self.ids)
                    count = 0
                else:
                    self.function = fill_values(self.function, True, mutation_methods, False, self.ids)

            resp = self._execute_action(self.function, crashes, hangs)

        self.response = resp
        requests_log.append({"status_code": self.response.status_code, "message": self.response.content})
        print(self.response.text)
        self._update_environment_state(requests_log)

        # Calculate the reward based on the response
        reward = self._calculate_reward()

        # Return the new state, reward, and episode completion status
        return self.state, reward, self.done

    def reset(self):
        self.state = 1
        self.done = False
        return self.state

    def _execute_action(self, function, crashes=None, hangs=None):
        if crashes is None:
            crashes = {}
        if hangs is None:
            hangs = {}
        parameters = {}
        headers = {'Content-type': function.content_type, 'accept': '*/*'}
        response = None

        path: str = copy.deepcopy(function.url)
        if len(function.parameters) > 0:
            for item in function.parameters:
                if item.name in path:
                    sample = item.sample
                    if (isinstance(item.sample, FuzzCore.Taxonomy.Attribute)):
                        sample = item.sample.value
                    path = safe_replace_path(path, item.name, sample)
                else:
                    parameters[item.name] = str(item.sample)
        try:
            if function.method == 'GET':
                if len(parameters) > 0:
                    response = requests.get(self.base_url + path, params=parameters, timeout=40)
                else:
                    response = requests.get(self.base_url + path, timeout=40)

            elif function.method == 'PUT':
                sample = function.request_body.to_dict_request() if function.request_body else None
                if len(parameters) > 0:
                    response = requests.put(self.base_url + path, json=sample, headers=headers,
                                            params=parameters, timeout=40)
                else:
                    response = requests.put(self.base_url + path, json=sample, headers=headers,
                                            timeout=40)

            elif function.method == 'DELETE':
                sample = function.request_body.to_dict_request() if function.request_body else None
                if len(parameters) > 0:
                    response = requests.delete(self.base_url + path, json=sample, headers=headers,
                                               params=parameters, timeout=40)
                else:
                    response = requests.delete(self.base_url + path, json=sample, headers=headers,
                                               timeout=40)
            elif function.method == 'PATCH':
                sample = function.request_body.to_dict_request() if function.request_body else None
                if function.content_type == "multipart/form-data":
                    files = {'plant': sample.pop('plant')}
                    if len(parameters) > 0:
                        response = requests.patch(self.base_url + path, json=sample, files=files,
                                                 params=parameters,headers=headers, timeout=40)
                    else:
                        response = requests.patch(self.base_url + path,json=sample, files=files,headers=headers,
                                                 timeout=40)
                else:
                    if len(parameters) > 0:
                        response = requests.patch(self.base_url + path, json=sample, headers=headers,
                                                params=parameters, timeout=40)
                    else:
                        response = requests.patch(self.base_url + path, json=sample, headers=headers,
                                                timeout=40)
            elif function.method == 'POST':
                sample = function.request_body.to_dict_request() if function.request_body else None
                if function.content_type == "multipart/form-data":
                    files = {'file': sample.pop('file')}
                    if len(parameters) > 0:
                        response = requests.post(self.base_url + path, json=sample, files=files,
                                                 params=parameters, timeout=40)
                    else:
                        response = requests.post(self.base_url + path, json=sample, files=files,
                                                 timeout=40)
                else:
                    if len(parameters) > 0:
                        response = requests.post(self.base_url + path, json=sample,
                                                 headers=headers, params=parameters, timeout=40)
                    else:
                        response = requests.post(self.base_url + path, json=sample,
                                                 headers=headers, timeout=40)
            response.raise_for_status()
            return response
        except requests.exceptions.Timeout as e:
            log_and_track_hangs(e, function, hangs)
            return "error"
        except requests.exceptions.HTTPError as e:
            if response.status_code >= 500:
                log_and_track_crash(e, function, crashes)
            return response
        except Exception as e:
            return "error"

    def _calculate_reward(self):
        # Implement the logic to calculate the reward based on the API response
        # You can define a reward function that suits your testing objective
        # Return the reward value
        if int(self.response.status_code) in range(100, 200):
            return 0
        elif int(self.response.status_code) in range(200, 300):
            return 5
        elif int(self.response.status_code) in range(300, 400):
            return 5
        elif int(self.response.status_code) in range(400, 500):
            return -20
        elif int(self.response.status_code) >= 500:
            return 10

        return 0

    def _update_environment_state(self, requests_log):
        # Implement any necessary state updates based on the API response
        # For example, update the state with new information after each request
        # Change the state
        if int(self.response.status_code) in range(100, 200):
            self.state = 0
        elif int(self.response.status_code) in range(200, 300):
            self.state = 1
        elif int(self.response.status_code) in range(300, 400):
            self.state = 2
        elif int(self.response.status_code) in range(400, 500):
            self.state = 3
        elif int(self.response.status_code) >= 500:
            self.state = 4
            self.done = True
            requests_log.append({"status_code": self.response.status_code, "message": self.response.content})

    def _change_environment_function(self, function):
        self.function = function

    def render(self, mode='human'):
        # Implement the logic to visualize the environment if needed
        if mode == 'human':
            # Print the current state or any relevant information for human visualization
            print("Current state:", self.state)
            print("Last response status code:", self.response.status_code)
            # Print any other relevant information about the environment

        elif mode == 'machine':
            # Return the current state or any relevant information for machine visualization
            # You can return it as a dictionary or in any other appropriate format
            return {'current_state': self.state, 'last_response_status': self.response.status_code}

        else:
            raise ValueError("Invalid render mode. Supported modes are 'human' and 'machine'.")

        pass


def get_unique_crash_identifier(exception):
    exc_type = type(exception).__name__
    exc_message = str(exception)
    stack_trace_elements = traceback.format_tb(exception.__traceback__)
    limited_stack_trace = ''.join(stack_trace_elements[:5])
    unique_hash_input = f"{exc_type}:{exc_message}:{limited_stack_trace}"
    return hashlib.sha256(unique_hash_input.encode()).hexdigest()


def log_and_track_crash(exception, function, crash_dict):
    crash_id = get_unique_crash_identifier(exception)
    if crash_id in crash_dict:
        crash_dict[crash_id]['count'] += 1
    else:

        crash_dict[crash_id] = {
            'count': 1,
            'error_message':exception.response.text,
            'stack_trace': ''.join(traceback.format_tb(exception.__traceback__)[5:15]),
            'sample_input':f"url:{exception.request.url},\n body: {exception.request.body}",
        }
    return crash_dict


def get_unique_hang_identifier(exception, function):
    exc_type = type(exception).__name__
    exc_message = str(exception)
    unique_hash_input = f"{exc_type}:{exc_message}:{function.url}:{function.method}"
    return hashlib.sha256(unique_hash_input.encode()).hexdigest()


def log_and_track_hangs(exception, function, hang_dict):
    hang_id = get_unique_hang_identifier(exception, function)
    if hang_id in hang_dict:
        hang_dict[hang_id]['count'] += 1
    else:
        hang_dict[hang_id] = {
            'count': 1,
            'error_message': str(exception),
            'url': function.url,
            'method': function.method,
            'parameters': function.parameters,
        }
    return hang_dict

def safe_replace_path(path, item_name, sample):
    encoded_sample = str(sample).replace('/', '%2F')
    return path.replace('{' + item_name + '}', encoded_sample)