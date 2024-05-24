import copy

import yaml

from FuzzCore.Taxonomy import Schema, Object, Attribute, Parameter, RequestBody, HTTPRequest
from utils import fill_values


def create_Schema(name,object_data, existing_objects: dict):
    """
    Constructs a Schema instance from given object data.

    Args:
        object_data (dict): Raw schema data from OpenAPI specification.
        existing_objects (dict): A dictionary of pre-existing schemas for resolving references.

    Returns:
        Schema: The constructed Schema instance with populated Objects and Attributes.
    """
    if 'properties' in object_data:
        properties = object_data['properties']
        obj = Object(attributes=[])
        for prop_name, prop_data in properties.items():
            if 'type' in prop_data:
                prop_type = prop_data['type']
                if prop_type == 'array':
                    if 'type' in prop_data['items']:
                        item_type = prop_data['items'].get('type')
                        attribute = Attribute(type=[item_type], name=prop_name)
                        obj.attributes.append(attribute)
                    elif '$ref' in prop_data['items']:
                        ref_schema_name = prop_data['items']['$ref'].split('/')[-1]
                        referenced_schema = copy.deepcopy(existing_objects.get(ref_schema_name))
                        attribute = Attribute(type=[referenced_schema], name=prop_name)
                        obj.attributes.append(attribute)
                else:
                    attribute = Attribute(type=prop_type, name=prop_name)
                    obj.attributes.append(attribute)
            elif '$ref' in prop_data:
                ref_schema_name = prop_data['$ref'].split('/')[-1]
                referenced_schema = copy.deepcopy(existing_objects.get(ref_schema_name))
                attribute = Attribute(type=referenced_schema, name=prop_name)
                obj.attributes.append(attribute)

        return Schema(schema_name=name, objects=[obj])
    else:
        prop_data = object_data['content']['application/json']['schema']
        if '$ref' in prop_data:
            ref_schema_name = prop_data['$ref'].split('/')[-1]
            return copy.deepcopy(existing_objects.get(ref_schema_name))

        elif prop_data['type'] == "array":
            ref_schema_name = prop_data['items']['$ref'].split('/')[-1]
            objects=copy.deepcopy(existing_objects.get(ref_schema_name).objects)
            return Schema(schema_name=name, objects=[objects])


def create_schemas_and_ids(spec):
    schemas = {}
    ids = {}

    for object_name, object_data in spec['components']['schemas'].items():
        schema = create_Schema(object_name,object_data, schemas)
        schemas[object_name] = schema

    for object_name, object_data in spec['components']['requestBodies'].items():
        schema = create_Schema(object_name,object_data, schemas)
        schemas[object_name] = schema
    return schemas, ids

def parse_OpenApi_file(file_path: str):
    with open(file_path, 'r') as file:
        spec = yaml.safe_load(file)

    # Extract the base connection string (servers -> url)
    base_url = spec['servers'][0]['url']

    # Load schemas
    schemas = {}

    # ID dicts
    ids = {}

    schemas,ids=create_schemas_and_ids(spec)


    httpRequests = {}
    for path, path_item in spec['paths'].items():
        for method, operation in path_item.items():
            request_name = operation.get('operationId')
            request_body = operation.get('requestBody')
            request_parameters = operation.get('parameters')
            input_schema = None
            parameter_name = None
            parameter_in = None
            parameter_schema_name = None
            parameter_type = None
            schema = None

            function_parameters: list = []

            # Extract parameters
            if request_parameters != None:
                for parameters in request_parameters:
                    if request_parameters != None:
                        parameter_name = parameters['name']
                        parameter_in = parameters['in']
                        parameter_schema_name = parameters['schema']['type']

                        if parameter_schema_name == 'array':
                            parameter_schema_name = f"[{parameters['schema']['items']['type']}]"

                    function_parameters.append(Parameter(parameter_name,parameter_in, parameter_schema_name, copy.deepcopy(parameter_schema_name)))

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
                input_body = None
            else:
                input_body = RequestBody(schema, copy.deepcopy(schema))
            http_request = HTTPRequest(path, input_applicaton, method.upper(), function_parameters, input_body)
            function = fill_values(http_request, False, None, False, ids)

            # Store the information in the functions dictionary
            httpRequests[request_name] = function

    return {
        "httpRequests": httpRequests,
        "base_url": base_url,
        "ids":ids
    }
