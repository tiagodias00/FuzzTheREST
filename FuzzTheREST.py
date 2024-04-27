# %% [markdown]
# # Imports

# %%
import gym, requests, random, sys, struct, string, os
import numpy as np
import yaml
import json, copy, time
from requests.exceptions import ChunkedEncodingError
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from textblob import Word

# %% [markdown]
# # Data Setup

# %%
def create_json_body(object_data, existing_objects: dict):
    """Converts components of the OpenAPI specifications to JSON objects.

    Args:
        object_data (yaml): component to be built.
        existing_objects (dict): components already built that may be referenced in other components.

    Returns:
        JSON: The component in a JSON format.
    """
    json_body = {}
    property_dict = {}

    if 'properties' in object_data:
        properties = object_data['properties']

        for prop_name, prop_data in properties.items():
            if 'type' in prop_data:
                prop_type = prop_data['type']
                if prop_type == 'array':
                    if 'type' in prop_data['items']:
                        array_type = prop_data['items']['type']
                        property_dict[prop_name] = [array_type]
                    elif '$ref' in prop_data['items']:
                        array_type = prop_data['items']['$ref']
                        property_dict[prop_name] = [existing_objects.get(prop_ref)]
                else:
                    property_dict[prop_name] = prop_type
            elif '$ref' in prop_data:
                prop_ref = prop_data['$ref'].split('/')[-1]
                property_dict[prop_name] = existing_objects.get(prop_ref)
        return property_dict
    else:
        prop_data = object_data['content']['application/json']['schema']
        if '$ref' in prop_data:
            return existing_objects.get(prop_data['$ref'].split('/')[-1])
        elif prop_data['type'] == "array":
            return [existing_objects.get(prop_data['items']['$ref'].split('/')[-1])]



# %%
def fill_body_values(schema, old_sample, contains_previous, mutation_methods, schema_name, store_id):
    if schema is not None:
        sample = copy.deepcopy(schema)
        if contains_previous:
            sample = fill_previous_body(sample, old_sample)

        for item in sample.items():
            if type(item[1]) is list:
                list_size = random.randint(0,100)
                values = []

                if list_size <= len(item[1]):
                    values = item[1][0:list_size]
                else:
                    values = [schema[item[0]][0]] * list_size
                    values[0:len(item[1])] = item[1]

                for i in range(list_size):
                    if type(values[i]) is dict:
                        if type(schema[item[0]]) is list:
                            values[i] = fill_body_values(schema[item[0]][0], values[i], contains_previous, mutation_methods, item[0], store_id)
                        else:
                            values[i] = fill_body_values(schema[item[0]], values[i], contains_previous, mutation_methods, item[0], store_id)

                    else:
                        if type(values[i]) is str and values[i] in {"integer", "double", "float", "string", "boolean"}:
                            values[i] = get_mutated_value(None, values[i], None, Word(schema_name.capitalize()).singularize())
                        else:
                            values[i] = get_mutated_value(values[i], None, mutation_methods[type(values[i])], Word(schema_name.capitalize()).singularize())

                sample[item[0]] = values

                if item[0] == 'id' and store_id:
                    for value in values:
                        if value not in ids[Word(schema_name.capitalize()).singularize()]:
                            ids[Word(schema_name.capitalize()).singularize()].append(value)

            else:
                if type(item[1]) is dict:
                        sample[item[0]] = fill_body_values(schema[item[0]], item[1], contains_previous, mutation_methods,item[0], store_id)
                else:
                    if type(item[1]) is str and item[1] in {"integer", "double", "float", "string", "boolean"}:
                        sample[item[0]] = get_mutated_value(None, item[1], None, Word(schema_name.capitalize()).singularize())
                    else:
                        sample[item[0]] = get_mutated_value(item[1], None,  mutation_methods[type(item[1])], Word(schema_name.capitalize()).singularize())

                    if item[0] == 'id' and store_id:
                        if sample[item[0]] not in ids[Word(schema_name.capitalize()).singularize()]:
                            ids[Word(schema_name.capitalize()).singularize()].append(sample[item[0]])

        return sample

def fill_previous_body(schema, old_sample):
    sample = copy.deepcopy(schema)
    for item in old_sample.items():
        if type(item[1]) is list:
            if len(item[1]) > 0:
                if item[1][0] is dict:
                    #TODO Implement to when it is a dict inside a list
                    raise ValueError("Unsuported dict inside list verification")
                else:
                    sample[item[0]] = item[1]
        else:
            if type(item[1]) is dict:
                sample[item[0]] = fill_previous_body(sample[item[0]], item[1])
            else:
                sample[item[0]] = item[1]


    return sample


