import argparse
import json
import os


# Get the path to the project root directory
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

# Define the path to the data directory
DATA_PATH = os.path.join(PROJECT_ROOT, "data")


def parse_configuration_file(description):
    argparser = argparse.ArgumentParser(description=description)
    argparser.add_argument("-c", "--conf", help="Path to the configuration file.")
    args = argparser.parse_args()
    return args


def read_json(config_path):
    with open(config_path) as config_buffer:
        config = json.loads(config_buffer.read())
    return config
