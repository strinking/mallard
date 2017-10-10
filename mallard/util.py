#
# util.py
#
# mallard - DDG Instant Answers bot for the Programming Server
# Copyright (c) 2017 Ammon Smith et al.
#
# mallard is available free of charge under the terms of the MIT
# License. You are free to redistribute and/or modify it under those
# terms. It is distributed in the hopes that it will be useful, but
# WITHOUT ANY WARRANTY. See the LICENSE file for more details.
#

def plural(n) -> str:
    if n == 1:
        return ''
    else:
        return 's'