def fill_parameter_values(input_parameters, contains_previous, mutation_methods):
    for parameter in input_parameters:
        parameter_name = parameter['name'].lower()
        if 'id' in parameter_name:
            parameter_name = parameter_name.replace('id', '').capitalize()
        if type(parameter['schema']) is list:
            list_size = random.randint(1,100)
            values = []
            if contains_previous:
                if list_size <= len(parameter['sample']):
                    values = parameter['sample'][0:list_size]
                else:
                    values = [random_generation(type(parameter['sample'][0]))] * list_size
                    values[0:len(parameter['sample'])] = parameter['sample']

                for i in range(list_size):
                    values[i] = get_mutated_value(values[i], None, mutation_methods[type(values[i])], parameter_name)

            else:
                for i in range(list_size):
                    values.append(get_mutated_value(None, parameter['schema'][0], None, parameter_name))

            parameter["sample"] = values

        else:
            if contains_previous:
                parameter['sample'] = get_mutated_value(parameter['sample'], parameter['schema'], mutation_methods[type(parameter['sample'])], parameter_name)
            else:
                parameter['sample'] = get_mutated_value(None, parameter['schema'], None, parameter_name)

    return input_parameters


def fill_values(function, contains_previous_values, mutation_methods, store_id):
    function['input_parameters'] = fill_parameter_values(function['input_parameters'], contains_previous_values, mutation_methods)

    if type(function['input_body']['schema']) is list:
        list_size = random.randint(0,100)
        list_schema = function['input_body']['schema'][0]
        items = []
        for i in range(list_size):
            items.append(fill_body_values(list_schema, function['input_body']['sample'], contains_previous_values, mutation_methods, function['input_body']['schema_name'], store_id))

        function['input_body']['sample'] = items
    else:
        function['input_body']['sample'] = fill_body_values(function['input_body']['schema'], function['input_body']['sample'], contains_previous_values, mutation_methods, function['input_body']['schema_name'], store_id)

    return function

# %% [markdown]
# # Mutation Methods

# %%
# Bit Flips: Randomly flips individual bits in the input data.
def bit_flips(data):
    if isinstance(data, str):
        chars = list(data)
        for i in range(len(chars)):
            char_code = ord(chars[i])
            flipped_code = char_code ^ random.getrandbits(16)
            chars[i] = chr(flipped_code)
        modified_data = ''.join(chars)
        return modified_data
    elif isinstance(data, bytes):
        flipped_data = bytearray(data)
        for i in range(len(flipped_data)):
            flipped_data[i] = flipped_data[i] ^ random.getrandbits(8)
        return bytes(flipped_data)
    elif isinstance(data, bool):
        flipped_data = not data
        return flipped_data
    else:
        raise ValueError("Unsupported data type for bit flips")

# Byte Shuffling: Shuffles the order of the bytes in the input data.
def byte_shuffling(data):
    if isinstance(data, str):
        char_list = list(data)
        random.shuffle(char_list)
        shuffled_string = ''.join(char_list)
        return shuffled_string
    elif isinstance(data, bytes):
        byte_list = list(data)
        random.shuffle(byte_list)
        return bytes(byte_list)
    elif isinstance(data, bool):
        return data
    else:
        raise ValueError("Unsupported data type for byte shuffling")

# Byte Injection/Deletion: Adds or removes random bytes, causing structural changes to the input data.
def byte_injection(data):
    if isinstance(data, str):
        code_points = list(data)
        code_point_to_inject = chr(random.randint(0, 1114111))
        index = random.randint(0, len(code_points))
        code_points.insert(index, code_point_to_inject)
        return ''.join(code_points)
    elif isinstance(data, bytes):
        mutated_data = bytearray(data)
        byte_to_inject = random.randint(0, 255)
        index = random.randint(0, len(mutated_data))
        mutated_data.insert(index, byte_to_inject)
        return bytes(mutated_data)
    else:
        raise ValueError("Unsupported data type for byte injection/deletion")

def byte_deletion(data):
    if isinstance(data, str):
        code_points = list(data)
        if len(code_points) > 0:
            index = random.randint(0, len(code_points) - 1)
            del code_points[index]
        return ''.join(code_points)
    elif isinstance(data, bytes):
        mutated_data = bytearray(data)
        if len(mutated_data) > 0:
            index = random.randint(0, len(mutated_data) - 1)
            del mutated_data[index]
        return bytes(mutated_data)
    else:
        raise ValueError("Unsupported data type for byte injection/deletion")

