from typing import Dict

from FuzzCore.Taxonomy import HTTPRequest, Object
from FuzzCore.controllers.openAPIController import SchemaModel, ObjectModel, HTTPRequestModel, ParameterModel, \
    RequestBodyModel, AttributeModel


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
