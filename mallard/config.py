#
# config.py
#
# mallard - DDG Instant Answers bot for the Programming Server
# Copyright (c) 2017 Ammon Smith et al.
#
# mallard is available free of charge under the terms of the MIT
# License. You are free to redistribute and/or modify it under those
# terms. It is distributed in the hopes that it will be useful, but
# WITHOUT ANY WARRANTY. See the LICENSE file for more details.
#

import yaml

def load_config(path):
    with open(path, 'r') as fh:
        obj = yaml.safe_load(fh)

    # Required fields
    if not isinstance(obj['bot']['token'], str):
        return ValueError("Configuration file doesn't specify bot token")

    # Optional fields
    if not isinstance(obj.getattr('mentions', None), list):
        obj['mentions'] = []

    if hasattr(obj, 'colour') and not hasattr(obj, 'color'):
        obj['color'] = obj['colour']

    return obj