# Bytes Substitution: Randomly replaces bytes with others.
def bytes_substitution(data):
    if isinstance(data, str):
        mutated_data = ""
        for char in data:
            if random.random() < 0.5:  # 50% probability for substitution
                mutated_data += random.choice(string.printable)
            else:
                mutated_data += char
        return mutated_data
    elif isinstance(data, bytes):
        mutated_data = bytearray(data)
        for i in range(len(mutated_data)):
            mutated_data[i] = random.randint(0, 255)
        return bytes(mutated_data)
    else:
        raise ValueError("Unsupported data type for bytes substitution")

# Truncation: Shortens the input data by removing trailing bytes.
def truncation(data):
    if isinstance(data, str):
        if len(data) > 1:
            truncation_length = random.randint(0, len(data)-1)
            return data[:-truncation_length]
        else:
            return data
    elif isinstance(data, bytes):
        if len(data) > 1:
            truncation_length = random.randint(0, len(data)-1)
            return data[:-truncation_length]
        else:
            return data
    else:
        raise ValueError("Unsupported data type for truncation")

# Dictionary Fuzzy: only works for integers
def dictionary_fuzzy(schema_name, ids):
    if schema_name in ids.keys():
        if len(ids[schema_name]) != 0:
            value = random.choice(ids[schema_name])
            return value
    return None

def arithmetic_addition(data):
    if isinstance(data, float):
        return data + random.uniform(sys.float_info.min, sys.float_info.max)
    elif isinstance(data, int):
        new_value = data + random.randrange(-2147483648, 2147483647)
        if new_value > 2147483647 or new_value < -2147483648:
            return data
        return new_value
    else:
        raise ValueError("Unsupported data type for arithmetic operations")

def arithmetic_subtraction(data):
    if isinstance(data, float):
        return data - random.uniform(sys.float_info.min, sys.float_info.max)
    elif isinstance(data, int):
        new_value = data - random.randrange(-2147483648, 2147483647)
        new_value = new_value & 0xFFFFFFFF  # 0xFFFFFFFF represents a 32-bit mask (all 1's)
        # If the number exceeds the positive limit of 2147483647, convert to negative equivalent
        if new_value > 2147483647 or new_value < -2147483648:
            return data
        return new_value
    else:
        raise ValueError("Unsupported data type for arithmetic operations")

def arithmetic_multiplication(data):
    if isinstance(data, float):
        return data * random.uniform(sys.float_info.min, sys.float_info.max)
    elif isinstance(data, int):
        new_value = data * random.randrange(-2147483648, 2147483647)
        new_value = new_value & 0xFFFFFFFF  # 0xFFFFFFFF represents a 32-bit mask (all 1's)
        # If the number exceeds the positive limit of 2147483647, convert to negative equivalent
        if new_value > 2147483647 or new_value < -2147483648:
            return data
        return new_value
    else:
        raise ValueError("Unsupported data type for arithmetic operations")

def arithmetic_division(data):
    if isinstance(data, float):
        return data / random.uniform(sys.float_info.min, sys.float_info.max)
    elif isinstance(data, int):
        return data // random.randrange(-2147483648, 2147483647)
    else:
        raise ValueError("Unsupported data type for arithmetic operations")

# Random Generation: Randomly generates input of a certain type.
def random_generation(data_type):
    if data_type == str:
        size = random.randint(0, 500)  # Random size between int min and int max
        return ''.join(random.choice(string.printable) for _ in range(size))
    elif data_type == int:
        return random.randrange(-2147483648, 2147483647)  # Random integer between int min and int max
    elif data_type == float:
        return random.uniform(sys.float_info.min, sys.float_info.max)
    elif data_type == bool:
        return random.choice([True, False])
    elif data_type == bytes:
        size = random.randint(0, 500)  # Random size between 1 and 10
        return bytes(random.randint(0, 255) for _ in range(size))
    else:
        raise ValueError("Unsupported data type for random generation")

# %%
# Method to Convert to Binary
def to_binary(data):
    if isinstance(data, str):
        binary_data = data.encode('utf-8')
    elif isinstance(data, int):
        binary_data = struct.pack("i", data)
    elif isinstance(data, float):
        binary_data = struct.pack('d', data)
    elif isinstance(data, bool):
        binary_data = struct.pack('?', data)
    elif isinstance(data, bytes):
        binary_data = data
    else:
        raise ValueError("Unsupported data type")

    return binary_data

