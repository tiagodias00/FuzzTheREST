from typing import List, Dict, Optional

class Attribute:
    def __init__(self, type, name: str, is_id: bool = False, value=None):
        self.type = type
        self.name = name
        self.value = value
        self.is_id = is_id


class Object:
    def __init__(self, attributes: List[Attribute]):
        self.attributes = attributes


class Schema:
    def __init__(self, schema_name: str, objects: List[Object]):
        self.name = schema_name
        self.objects = objects
class Parameter:
    def __init__(self, name: str, location: str, schema: Schema,sample):
        self.name = name
        self.in_ = location
        self.schema_info = schema
        self.sample = sample

class RequestBody:
    def __init__(self, schema: Schema,sample):
        self.schema_info = schema
        self.sample = sample

class HTTPRequest:
    def __init__(self, url: str,content_type:str, method: str,parameters:List[Parameter], request_body:RequestBody=None):
        self.url = url
        self.content_type = content_type
        self.method = method
        self.parameters = parameters
        self.request_body = request_body

class Format:
    pass


class taxonomy:
    def __init__(self, http_requests: dict,base_url, ids: Dict[str, List[str]]):
        self.httpRequests = http_requests
        self.base_url = base_url
        self.ids = ids
