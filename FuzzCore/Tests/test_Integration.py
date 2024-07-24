import pytest
import requests
from fastapi import FastAPI
from fastapi.testclient import TestClient
from FuzzCore.main import app


@pytest.fixture(scope="module")
def test_client():
    client = TestClient(app)
    return client


def test_Valid_openapi_endpoint_Parsing(test_client):
    url = '/openapi'
    request_data = {
        "file_path": "C:\\Users\\franc\\Documents\\FuzzTheREST\\openapi.yaml",
        "ids_fields":{}
    }

    response = test_client.post(url, json=request_data)

    assert response.status_code == 200
    assert 'base_url' in response.json()
    assert 'httpRequests' in response.json()


def test_Invalid_openapi_endpoint_Parsing(test_client):
    url = '/openapi'
    request_data = {
        "file_path": "C:\\Users\\franc\\Documents\\FuzzTheREST\\openapi.yaml",
    }

    response = test_client.post(url, json=request_data)

    assert response.status_code == 422
    assert 'detail' in response.json()