# Method to Convert From Binary to original data type.
def from_binary(binary_data, data_type):
    if data_type == str:
        output_value = binary_data.decode('utf-8')
    elif data_type == int:
        output_value = struct.unpack("i", binary_data)[0]
    elif data_type == float:
        output_value = struct.unpack('d', binary_data)[0]
    elif data_type == bool:
        output_value = struct.unpack('?', binary_data)[0]
    elif data_type == bytes:
        output_value = binary_data
    else:
        raise ValueError("Unsupported data type")

    return output_value

# %%
def get_mutated_value(old_value, datatype, method, schema_name):
        if old_value is None:
            if datatype == 'integer':
                return random_generation(int)
            elif datatype == 'float' or datatype == 'double':
                return random_generation(float)
            elif datatype == 'boolean':
                return random_generation(bool)
            elif datatype == 'string':
                return random_generation(str)
            else:
                random_generation(bytes)
        else:
            datatype = type(old_value)
            if method is random_generation:
                return random_generation(datatype)
            elif method is dictionary_fuzzy:
                new_value = dictionary_fuzzy(schema_name, ids)
                if new_value is None:
                    return old_value
                else:
                    return new_value
            if datatype is int or datatype is float:
                if method is arithmetic_division or method is arithmetic_addition or method is arithmetic_multiplication or method is arithmetic_subtraction:
                    return method(old_value)
                else:
                    new_value_bin = to_binary(old_value)
                    return from_binary(method(new_value_bin), datatype)
            else:
                return method(old_value)

# %% [markdown]
# # Reinforcement Learning Environment

# %%
import gym
from gym.spaces import MultiDiscrete, Discrete
import numpy as np

class APIFuzzyTestingEnvironment(gym.Env):
    def __init__(self, base_url, function, mutation_methods):
        super(APIFuzzyTestingEnvironment, self).__init__()
        self.function = function
        self.base_url = base_url
        self.response = None
        self.mutation_methods = mutation_methods  # List of mutation methods.
        self.action_space: MultiDiscrete = MultiDiscrete([len(methods) for methods in mutation_methods])
        self.observation_space: Discrete = Discrete(5) # Possible HTTP error codes.
        self.done = False

    def step(self, action):
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
            if self.function['method'] == 'POST':
                if count == 5:
                    print("stuck here")
                    self.function = fill_values(self.function, False, mutation_methods, True)
                    count = 0
                else:
                    self.function = fill_values(self.function, True, mutation_methods, True)
            else:
                if count == 5:
                    self.function = fill_values(self.function, False, mutation_methods, False)
                    count = 0
                else:
                    self.function = fill_values(self.function, True, mutation_methods, False)


            resp = self._execute_action(self.function)

        self.response = resp
        requests_log.append({"status_code": self.response.status_code, "message": self.response.content})

        self._update_environment_state()

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
        headers = {'Content-type': function['content-type'], 'accept': '*/*'}
        path: str = copy.deepcopy(function['path'])
        if len(function['input_parameters']) > 0:
            for item in function['input_parameters']:
                if item['name'] in path:
                    path = path.replace('{' + item['name'] + '}', str(item['sample']))
                else:
                    parameters[item['name']] = str(item['sample'])
        try:
            if function['method'] == 'GET':
                if len(parameters) > 0:
                    return requests.get(self.base_url + path, params=parameters, timeout=40)
                else:
                    return requests.get(self.base_url + path, timeout=40)

            elif function['method'] == 'PUT':
                if len(parameters) > 0:
                    return requests.put(self.base_url + path, json=function['input_body']['sample'], headers=headers, params=parameters, timeout=40)
                else:
                    return requests.put(self.base_url + path, json=function['input_body']['sample'], headers=headers, timeout=40)

            elif function['method'] == 'DELETE':
                if len(parameters) > 0:
                    return requests.delete(self.base_url + path, json=function['input_body']['sample'], headers=headers, params=parameters, timeout=40)
                else:
                    return requests.delete(self.base_url + path, json=function['input_body']['sample'], headers=headers, timeout=40)

            elif function['method'] == 'POST':
                if function['content-type'] == "multipart/form-data":
                    files = {'file': function['input_body']['sample'].pop('file')}
                    if len(parameters) > 0:
                        return requests.post(self.base_url + path, json=function['input_body']['sample'], files=files, params=parameters,timeout=40)
                    else:
                        return requests.post(self.base_url + path, json=function['input_body']['sample'], files=files, timeout=40)
                else:
                    if len(parameters) > 0:
                        return requests.post(self.base_url + path, json=function['input_body']['sample'], headers=headers, params=parameters,timeout=40)
                    else:
                        return requests.post(self.base_url + path, json=function['input_body']['sample'], headers=headers, timeout=40)
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


    def _update_environment_state(self):
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

