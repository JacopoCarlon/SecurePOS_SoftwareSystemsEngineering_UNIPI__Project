from utility.json_validation import validate_json_file_file

testing_config_path_relative = f'evaluation_system/configs/testing_config.json'
testing_config_schema_path_relative = f'evaluation_system/configs/testing_config_schema.json'
TESTING = validate_json_file_file(testing_config_path_relative, testing_config_schema_path_relative)
print(f'testing status : {TESTING}')
