from pydantic import BaseModel, HttpUrl,field_validator, Field, Extra
from typing import List, Dict, Optional, Any
from FuzzCore.Taxonomy import HTTPRequest, Object, Schema


class AttributeModel(BaseModel):
    type: Any
    name: str
    is_id: bool
    value: Optional[Any] = None

    @field_validator('type')
    def validate_type(cls, v):
        if isinstance(v, Schema):
            return convert_schema(v)
        elif isinstance(v, list) and all(isinstance(item, Schema) for item in v):
            return [convert_schema(item) for item in v]
        return v

    @field_validator('value')
    def handle_complex_values(cls, v):
        return convert_attribute_value(v)


class ObjectModel(BaseModel):
    attributes: List[AttributeModel]


class SchemaModel(BaseModel):
    name: str
    objects: List[ObjectModel]


class ParameterModel(BaseModel):
    name: str
    location: str
    schema_info: str
    sample: Any


class RequestBodyModel(BaseModel):
    schema_info: SchemaModel
    sample: SchemaModel


class HTTPRequestModel(BaseModel):
    content_type: Optional[str] = None
    method: str
    parameters: List[ParameterModel]
    request_body: Optional[RequestBodyModel] = None
    url: str


class TaxonomyModel(BaseModel):
    httpRequests: Dict[str, HTTPRequestModel]
    base_url: HttpUrl
    ids: Dict[str, List[str]]


class BasePayload(BaseModel):
    algorithm_type: str
    base_url: str
    function: Dict[str, HTTPRequestModel]
    ids: Dict
    scenarios: List
    additional_params: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        extra = Extra.allow


def convert_http_requests(http_requests: Dict[str, HTTPRequest]) -> Dict[str, HTTPRequestModel]:
    model_dict = {}
    for key, request in http_requests.items():
        parameters = [
            ParameterModel(
                name=p.name,
                location=p.in_,
                schema_info=p.schema_info,
                sample=p.sample
            ) for p in request.parameters if hasattr(p, 'name') and hasattr(p, 'in_')
        ]
        request_body = RequestBodyModel(
            schema_info=convert_schema(request.request_body.schema_info),
            sample=convert_schema(request.request_body.sample)
        ) if request.request_body else None

        model_dict[key] = HTTPRequestModel(
            url=request.url,
            content_type=request.content_type,
            method=request.method,
            parameters=parameters,
            request_body=request_body
        )

    return model_dict


def convert_schema(taxonomy_schema) -> SchemaModel:
    all_object_models = []
    for entry in taxonomy_schema.objects:
        if isinstance(entry, Object):
            object_list = [entry]
        else:
            object_list = entry

        for obj in object_list:
            object_model = ObjectModel(attributes=[
                AttributeModel(
                    type=attr.type,
                    name=attr.name,
                    is_id=attr.is_id,
                    value=attr.value
                ) for attr in obj.attributes
            ])
            all_object_models.append(object_model)

    return SchemaModel(
        name=taxonomy_schema.name,
        objects=all_object_models
    )


def convert_attribute_value(value):
    if isinstance(value, Object):
        return convert_object(value)
    elif isinstance(value, list):
        return [convert_attribute_value(item) for item in value]
    else:
        return value


def convert_object(taxonomy_object):
    return ObjectModel(attributes=[
        AttributeModel(
            type=attr.type,
            name=attr.name,
            is_id=attr.is_id,
            value=convert_attribute_value(attr.value)
        ) for attr in taxonomy_object.attributes
    ])
