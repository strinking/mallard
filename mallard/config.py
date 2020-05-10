#
# config.py
#
# mallard - DDG Instant Answers bot for the Programming Server
# Copyright (c) 2017 Johannes Christ, Ammon Smith et al.
#
# mallard is available free of charge under the terms of the MIT
# License. You are free to redistribute and/or modify it under those
# terms. It is distributed in the hopes that it will be useful, but
# WITHOUT ANY WARRANTY. See the LICENSE file for more details.
#

import yaml


def load_config(path):
    with open(path, "r") as fh:
        obj = yaml.safe_load(fh)

    # Required fields
    if not isinstance(obj["bot"]["token"], str):
        raise ValueError("Configuration file doesn't specify bot token")

    if "ratelimit" not in obj:
        raise ValueError("Configuration file doesn't specify ratelimit information")

    # Optional fields
    if not isinstance(obj.get("mentions", None), list):
        obj["mentions"] = []

    if "colour" in obj and "color" not in obj:
        obj["color"] = obj["colour"]

    return obj
