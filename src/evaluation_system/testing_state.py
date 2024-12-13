from utility.json_validation import validate_json
from utility import data_folder
import json

testing_config_path_relative = f'{data_folder}/evaluation_system/configs/testing_config.json'
testing_config_schema_path_relative = f'{data_folder}/evaluation_system/configs/testing_config_schema.json'
with open(testing_config_path_relative, "r", encoding="UTF-8") as file:
    test_config = json.load(file)
with open(testing_config_schema_path_relative, "r", encoding="UTF-8") as file:
    test_config_schema = json.load(file)
TESTING = validate_json(test_config, test_config_schema)
print(f'testing status : {TESTING}')
