from typing import Dict

from FuzzCore.Taxonomy  import Attribute, Object, Schema, Parameter, RequestBody, HTTPRequest


def parse_attribute(data: Dict) -> Attribute:
    return Attribute(
        type=convert_attribute_type(data.get('type')),
        name=data['name'],
        is_id=data.get('is_id', False),
        value=convert_attribute_value(data.get('value'))
    )

def parse_object(data: Dict) -> Object:
    attributes = [parse_attribute(attr) for attr in data['attributes']]
    return Object(attributes)

def parse_schema(data: Dict) -> Schema:
    objects = [parse_object(obj) for obj in data['objects']]
    return Schema(schema_name=data['name'], objects=objects)

def parse_parameter(data: Dict) -> Parameter:
    return Parameter(
        name=data['name'],
        location=data['location'],
        schema=data['schema_info'],
        sample=data['sample']
    )

def parse_request_body(data: Dict) -> RequestBody:
    schema = parse_schema(data['schema_info'])
    sample=parse_schema(data['sample'])
    return RequestBody(schema=schema, sample=sample)

def parse_http_request(data: Dict,base_url:str) -> HTTPRequest:
    if data.get('parameters')!=[]:
        parameters = [parse_parameter(param) for param in data.get('parameters', [])]
    else:
        parameters = []
    request_body = parse_request_body(data['request_body']) if 'request_body' in data else None
    return HTTPRequest(
        url=base_url,
        content_type=data['content_type'],
        method=data['method'],
        parameters=parameters,
        request_body=request_body
    )

def convert_attribute_value(value):

    if isinstance(value, dict):
        return parse_object(value)
    elif isinstance(value, list):
        return [convert_attribute_value(item) for item in value]
    else:
        return value

def convert_attribute_type(type):
    if isinstance(type, dict):
        return parse_schema(type)
    elif isinstance(type, list):
        return [convert_attribute_type(item) for item in type]
    else:
        return type