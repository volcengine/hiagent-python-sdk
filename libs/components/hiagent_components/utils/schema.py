# Copyright (c) 2024 Bytedance Ltd. and/or its affiliates
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from typing import Any

from hiagent_api.workflow_types import FieldDefinition


def _convert_field_definition(field: FieldDefinition) -> dict[str, Any]:
    """convert hiagent field definition to json schema
    Return:
        dict: json schema of field
    """

    # match case syntax need python 3.10
    match field.type:
        case 0:  # str
            return {
                "type": "string",
                "description": field.desc or "",
            }
        case 1:  # int
            return {
                "type": "integer",
                "description": field.desc or "",
            }
        case 2:  # bool
            return {
                "type": "boolean",
                "description": field.desc or "",
            }
        case 3:  # number
            return {
                "type": "number",
                "description": field.desc or "",
            }
        case 4:  # object
            schema: dict[str, Any] = {
                "type": "object",
                "description": field.desc or "",
                "properties": {},
            }

            if field.sub_parameters:
                schema = convert_hiagent_schema_to_json_schema(field.sub_parameters)
                schema["description"] = field.desc or ""

            return schema

        case 5:  # array_of_string
            schema = {
                "type": "array",
                "description": field.desc or "",
                "items": {
                    "type": "string",
                },
            }

            return schema
        case 6:  # array_of_integer
            schema = {
                "type": "array",
                "description": field.desc or "",
                "items": {
                    "type": "integer",
                },
            }

            return schema
        case 7:  # array_of_bool
            schema = {
                "type": "array",
                "description": field.desc or "",
                "items": {
                    "type": "boolean",
                },
            }

            return schema
        case 8:  # array_of_number
            schema = {
                "type": "array",
                "description": field.desc or "",
                "items": {
                    "type": "number",
                },
            }

            return schema
        case 9:  # array_of_object
            schema = {
                "type": "array",
                "description": field.desc,
                "items": {
                    "type": "object",
                    "properties": {},
                },
            }

            if field.sub_parameters:
                schema["items"] = convert_hiagent_schema_to_json_schema(
                    field.sub_parameters
                )

            return schema
        case 10:  # file
            schema = {
                "type": "object",
                "description": field.desc or "",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "文件名",
                    },
                    "url": {
                        "type": "string",
                        "description": "文件 url",
                    },
                },
                "required": ["name", "url"],
            }

            return schema
        case 11:  # array_of_file
            schema = {
                "type": "array",
                "description": field.desc or "",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "文件名",
                        },
                        "url": {
                            "type": "string",
                            "description": "文件 url",
                        },
                    },
                    "required": ["name", "url"],
                },
            }

            return schema
        case -1:
            return {
                "type": "any",
                "description": field.desc or "",
            }
        case _:
            raise ValueError(f"unknown field type {field.type}")


def convert_hiagent_schema_to_json_schema(
    hiagent_schema: list[FieldDefinition],
) -> dict[str, Any]:
    """convert hiagent schema to json schema"""
    json_schema: dict[str, Any] = {
        "type": "object",
        "properties": {},
        "required": [],
    }
    for field in hiagent_schema:
        json_schema["properties"][field.name] = _convert_field_definition(field)
        if field.required:
            json_schema["required"].append(field.name)
    return json_schema
