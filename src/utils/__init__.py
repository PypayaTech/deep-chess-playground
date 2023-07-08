import argparse
import json
import os

PROJECT_REAL_PATH = os.path.dirname(os.path.realpath(__file__))[0:-6]

DATA_REAL_PATH = os.path.join(PROJECT_REAL_PATH, "data")


def parse_configuration_file(description):
    argparser = argparse.ArgumentParser(description=description)
    argparser.add_argument("-c", "--conf", help="Path to the configuration file.")
    args = argparser.parse_args()
    return args


def read_json(config_path):
    with open(config_path) as config_buffer:
        config = json.loads(config_buffer.read())
    return config