# %%
class QLearningAgent:
    def __init__(self, env: APIFuzzyTestingEnvironment, mutation_methods, max_steps_per_episode, learning_rate=0.1, discount_factor=0.9, exploration_rate=0.1, min_exploration_rate=0.1, max_exploration_rate=1, exploration_decay_rate=0.01):
        self.env = env
        self.int_q_table = np.zeros([env.observation_space.n, len(mutation_methods[0])])
        self.float_q_table = np.zeros([env.observation_space.n, len(mutation_methods[1])])
        self.bool_q_table = np.zeros([env.observation_space.n, len(mutation_methods[2])])
        self.byte_q_table = np.zeros([env.observation_space.n, len(mutation_methods[3])])
        self.string_q_table = np.zeros([env.observation_space.n, len(mutation_methods[4])])
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.exploration_rate = exploration_rate
        self.min_exploration_rate = min_exploration_rate
        self.max_exploration_rate = max_exploration_rate
        self.exploration_decay_rate = exploration_decay_rate
        self.max_steps_per_episode = max_steps_per_episode
        self.episode_rewards = []  # To store the rewards obtained in each episode
        self.rewards_all_episodes=[]
        self.mutation_methods = mutation_methods
        self.mutation_counts = {i: {method: 0 for method in mutation_methods[i]} for i in range(env.observation_space.n)}
        self.mutation_rewards = {i: {method: [] for method in mutation_methods[i]} for i in range(env.observation_space.n)}
        self.state_visits = np.zeros(env.observation_space.n)
        self.q_value_convergence = {}
        self.num_episodes = 30

    def choose_action(self, state, int_q_table, float_q_table, bool_q_table, byte_q_table, string_q_table):
        # Epsilon-greedy exploration policy
        if random.uniform(0, 1) < self.exploration_rate:
            action = self.env.action_space.sample()
        else:
            action = []
            action.append(np.argmax(int_q_table[state,:]))
            action.append(np.argmax(float_q_table[state,:]))
            action.append(np.argmax(bool_q_table[state,:]))
            action.append(np.argmax(byte_q_table[state,:]))
            action.append(np.argmax(string_q_table[state,:]))
        return action

    def update_q_table(self, state, action, reward, new_state, q_table):
        q_table[state, action] = q_table[state, action] * (1 - self.learning_rate) + \
            self.learning_rate * (reward + self.discount_factor * np.max(q_table[new_state, :]))

    def train(self, num_episodes):
        self.q_value_convergence = {
            'int': [],
            'float': [],
            'bool': [],
            'byte': [],
            'string': []
        }

        self.num_episodes = num_episodes

        for episode in range(num_episodes):
            done = False
            state = self.env.reset()
            rewards_current_episode = 0

            print(episode)

            for step in range(self.max_steps_per_episode):
                action = self.choose_action(state, self.int_q_table, self.float_q_table, self.bool_q_table, self.byte_q_table, self.string_q_table)
                new_state, reward, done = self.env.step(action)
                self.update_q_table(state, action[0], reward, new_state, self.int_q_table)
                self.update_q_table(state, action[1], reward, new_state, self.float_q_table)
                self.update_q_table(state, action[2], reward, new_state, self.bool_q_table)
                self.update_q_table(state, action[3], reward, new_state, self.byte_q_table)
                self.update_q_table(state, action[4], reward, new_state, self.string_q_table)

                for i in range(len(self.mutation_counts)):
                    chosen_method = self.mutation_methods[i][action[i]]  # Get the chosen mutation method dynamically
                    self.mutation_counts[i][chosen_method] += 1
                    self.mutation_rewards[i][chosen_method].append(reward)

                state = new_state
                rewards_current_episode += reward
                self.episode_rewards.append(reward)
                self.state_visits[state] += 1

                if done is True:
                    break

            # Exploration rate decay
            self.exploration_rate = self.min_exploration_rate + \
                (self.max_exploration_rate - self.min_exploration_rate) * np.exp(-self.exploration_decay_rate*episode)

            self.rewards_all_episodes.append(rewards_current_episode)

            self.q_value_convergence['int'].append(np.copy(self.int_q_table))
            self.q_value_convergence['float'].append(np.copy(self.float_q_table))
            self.q_value_convergence['bool'].append(np.copy(self.bool_q_table))
            self.q_value_convergence['byte'].append(np.copy(self.byte_q_table))
            self.q_value_convergence['string'].append(np.copy(self.string_q_table))

        # Calculate and print the average reward per hundred episodes
        rewards_per_number_episodes = np.split(np.array(self.rewards_all_episodes),num_episodes/num_episodes)
        count = num_episodes
        print("********Average reward per number of episodes********\n")
        for r in rewards_per_number_episodes:
            print(count, ": ", str(sum(r/num_episodes)))
            count += num_episodes

    def plot_q_value_convergence(self, base_path):
        x = np.arange(0, self.num_episodes)
        data_types = ['int', 'float', 'bool', 'byte', 'string']
        for data_type in data_types:
            q_values = np.array(self.q_value_convergence[data_type])
            avg_q_values = np.mean(q_values, axis=(1, 2))  # Average over states and actions
            plt.plot(x, avg_q_values, label=data_type)

        plt.xlabel('Episodes')
        plt.ylabel('Average Q-value')
        plt.legend()
        plt.title('Q-value Convergence')
        plt.savefig(base_path + "q_value_convergence.png")
        plt.close()

    def plot_learning_curve(self, num_episodes):
        # Calculate the average reward over a fixed number of episodes (e.g., last 100 episodes) and plot the learning curve
        window_size = 10
        average_rewards = [np.mean(self.episode_rewards[i:i + window_size]) for i in range(len(self.episode_rewards) - window_size + 1)]
        plt.plot(range(window_size, num_episodes + 1), average_rewards)
        plt.xlabel('Episodes')
        plt.ylabel('Average Reward')
        plt.title('Learning Curve')
        plt.show()

    def plot_action_distribution(self, base_path):
        data_types = ['int', 'float', 'bool', 'byte', 'string']
        for i in range(len(self.mutation_counts)):
            mutation_methods = list(self.mutation_counts[i].keys())
            method_counts = list(self.mutation_counts[i].values())

            indices = np.arange(len(mutation_methods))

            # Define a list of colors for the columns
            colors = plt.cm.viridis(np.linspace(0, 1, len(mutation_methods)))

            # Use the 'colors' list to set different colors for each column
            bars = plt.bar(indices, method_counts, color=colors)

            plt.xticks(indices, indices)
            plt.xlabel('Mutation Method Index')
            plt.ylabel('Action Counts')
            plt.title(f'Action Distribution for {data_types[i]}')

            # Create custom legend handles for each mutation method
            legend_handles = [mpatches.Patch(color=colors[j], label=mutation_method.__name__) for j, mutation_method in enumerate(mutation_methods)]

            # Move the legend outside the plot
            plt.legend(handles=legend_handles, loc='upper left', bbox_to_anchor=(1, 1))

            # Annotate each bar with the exact number on top
            for j, count in enumerate(method_counts):
                plt.text(j, count + 0.1, str(count), ha='center', va='bottom')

            plt.savefig(base_path + "q_action_distribution_" + str(i) + ".png", bbox_inches='tight')
            plt.close()

    def plot_state_visits(self, base_path):
        states = list(range(len(self.state_visits)))
        visit_counts = list(self.state_visits)

        # Define legend labels for HTTP status code ranges
        legend_labels = ['1XX', '2XX', '3XX', '4XX', '5XX']

        # Define colors for each HTTP status code range
        colors = ['lightblue', 'green', 'yellow', 'orange', 'red']

        plt.bar(states, visit_counts, color=colors)
        plt.xlabel('HTTP Status Code Ranges')
        plt.ylabel('Number of Visits')
        plt.title('Number of Visits to Each HTTP Status Code Range')

        # Set x-axis ticks and labels to the legend labels
        plt.xticks(states, legend_labels)

        # Annotate each bar with the exact number on top
        for state, count in zip(states, visit_counts):
            plt.text(state, count + 0.1, str(count), ha='center', va='bottom')

        plt.savefig(base_path + "state_visits.png", bbox_inches='tight')
        plt.close()


    def test(self):
        for episode in range(5):
            state = self.env.reset()
            done = False

            print("*******Episode ", episode+1, "*******\n\n")
            for step in range(self.max_steps_per_episode):
                # Choose action with highest Q-value for current state
                self.env.render()
                # Take new action
                # time.sleep(0.3)
                action = []
                action.append(np.argmax(self.int_q_table[state,:]))
                action.append(np.argmax(self.float_q_table[state,:]))
                action.append(np.argmax(self.bool_q_table[state,:]))
                action.append(np.argmax(self.byte_q_table[state,:]))
                action.append(np.argmax(self.string_q_table[state,:]))
                new_state, reward, done = self.env.step(action)

                if done:
                    env.render()
                    if reward == 1:
                        # Agent reached the goal and won episode
                        print("****You reached the goal****")
                        # time.sleep(3)
                    break
                else:
                    print("****You lost****")
                    # time.sleep(3)

                state = new_state

