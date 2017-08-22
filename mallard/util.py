"""
Utility file for mallard.

Contains the configuration
along with other hopefully
helpful functions.
"""

import os
import json


PARENT_DIR = os.path.dirname(os.path.dirname(__file__))

with open(os.path.join(PARENT_DIR, "config.json"), 'r') as f:
    CONFIG = json.load(f)
