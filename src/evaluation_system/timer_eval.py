"""
    Testing Module for EvaluationSystem
"""
import logging
import time
import sys
import json
import os
from math import ceil
import jsonschema
import requests


TARGET_IP = "http://127.0.0.1:8001"
SECOND_IP = "http://192.168.142.201:8001"

project_root = os.path.realpath(__file__ + "/../../..")
data_folder = os.path.join(project_root, "data")

TEST_SYMBOL = "->"

CORRECT = "attack"
MISTAKE = "normal"


def validate_json(json_data: dict, schema: dict) -> bool:
    """
        Quick json validation implementation
    :param json_data: dictionary of data
    :param schema: json schema to validate against
    :return:
    """
    try:
        jsonschema.validate(instance=json_data, schema=schema)
    except jsonschema.exceptions.ValidationError as ex:
        logging.error(ex)
        return False
    return True


def send_label(label_json):
    """
        Quick request->POST call
    :param label_json: json data
    :return:
    """
    response = requests.post(TARGET_IP, json=label_json, timeout=15)
    if not response.ok:
        logging.error("Failed to send label:\n%s", label_json)


def goodbye():
    """
        Goodbye function
    :return:
    """
    print("ciao")


def send_with_delay_and_overload(send_delay, overload_times, err_range, gen_step):
    for k in range(0, overload_times, 1):
        for i in range(0, err_range+2, 1):
            for j in range(0, gen_step):
                first = CORRECT
                second = MISTAKE if (j < i) else CORRECT
                label = {
                    "session_id": str(j),
                    "source": "expert",
                    "value": first
                }
                send_label(label)
                time.sleep(send_delay)
                label = {
                    "session_id": str(j),
                    "source": "classifier",
                    "value": second
                }
                send_label(label)
                time.sleep(send_delay)
            print(f'{TEST_SYMBOL} done iteration : {i} .')


if __name__ == "__main__":
    config_path = f'{data_folder}/evaluation_system/configs/eval_config.json'
    config_schema_path = f'{data_folder}/evaluation_system/schemas/eval_config_schema.json'
    with open(config_path, "r", encoding="UTF-8") as jsonFile:
        ev_config = json.load(jsonFile)
    with open(config_path, "r", encoding="UTF-8") as jsonFileSchema:
        ev_config_schema = json.load(jsonFileSchema)
    GOOD_CONF = validate_json(ev_config, ev_config_schema)
    if not GOOD_CONF:
        logging.error("bad evaluation schema")
        goodbye()

    min_labels_step = ev_config["min_labels_opinionated"]
    max_conflict = ev_config["max_conflicting_labels_threshold"]
    max_cons_conflict = ev_config["max_consecutive_conflicting_labels_threshold"]

    # delay expressed in seconds, precision is up to microseconds.
    # see: https://docs.python.org/3/library/time.html#time.sleep
    delay_list = [500000, 300000, 100000, 50000, 10000, 5000]

    #  create sender and receiver
    over_load_times = 2
    generation_step = max(min_labels_step, max_conflict, max_cons_conflict)
    error_range = max(max_conflict, max_cons_conflict, ceil(generation_step/2))

    data_recorder = []

    for dl_it in range(0, len(delay_list)):
        this_delay = delay_list[dl_it]
        val_list = []

        #  --- send all labels, the report will be saved in a filename
        send_with_delay_and_overload(this_delay, over_load_times, error_range, generation_step)

        #  --- now all labels have been received, wait a bit then open the file
        time.sleep(10)
        #  --- trg_filename = "timings.txt"
        trg_file_path = os.path.join(data_folder, "evaluation_system/timings.txt" )
        with open(trg_file_path, 'r') as timing_file:
            data_list = timing_file.read().split('\n')[:-1]
            int_data_list = [int(item) for item in data_list]
            int_diff_list = [j-i for i, j in zip(int_data_list[:-1], int_data_list[1:])]
            # --- print(int_diff_list)
            int_avg = sum(int_diff_list)/len(int_diff_list)
            # --- print(int_avg)
            data_recorder.append( (this_delay, int_avg) )
            timing_file.close()
            os.remove(trg_file_path)

        # after receiver has received, go to next delay iteration
        print(f'tested with delay : {this_delay}, found : {data_recorder}')
        time.sleep(3)

    print(f'{TEST_SYMBOL} end of test errors')

    goodbye()
    # eof
