#
# url.py
#
# mallard - DDG Instant Answers bot for the Programming Server
# Copyright (c) 2017 Ammon Smith et al.
#
# mallard is available free of charge under the terms of the MIT
# License. You are free to redistribute and/or modify it under those
# terms. It is distributed in the hopes that it will be useful, but
# WITHOUT ANY WARRANTY. See the LICENSE file for more details.
#

from typing import Optional

import aiohttp

async def try_follow_redirect(url: str, default: str = None) -> Optional[str]:
    """
    Attempts to open the given text as an URL.
    Since the DuckDuckGo API sometimes returns
    redirects instead of the actual links, for
    example for the query !aw systemd, it only
    returns an URL instead of anything else -
    for convenience, it's nicer to have the
    actual resulting URL instead of just an URL
    to the redirect.

    Returns:
        Optional[str]:
            `None` if the given text could not be opened,
            or the link that the given text redirects to,
            given that the text is a valid URL.

            If the user provided a value for the `default`
            argument, that is returned instead.
    """

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                return str(response.url)
        except ValueError:
            return default
