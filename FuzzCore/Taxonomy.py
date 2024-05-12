from typing import List, Dict, Optional


class Schema:
    def __init__(self, type: str, properties: Optional[Dict[str, 'Property']] = None):
        self.type = type
        self.properties = properties


class Property:
    def __init__(self, name: str, type: str, is_id: bool = False):
        self.name = name
        self.type = type
        self.is_id = is_id


class Parameter:
    def __init__(self, name: str, in_: str, description: str, required: bool, schema: Schema):
        self.name = name
        self.in_ = in_
        self.description = description
        self.required = required
        self.schema = schema


class RequestBody:
    def __init__(self, content: Schema):
        self.content = content


class Paths:
    def __init__(self, path: str, method: str, description: str, parameters: List[Parameter],
                 request_body: Optional[RequestBody]):
        self.path = path
        self.method = method
        self.description = description
        self.parameters = parameters
        self.request_body = request_body


class Component:
    def __init__(self, schemas: Dict[str, Schema] = None, bodies: Dict[str, RequestBody] = None):
        self.schemas = schemas
        self.requestBodies = bodies


class OpenAPIDocument:
    def __init__(self, name: str, BaseUrl, paths: Dict[str, Paths], components:Component = None,
                 ):
        self.name = name
        self.baseUrl = BaseUrl
        self.paths = paths
        self.components = components
