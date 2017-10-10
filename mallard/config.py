"""
Utility file for mallard.

Contains the configuration
along with other hopefully
helpful functions.
"""

import yaml

def open_config(path):
    with open(path, 'r') as fh:
        obj = yaml.safe_load(fh)

    if not hasattr(obj['discord-token']):
        return ValueError("Configuration file doesn't specify bot token")
