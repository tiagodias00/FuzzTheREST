from pydantic import BaseModel, HttpUrl, validator, field_validator
from typing import List, Dict, Optional, Any
from fastapi import APIRouter, HTTPException

from FuzzCore.Taxonomy import HTTPRequest, Object, Schema
from FuzzCore.services.mapper_service import convert_http_requests, convert_schema, convert_attribute_value
from FuzzCore.services.parser_service import parse_OpenApi_file


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


class Request(BaseModel):
    file_path: str


router = APIRouter()


@router.post('/openapi', response_model=TaxonomyModel)
async def get_openapi_spec(request: Request):
        data = parse_OpenApi_file(request.file_path)
        converted_requests = convert_http_requests(data['httpRequests'])
        data['httpRequests'] = converted_requests
        return TaxonomyModel(**data)




