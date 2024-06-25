import pytest

from FuzzCore.Taxonomy import Attribute, Object, Schema, Parameter, RequestBody, HTTPRequest

def test_object_initialization():
    attr1 = Attribute(type=int, name="id", is_id=True, value=1)
    attr2 = Attribute(type=str, name="name", value="Test")
    obj = Object(attributes=[attr1, attr2])
    assert len(obj.attributes) == 2
    assert obj.attributes[0].name == "id"
    assert obj.attributes[1].name == "name"

def test_schema_initialization():
    attr1 = Attribute(type=int, name="id", is_id=True, value=1)
    attr2 = Attribute(type=str, name="name", value="Test")
    obj = Object(attributes=[attr1, attr2])
    schema = Schema(schema_name="TestSchema", objects=[obj])
    assert schema.name == "TestSchema"
    assert len(schema.objects) == 1
    assert schema.objects[0].attributes[0].name == "id"

def test_parameter_initialization():
    schema = Schema(schema_name="TestSchema", objects=[])
    param = Parameter(name="param1", location="query", schema=schema, sample=None)
    assert param.name == "param1"
    assert param.in_ == "query"
    assert param.schema_info == schema
    assert param.sample is None

def test_request_body_initialization():
    attr = Attribute(type=str, name="name", value="Sample")
    obj = Object(attributes=[attr])
    schema = Schema(schema_name="TestSchema", objects=[obj])
    sample = Object(attributes=[Attribute(type=str, name="name", value="Sample")])
    request_body = RequestBody(schema=schema, sample=sample)
    assert request_body.schema_info == schema
    assert request_body.sample == sample
def Valid_attribute_initialization():
    attr = Attribute(type=int, name="id", is_id=True, value=123)
    assert attr.type == int
    assert attr.name == "id"
    assert attr.is_id
    assert attr.value == 123

def Ensure_Invalid_Throws_Error():
        with pytest.raises(ValueError):
            attr = Attribute('type', '')



def test_to_dict_request():
    attr = Attribute(type=str, name="name", value="Sample")
    obj = Object(attributes=[attr])
    schema = Schema(schema_name="TestSchema", objects=[obj])
    sample = Schema(schema_name="TestSample", objects=[obj])
    request_body = RequestBody(schema=schema, sample=sample)
    expected_dict = {"name": "Sample"}
    assert request_body.to_dict_request() == expected_dict

def test_http_request_initialization():
    schema = Schema(schema_name="TestSchema", objects=[])
    param = Parameter(name="param1", location="query", schema=schema, sample=None)
    request_body = RequestBody(schema=schema, sample=None)
    http_request = HTTPRequest(
        url="http://example.com",
        content_type="application/json",
        method="POST",
        parameters=[param],
        request_body=request_body
    )
    assert http_request.url == "http://example.com"
    assert http_request.content_type == "application/json"
    assert http_request.method == "POST"
    assert http_request.parameters == [param]
    assert http_request.request_body == request_body

if __name__ == "__main__":
    pytest.main()
