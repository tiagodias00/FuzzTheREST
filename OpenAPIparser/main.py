from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from OpenAPIparser.Parser import parse_OpenApi_file
from pydantic import BaseModel, HttpUrl
from typing import Dict, List, Optional


class Request(BaseModel):
    file_path: str


class FunctionDetail(BaseModel):
    path: str
    method: str
    content_type: Optional[str] = None
    input_parameters: List
    input_body: Dict

class OpenAPIData(BaseModel):
    functions: Dict[str, FunctionDetail]
    base_url: HttpUrl


app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post('/openapi', response_model=OpenAPIData)
async def get_openapi_spec(request: Request):
    return parse_OpenApi_file(request.file_path)


@app.get("/")
async def root():
    return {"message": "Helkjjuhyyyylo World"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
