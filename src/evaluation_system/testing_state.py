"""Module for testing state configuration acquisition"""
import json
from utility.json_validation import validate_json_file_file
from utility import data_folder

TESTING_CONFIG_PATH_RELATIVE = "evaluation_system/configs/testing_config.json"
TESTING_CONFIG_SCHEMA_PATH_RELATIVE = "evaluation_system/configs/testing_config_schema.json"
TESTING_VALIDITY = \
    validate_json_file_file(TESTING_CONFIG_PATH_RELATIVE, TESTING_CONFIG_SCHEMA_PATH_RELATIVE)

testing_conf_location = f'{data_folder}/{TESTING_CONFIG_PATH_RELATIVE}'

with open(testing_conf_location, "r", encoding="UTF-8") as jsonTestingFile:
    testing_config_content = json.load(jsonTestingFile)

TESTING = testing_config_content["testing"] == "True"

print(f'testing status : {TESTING}')
