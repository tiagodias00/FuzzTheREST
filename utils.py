import copy
import random
import string
import struct
import sys

from textblob import Word

import FuzzCore.Taxonomy
from FuzzCore.Taxonomy import Schema


def fill_body_values(schema, old_sample, contains_previous, mutation_methods, schema_name, store_id, ids):
    if schema is not None:
        sample = copy.deepcopy(schema)
        if contains_previous:
            sample = fill_previous_body(sample, old_sample)

        for item in sample.attributes:

            if isinstance(item.type, list):
                list_size = random.randint(0, 100)
                values = []

                if list_size <= len(item.type):
                    values = item.type[0:list_size]
                else:
                    attr = search_attr(schema, item.name)
                    values = [attr.type[0]] * list_size
                    values[0:len(item.type)] = item.type

                for i in range(list_size):
                    if type(values[i]) is Schema:
                        attr = search_attr(sample, item.name)
                        if type(attr.type) is list:
                            values[i] = fill_body_values(attr.type[0].objects[0], values[i].objects[0], contains_previous,
                                                         mutation_methods, item.name, store_id, ids)
                        else:
                            values[i] = fill_body_values(attr.type.objects[0], values[i].objects[0], contains_previous,
                                                         mutation_methods, item.name, store_id, ids)

                    else:
                        if type(values[i]) is str and values[i] in {"integer", "double", "float", "string", "boolean"}:
                            values[i] = get_mutated_value(None, values[i], None,
                                                          Word(schema_name.capitalize()).singularize(), ids)
                        else:
                            values[i] = get_mutated_value(values[i], None, mutation_methods[type(values[i])],
                                                          Word(schema_name.capitalize()).singularize(), ids)
                attrSample = search_attr(sample, item.name)
                attrSample.value = values

                if item.is_id and store_id:
                    for value in values:
                        if value not in ids[Word(schema_name.capitalize()).singularize()]:
                            ids[Word(schema_name.capitalize()).singularize()].append(value)

            else:
                if isinstance(item.type, Schema):
                    attrSample = search_attr(sample, item.name)
                    attrSchema = search_attr(schema, item.name)

                    result = copy.deepcopy(
                        fill_body_values(attrSchema.type.objects[0], item.type.objects[0], contains_previous, mutation_methods,
                                         item.name, store_id, ids))
                    attrSample.type.objects[0] = result

                else:
                    if isinstance(item.type, str) and item.type in {"integer", "double", "float", "string", "boolean"}:
                        attr = search_attr(sample, item.name)
                        attr.value = get_mutated_value(None, item.type, None,
                                                       Word(schema_name.capitalize()).singularize(), ids)
                    else:
                        attr = search_attr(sample, item.name)

                        attr.value = get_mutated_value(item.type, None, mutation_methods[item.type],
                                                       Word(schema_name.capitalize()).singularize(), ids)
                    if item.name == 'id' and store_id:
                        attr = search_attr(sample, item.name)
                        if attr not in ids[Word(schema_name.capitalize()).singularize()]:
                            ids[Word(schema_name.capitalize()).singularize()].append(copy.deepcopy(attr))

        return sample


def search_attr(schema, name):
    for attr in schema.attributes:
        if attr.name == name:
            return attr


def fill_previous_body(schema, old_sample):
    sample = copy.deepcopy(schema)
    for item in old_sample.attributes:
        if isinstance(item.type, list):
            if len(item.type) > 0:
                if item.type[0] is dict:
                    #TODO Implement to when it is a dict inside a list
                    raise ValueError("Unsuported dict inside list verification")
                else:
                    attr = search_attr(sample, item.name)
                    attr.type = item.type
        else:
            attr = search_attr(sample, item.name)
            if isinstance(item.type, Schema):
                attr.type.objects[0] = fill_previous_body(attr.type.objects[0], item.type.objects[0])
            else:
                attr.type = item.type

    return sample


