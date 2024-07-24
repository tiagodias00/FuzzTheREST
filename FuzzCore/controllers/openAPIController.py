from pydantic import BaseModel
from fastapi import APIRouter, HTTPException


from FuzzCore.services.mapper_service import convert_http_requests, TaxonomyModel
from FuzzCore.services.parser_service import parse_OpenApi_file




class Request(BaseModel):
    file_path: str
    ids_fields: dict


router = APIRouter()


@router.post('/openapi', response_model=TaxonomyModel)
async def get_openapi_spec(request: Request):
        data = parse_OpenApi_file(request.file_path, request.ids_fields)
        converted_requests = convert_http_requests(data['httpRequests'])
        data['httpRequests'] = converted_requests
        return TaxonomyModel(**data)




