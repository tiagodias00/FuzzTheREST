import copy
import pickle

import gym
import requests
from gym.spaces import MultiDiscrete, Discrete

from utils import fill_values




class APIFuzzyTestingEnvironment(gym.Env):
    def __init__(self, base_url, function, mutation_methods,ids):
        super(APIFuzzyTestingEnvironment, self).__init__()
        self.function = function
        self.base_url = base_url
        self.response = None
        self.mutation_methods = mutation_methods  # List of mutation methods.
        self.action_space: MultiDiscrete = MultiDiscrete([len(methods) for methods in mutation_methods])
        self.observation_space: Discrete = Discrete(5)  # Possible HTTP error codes.
        self.done = False
        self.ids = ids

    def step(self, action,requests_log):
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
                    self.function = fill_values(self.function, False, mutation_methods, True,self.ids)
                    count = 0
                else:
                    self.function = fill_values(self.function, True, mutation_methods, True,self.ids)
            else:
                if count == 5:
                    self.function = fill_values(self.function, False, mutation_methods, False,self.ids)
                    count = 0
                else:
                    self.function = fill_values(self.function, True, mutation_methods, False,self.ids)

            resp = self._execute_action(self.function)

        self.response = resp
        requests_log.append({"status_code": self.response.status_code, "message": self.response.content})

        self._update_environment_state(requests_log)

        # Calculate the reward based on the response
        reward = self._calculate_reward()

        # Return the new state, reward, and episode completion status
        return self.state, reward, self.done

    def reset(self):
        self.state = 1
        self.done = False
        return self.state

    def _execute_action(self, function):
        parameters = {}
        headers = {'Content-type': function.content_type, 'accept': '*/*'}


        path: str = copy.deepcopy(function.url)
        if len(function.parameters) > 0:
            for item in function.parameters:
                if item.name in path:
                    path = path.replace('{' + item.name + '}', str(item.sample))
                else:
                    parameters[item.name] = str(item.sample)
        try:
            if function.method == 'GET':
                if len(parameters) > 0:
                    return requests.get(self.base_url + path, params=parameters, timeout=40)
                else:
                    return requests.get(self.base_url + path, timeout=40)

            elif function.method == 'PUT':
                sample=function.request_body.to_dict_request()
                if len(parameters) > 0:
                    return requests.put(self.base_url + path, json=sample, headers=headers,
                                        params=parameters, timeout=40)
                else:
                    return requests.put(self.base_url + path, json=sample, headers=headers,
                                        timeout=40)

            elif function.method == 'DELETE':
                sample = function.request_done.to_dict_request() if function.request_body else None
                if len(parameters) > 0:
                    return requests.delete(self.base_url + path, json=sample, headers=headers,
                                           params=parameters, timeout=40)
                else:
                    return requests.delete(self.base_url + path, json=sample, headers=headers,
                                           timeout=40)

            elif function.method == 'POST':
                sample = function.request_body.to_dict_request()
                if function.content_type == "multipart/form-data":
                    files = {'file':sample.pop('file')}
                    if len(parameters) > 0:
                        return requests.post(self.base_url + path, json=sample, files=files,
                                             params=parameters, timeout=40)
                    else:
                        return requests.post(self.base_url + path, json=sample, files=files,
                                             timeout=40)
                else:
                    if len(parameters) > 0:
                        return requests.post(self.base_url + path, json=sample,
                                             headers=headers, params=parameters, timeout=40)
                    else:
                        return requests.post(self.base_url + path, json=sample,
                                             headers=headers, timeout=40)
        except:
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

    def _update_environment_state(self,requests_log):
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

    def serialize(self):
        return pickle.dumps(self)
