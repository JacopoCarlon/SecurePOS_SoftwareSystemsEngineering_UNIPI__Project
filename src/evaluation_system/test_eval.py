import logging
import requests
import time
import sys
import json
import os
from math import ceil
import jsonschema


target_ip = "http://123.0.0.1:8001"
second_ip = "http://192.168.142.201:8001"

project_root = os.path.realpath(__file__ + "/../../..")
data_folder = os.path.join(project_root, "data")

TEST_SYMBOL = "->"


def validate_json(json_data: dict, schema: dict) -> bool:
    try:
        jsonschema.validate(instance=json_data, schema=schema)
    except jsonschema.exceptions.ValidationError as ex:
        logging.error(ex)
        return False
    return True


def send_label(label_json):
    response = requests.post("http://127.0.0.1:8001/", json=label_json)
    if not response.ok:
        logging.error("Failed to send label:\n%s", label_json)


def goodbye():
    print(f'{TEST_SYMBOL}goodbye')
    sys.exit(0)


if __name__ == "__main__":
    config_path = f'{data_folder}/evaluation_system/configs/eval_config.json'
    config_schema_path = f'{data_folder}/evaluation_system/configs/eval_config_schema.json'
    with open(config_path, "r", encoding="UTF-8") as jsonFile:
        ev_config = json.load(jsonFile)
    with open(config_path, "r", encoding="UTF-8") as jsonFileSchema:
        ev_config_schema = json.load(jsonFileSchema)
    good_conf = validate_json(ev_config, ev_config_schema)
    if not good_conf:
        logging.error("bad evaluation schema")
        goodbye()

    min_labels_step = ev_config["min_labels_opinionated"]
    max_conflict = ev_config["max_conflicting_labels_threshold"]
    max_cons_conflict = ev_config["max_consecutive_conflicting_labels_threshold"]

    # delay expressed in seconds, precision is up to microseconds.
    # see: https://docs.python.org/3/library/time.html#time.sleep
    delay = 300/1000
    print_delay = 800/1000

    print(f'starting test, delay-per-packet : {delay} ; delay-per-batch : {print_delay} .')
    print(f'min_labels:{min_labels_step}; max_errors:{max_conflict}; max_cons_err:{max_cons_conflict} ')

    gen_step = max(min_labels_step, max_conflict, max_cons_conflict)
    err_range = max(max_conflict, max_cons_conflict, ceil(gen_step/2))

    correct = "attack"
    mistake = "normal"
    print(f'{TEST_SYMBOL} begin tests errors')
    # err_range+1 covers from 0 to max_errors errors, but we might want to cover some more ...
    for i in range(0, err_range+2, 1):
        for j in range(0, gen_step):
            first = correct
            second = mistake if (j < i) else correct
            label = {
                "session_id": str(j),
                "source": "expert",
                "value": first
            }
            send_label(label)
            time.sleep(delay)
            label = {
                "session_id": str(j),
                "source": "classifier",
                "value": second
            }
            send_label(label)
            time.sleep(delay)

        print(f'{TEST_SYMBOL} done iteration : {i} .')

    print(f'{TEST_SYMBOL} end of test errors')

    goodbye()
    # eof