def write_agent_report(base_folder, agent_name, agent: QLearningAgent):
    # time.sleep(3)
    try:
        directory = os.path.dirname(base_folder + "/" + agent_name + "/")
        if not os.path.exists(directory):
            os.makedirs(directory)

        # Decode bytes in requests_log
        requests_log_decoded = []
        for request in requests_log:
            decoded_request = {}
            for key, value in request.items():
                if isinstance(value, bytes):
                    decoded_request[key] = value.decode('utf-8')
                else:
                    decoded_request[key] = value
            requests_log_decoded.append(decoded_request)

        with open(base_folder + "/" + agent_name + "/report.log", "w") as file:
            file.write("\n\n------ List of IDs ------\n\n")
            json.dump(ids, file, indent=4)
            file.write("\n\n------ List of Requests ------\n\n")
            json.dump(requests_log_decoded, file, indent=4)
            file.write("\n\n------ Q-tables ------\n\n")
            file.write("   Int table\n")
            file.write(str(agent.int_q_table))
            file.write("\n   Float table\n")
            file.write(str(agent.float_q_table))
            file.write("\n   Bool table\n")
            file.write(str(agent.bool_q_table))
            file.write("\n   String table\n")
            file.write(str(agent.string_q_table))
            file.write("\n   Byte table\n")
            file.write(str(agent.byte_q_table))

            agent.plot_q_value_convergence(base_folder + "/" + agent_name + "/")
            agent.plot_action_distribution(base_folder + "/" + agent_name + "/")
            agent.plot_state_visits(base_folder + "/" + agent_name + "/")
    except IOError as e:
        print("Error:", e)

