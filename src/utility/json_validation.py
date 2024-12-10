import json
import logging
import os

import jsonschema

import utility


def validate_json(json_data: dict, schema: dict) -> bool:
    """
    Validates a json object against a given json schema.
    :param json_data: json object
    :param schema: json schema
    :return: False if any error occurs, otherwise True
    see : https://python-jsonschema.readthedocs.io/en/latest/validate/
    """
    try:
        jsonschema.validate(instance=json_data, schema=schema)
    except jsonschema.exceptions.ValidationError as ex:
        logging.error(ex)
        return False
    return True
