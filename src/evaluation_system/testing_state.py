from utility.json_validation import validate_json_file_file
from utility import data_folder
import json

testing_config_path_relative = f'evaluation_system/configs/testing_config.json'
testing_config_schema_path_relative = f'evaluation_system/configs/testing_config_schema.json'
testing_validity = validate_json_file_file(testing_config_path_relative, testing_config_schema_path_relative)

testing_conf_location = f'{data_folder}/{testing_config_path_relative}'

with open(testing_conf_location, "r", encoding="UTF-8") as jsonTestingFile:
    testing_config_content = json.load(jsonTestingFile)

TESTING = True if testing_config_content["testing"] == "True" else False

print(f'testing status : {TESTING}')