# %%
# Read the OpenAPI specification file (assuming it's in YAML format)

with open('openapi_petshop.yaml', 'r') as file:
    spec = yaml.safe_load(file)

# Extract the base connection string (servers -> url)
base_url = spec['servers'][0]['url']

# Load schemas
schemas = {}

#ID dicts
ids = {}

for object_name, object_data in spec['components']['schemas'].items():
    parameter_schema = create_json_body(object_data, schemas)
    schemas[object_name] = parameter_schema
    if 'id' in parameter_schema:
        ids[object_name] = []

for object_name, object_data in spec['components']['requestBodies'].items():
    parameter_schema = create_json_body(object_data, schemas)
    schemas[object_name] = parameter_schema
    if 'id' in parameter_schema:
        ids[object_name] = []

# Extract the functions, input schemas, and output schemas
functions = {}
for path, path_item in spec['paths'].items():
    for method, operation in path_item.items():
        function_name = operation.get('operationId')
        request_body = operation.get('requestBody')
        request_parameters = operation.get('parameters')
        input_schema = None
        parameter_name = None
        parameter_in  = None
        parameter_schema = None
        parameter_type = None
        schema = None

        function_parameters: list = []

        # Extract parameters
        if request_parameters != None:
            for parameters in request_parameters:
                if request_parameters != None:
                    parameter_name = parameters['name']
                    parameter_in = parameters['in']
                    parameter_schema = parameters['schema']['type']

                    if parameter_schema == 'array':
                        parameter_schema = [parameters['schema']['items']['type']]

                function_parameters.append({
                    "name": parameter_name,
                    "in": parameter_in,
                    "schema": parameter_schema,
                    "sample": copy.deepcopy(parameter_schema)
                })

        # Extract input schema
        if(request_body != None and 'content' in request_body):
            input_schema = request_body['content']
            if 'application/json' in input_schema:
                input_applicaton = 'application/json'
                input_schema = input_schema['application/json']['schema']
            elif 'application/octet-stream' in input_schema:
                input_applicaton = 'application/octet-stream'
                input_schema = input_schema['application/octet-stream']['schema']
            elif 'application/x-www-form-urlencoded' in input_schema:
                input_applicaton = 'application/x-www-form-urlencoded'
                input_schema = input_schema['application/x-www-form-urlencoded']['schema']
            elif 'multipart/form-data' in input_schema:
                input_applicaton = 'multipart/form-data'
                input_schema = input_schema['multipart/form-data']['schema']

            if 'type' in input_schema:
                if input_schema['type'] == 'array':
                    schema = "array"
                    schema_type = input_schema['items']
                    if 'type' in schema_type:
                        schema_type = input_schema['items']['type']
                    elif '$ref' in schema_type:
                        schema_name = input_schema['items']['$ref'].split('/')[-1]
                        schema = schemas.get(schema_name)
                else:
                    schema = input_schema['type']

            if '$ref' in input_schema:
                schema_name = input_schema['$ref'].split('/')[-1]
                schema = schemas.get(schema_name)

        if schema is None:
            input_body = {"schema": [], "sample": None}

        input_body = {"schema": schema, "sample": copy.deepcopy(schema), "schema_name": schema_name}

        function = fill_values({
            'path': path,
            'content-type': input_applicaton,
            'method': method.upper(),
            'input_parameters': function_parameters,
            'input_body': input_body
        }, False, None, False)

        # Store the information in the functions dictionary
        functions[function_name] = function


