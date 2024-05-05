from typing import Optional, List, Dict

from fastapi import APIRouter
from pydantic import BaseModel, HttpUrl

from FuzzCore.services.parser_service import parse_OpenApi_file

router = APIRouter()


class FunctionDetail(BaseModel):
    path: str
    method: str
    content_type: Optional[str] = None
    input_parameters: List
    input_body: Dict


class OpenAPIData(BaseModel):
    functions: Dict[str, FunctionDetail]
    base_url: HttpUrl
    ids: Dict[str, List[str]]


class Request(BaseModel):
    file_path: str


@router.post('/openapi', response_model=OpenAPIData)
async def get_openapi_spec(request: Request):
    return parse_OpenApi_file(request.file_path)
