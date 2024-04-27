import copy

import yaml

from utils import fill_values


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


def parse_OpenApi_file(file_path: str):
    with open(file_path, 'r') as file:
        spec = yaml.safe_load(file)

    # Extract the base connection string (servers -> url)
    base_url = spec['servers'][0]['url']

    # Load schemas
    schemas = {}

    # ID dicts
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
            parameter_in = None
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
            if (request_body != None and 'content' in request_body):
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
            }, False, None, False, ids)

            # Store the information in the functions dictionary
            functions[function_name] = function

    return {
        'functions': functions,
        'base_url': base_url
    }