# %%
# Initialize mutation methods for different data types
# int_mutation_methods = [dictionary_fuzzy]
int_mutation_methods = [bit_flips, byte_shuffling, bytes_substitution, arithmetic_addition, arithmetic_subtraction, arithmetic_multiplication, arithmetic_division, random_generation, dictionary_fuzzy]
float_mutation_methods = [bit_flips, byte_shuffling, bytes_substitution, arithmetic_addition, arithmetic_subtraction, arithmetic_multiplication, arithmetic_division, random_generation]
bool_mutation_methods = [bit_flips, byte_shuffling, random_generation]
byte_mutation_methods = [bit_flips, byte_shuffling, byte_injection, byte_deletion, bytes_substitution, truncation, arithmetic_addition, arithmetic_subtraction, arithmetic_multiplication, arithmetic_division, random_generation]
str_mutation_methods = [bit_flips, byte_shuffling, byte_injection, byte_deletion, bytes_substitution, truncation, random_generation]

# Combine all mutation methods into a single list
mutation_methods = [int_mutation_methods, float_mutation_methods, bool_mutation_methods, byte_mutation_methods, str_mutation_methods]

# scenarios = [["addPet", "updatePet", "getPetById", "findPetsByStatus", "findPetsByTags", "uploadFile", "updatePetWithForm", "deletePet"]]
# scenarios = [["createUser", "loginUser", "updateUser", "logoutUser", "getUserByName", "deleteUser"]]
# scenarios = [["placeOrder", "getOrderById", "getInventory", "deleteOrder"]]
# scenarios = [["loginUser", "addPet", "uploadFile", "getPetById", "placeOrder", "getInventory", "getOrderById", "logoutUser"]]
scenarios = [["addPet", "updatePet", "getPetById", "findPetsByStatus", "findPetsByTags", "uploadFile", "updatePetWithForm", "deletePet"], ["createUser", "loginUser", "updateUser", "logoutUser", "getUserByName", "deleteUser"], ["placeOrder", "getOrderById", "getInventory", "deleteOrder"]]
env = None
requests_log=[]
for scenario_functions in scenarios:
    for function in scenario_functions:
        requests_log = []
        print("Starting ")

        if env is None:
            # Create an instance of the API testing environment
            env = APIFuzzyTestingEnvironment(base_url, functions[function], mutation_methods)
        else:
            env._change_environment_function(functions[function])

        # Create an instance of the Q-Learning agent
        agent = QLearningAgent(env,mutation_methods,10,exploration_rate=1)

        # Train the agent
        agent.train(num_episodes=500)

        write_agent_report("execution/train/", function, agent)

        requests_log = []

        # Test the agent
        agent.test()

        write_agent_report("execution/test/", function, agent)

        print(function + " ended.")

env.close()

# #%%
# import requests
# import random

# data = {"file": random_generation(bytes), "additionalMetadata": "Nothing"}

# files = {'file': data.pop("file")}
# print(data)
# response = requests.post("http://localhost:81/v3/pet/1/uploadImage/", data=data, files=files)
# print(response.content)
# # %%