def fill_parameter_values(input_parameters, contains_previous, mutation_methods, ids):
    for parameter in input_parameters:
        parameter_name = parameter.name.lower()
        if 'id' in parameter_name:
            parameter_name = parameter_name.replace('id', '').capitalize()

        if parameter.schema_info.startswith('['):
            list_size = random.randint(1, 100)
            values = []
            if(contains_previous):
                if list_size <= len(parameter.sample):
                    values = parameter.sample[0:list_size]
                else:
                    values = [random_generation(type(parameter.sample[0]))] * list_size
                    values[0:len(parameter.sample)] = parameter.sample

                    for i in range(list_size):
                        values[i] = get_mutated_value(values[i], None, mutation_methods[type(values[i])], parameter_name,
                                                      ids)
            else:
                for i in range(list_size):
                    values.append(get_mutated_value(None, parameter.schema_info[1:-1], None, parameter_name,ids))
            parameter.sample=values
        else:
            if contains_previous:
                if(type(parameter.sample) is FuzzCore.Taxonomy.Attribute):
                    parameter.sample.value = get_mutated_value(parameter.sample.value, parameter.sample.type,
                                                     mutation_methods[type(parameter.sample.value)], parameter.sample.name,
                                                     ids)
                else:
                    if type(parameter.sample) not in mutation_methods:
                        print(parameter.sample)
                    parameter.sample = get_mutated_value(parameter.sample, parameter.schema_info,
                                                     mutation_methods[type(parameter.sample)], parameter_name,
                                                     ids)
            else:
                parameter.sample = get_mutated_value(None, parameter.schema_info, None, parameter_name, ids)

    return input_parameters


def fill_values(function, contains_previous_values, mutation_methods, store_id, ids):
    function.parameters = fill_parameter_values(function.parameters, contains_previous_values, mutation_methods, ids)
    if function.request_body is not None:
        test_for_list = function.request_body.schema_info.objects[0]
        if type(test_for_list) is list:
            list_size = random.randint(0, 100)
            list_schema = test_for_list[0]
            items = []
            for i in range(list_size):
                items.append(
                    fill_body_values(list_schema, function.request_body.sample.objects[0], contains_previous_values,
                                     mutation_methods, function.request_body.schema_info.name, store_id, ids))

            function.request_body.sample.objects = items
        else:
            function.request_body.sample.objects[0] = fill_body_values(function.request_body.schema_info.objects[0],
                                                                       function.request_body.sample.objects[0],
                                                                       contains_previous_values, mutation_methods,
                                                                       function.request_body.schema_info.name, store_id,
                                                                       ids)

    return function


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
            truncation_length = random.randint(0, len(data) - 1)
            return data[:-truncation_length]
        else:
            return data
    elif isinstance(data, bytes):
        if len(data) > 1:
            truncation_length = random.randint(0, len(data) - 1)
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
def get_mutated_value(old_value, datatype, method, schema_name, ids):
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


int_mutation_methods = [bit_flips, byte_shuffling, bytes_substitution, arithmetic_addition, arithmetic_subtraction,
                        arithmetic_multiplication, arithmetic_division, random_generation, dictionary_fuzzy]
float_mutation_methods = [bit_flips, byte_shuffling, bytes_substitution, arithmetic_addition, arithmetic_subtraction,
                          arithmetic_multiplication, arithmetic_division, random_generation]
bool_mutation_methods = [bit_flips, byte_shuffling, random_generation]
byte_mutation_methods = [bit_flips, byte_shuffling, byte_injection, byte_deletion, bytes_substitution, truncation,
                         arithmetic_addition, arithmetic_subtraction, arithmetic_multiplication, arithmetic_division,
                         random_generation]
str_mutation_methods = [bit_flips, byte_shuffling, byte_injection, byte_deletion, bytes_substitution, truncation,
                        random_generation]

# Combine all mutation methods into a single list
mutation_methods = [int_mutation_methods, float_mutation_methods, bool_mutation_methods, byte_mutation_methods,
                    str_mutation_methods]
