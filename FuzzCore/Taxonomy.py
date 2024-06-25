from typing import List, Dict, Optional


class Attribute:
    def __init__(self, type, name: str, is_id: bool = False, value=None):
        if not name:
            raise ValueError("Attribute name must be provided.")
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
    def __init__(self, name: str, location: str, schema: Schema, sample):
        self.name = name
        self.in_ = location
        self.schema_info = schema
        self.sample = sample


class RequestBody:
    def __init__(self, schema: Schema, sample):
        self.schema_info = schema
        self.sample = sample

    def to_dict_request(self):
        result_dict = {}
        for example in self.sample.objects:
            for attribute in example.attributes:
                result_dict[attribute.name] = self.dict_attribute(attribute)
        return result_dict

    def dict_attribute(self, attribute):
        if hasattr(attribute, 'type') and isinstance(attribute.type, list):
            result_list = []
            for attr in attribute.type:
                if(not isinstance(attr, Schema)):
                    return attribute.value
                else:
                    for obj in attribute.value:
                        schema_dict = {}
                        for att in obj.attributes:
                            schema_dict[att.name] = self.dict_attribute(att)
                        result_list.append(schema_dict)
            return result_list
        elif hasattr(attribute, 'type') and isinstance(attribute.type, Schema):
            schema_dict = {}
            for obj in attribute.type.objects:
                for attr in obj.attributes:
                    schema_dict[attr.name] = self.dict_attribute(attr)
            return schema_dict
        else:
            if hasattr(attribute, 'value'):
                return attribute.value
            else:
                return attribute

class HTTPRequest:
    def __init__(self, url: str, content_type: str, method: str, parameters: List[Parameter],
                 request_body: RequestBody = None):
        self.url = url
        self.content_type = content_type
        self.method = method
        self.parameters = parameters
        self.request_body = request_body


class Format:
    pass
