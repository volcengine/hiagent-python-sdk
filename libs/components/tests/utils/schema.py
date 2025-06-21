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
from hiagent_api.workflow_types import FieldDefinition

from hiagent_components.utils.schema import convert_hiagent_schema_to_json_schema


def test_convert_hiagent_schema_to_json_schema():
    # test convert hiagent schema to json schema
    cases = [
        {
            "name": "object contains all types field",
            "hiagent_schema": [
                FieldDefinition(
                    name="field1",
                    type=0,
                    desc="desc1",
                    required=True,
                ),
                FieldDefinition(
                    name="field2",
                    type=1,
                    desc="desc2",
                    required=True,
                ),
                FieldDefinition(
                    name="field3",
                    type=2,
                    desc="desc3",
                    required=True,
                ),
                FieldDefinition(
                    name="field4",
                    type=3,
                    desc="desc4",
                    required=True,
                ),
                FieldDefinition(
                    name="field5",
                    type=4,  # object
                    desc="desc5",
                    sub_parameters=[
                        FieldDefinition(
                            name="field5_sub_field_1",
                            type=0,
                            desc="desc",
                            required=True,
                        ),
                        FieldDefinition(
                            name="field5_sub_field_2",
                            type=0,
                            desc="desc",
                            required=False,
                        ),
                    ],
                    required=True,
                ),
                FieldDefinition(
                    name="field6",
                    type=5,
                    desc="desc6",
                    required=True,
                ),
                FieldDefinition(
                    name="field7",
                    type=6,
                    desc="desc7",
                    required=True,
                ),
                FieldDefinition(
                    name="field8",
                    type=7,
                    desc="desc8",
                    required=True,
                ),
                FieldDefinition(
                    name="field9",
                    type=8,
                    desc="desc9",
                    required=True,
                ),
                FieldDefinition(
                    name="field10",
                    type=9,  # array of object
                    desc="desc10",
                    sub_parameters=[
                        FieldDefinition(
                            name="field10_sub_field_1",
                            type=0,
                            desc="desc",
                            required=True,
                        ),
                        FieldDefinition(
                            name="field10_sub_field_2",
                            type=0,
                            desc="desc",
                            required=False,
                        ),
                    ],
                    required=True,
                ),
                FieldDefinition(
                    name="field11",
                    type=10,
                    desc="desc11",
                    required=True,
                ),
                FieldDefinition(
                    name="field12",
                    type=11,
                    desc="desc12",
                    required=True,
                ),
                FieldDefinition(
                    name="field13",
                    type=-1,
                    desc="desc13",
                    required=False,
                ),
            ],
            "expected_schema": {
                "type": "object",
                "properties": {
                    "field1": {
                        "type": "string",
                        "description": "desc1",
                    },
                    "field2": {
                        "type": "integer",
                        "description": "desc2",
                    },
                    "field3": {
                        "type": "boolean",
                        "description": "desc3",
                    },
                    "field4": {
                        "type": "number",
                        "description": "desc4",
                    },
                    "field5": {
                        "type": "object",
                        "description": "desc5",
                        "properties": {
                            "field5_sub_field_1": {
                                "type": "string",
                                "description": "desc",
                            },
                            "field5_sub_field_2": {
                                "type": "string",
                                "description": "desc",
                            },
                        },
                        "required": ["field5_sub_field_1"],
                    },
                    "field6": {
                        "type": "array",
                        "description": "desc6",
                        "items": {
                            "type": "string",
                        },
                    },
                    "field7": {
                        "type": "array",
                        "description": "desc7",
                        "items": {
                            "type": "integer",
                        },
                    },
                    "field8": {
                        "type": "array",
                        "description": "desc8",
                        "items": {
                            "type": "boolean",
                        },
                    },
                    "field9": {
                        "type": "array",
                        "description": "desc9",
                        "items": {
                            "type": "number",
                        },
                    },
                    "field10": {
                        "type": "array",
                        "description": "desc10",
                        "items": {
                            "type": "object",
                            "properties": {
                                "field10_sub_field_1": {
                                    "type": "string",
                                    "description": "desc",
                                },
                                "field10_sub_field_2": {
                                    "type": "string",
                                    "description": "desc",
                                },
                            },
                            "required": ["field10_sub_field_1"],
                        },
                    },
                    "field11": {
                        "type": "object",
                        "description": "desc11",
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
                    "field12": {
                        "type": "array",
                        "description": "desc12",
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
                    },
                    "field13": {
                        "type": "any",
                        "description": "desc13",
                    },
                },
                "required": [
                    "field1",
                    "field2",
                    "field3",
                    "field4",
                    "field5",
                    "field6",
                    "field7",
                    "field8",
                    "field9",
                    "field10",
                    "field11",
                    "field12",
                ],
            },
        }
    ]

    for case in cases:
        got = convert_hiagent_schema_to_json_schema(case["hiagent_schema"])
        expected = case["expected_schema"]
        assert got == expected
