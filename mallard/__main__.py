"""
The entry point for mallard.
This module enables you to start
mallard by using
    python3 -m mallard
from the parent directory.
"""

from typing import Optional

import aiohttp
import duckduckgo
import discord

from .util import CONFIG


bot = discord.Client()
reference_list = ["@ddg", "@duck"]


@bot.event
async def on_ready():
    """
    This coroutine is called by discord.py
    when the bot has finished logging in.
    """

    print("Logged in.")


def parse_int(s):
    try:
        return int(s)
    except ValueError:
        return None


def fix_links(response: str) -> str:
    """
    Fixes links in the message that end with a `)`
    by simply appending a `#`. This is a fix for
    Discord's somewhat broken Markdown formatting.

    Arguments:
        response : str
            The response from `duckduckgo.get_zci`.

    Returns:
        str:
            The original response with broken links
            fixed so they render correctly in Discord's
            Markdown and websites respond as expected.
    """

    def fix_link(word: str) -> str:
        if word.startswith("http") and word.endswith(")"):
            return word + "#"
        return word

    return ' '.join(map(fix_link, response.split()))


async def try_follow_redirect(text: str) -> Optional[str]:
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
    """

    async with aiohttp.ClientSession() as cs:
        try:
            async with cs.get(text) as response:
                return str(response.url)
        except ValueError:
            return None


@bot.event
async def on_message(msg):
    """
    This coroutine is called when a message
    is received. Basically, this checks if
    the bot was mentioned and if so, will
    query the DuckDuckGo API for the message
    content without any mentions.
    """

    content_list = msg.content.split()

    # The Message is an Embed or an Image
    if not content_list:
        return

    mention_id_string = ''.join(c for c in content_list[0] if c.isdigit())
    # The Bot was not mentioned or referenced
    if not(parse_int(mention_id_string) == bot.user.id or content_list[0] in reference_list):
        return

    query_string = ' '.join(content_list[1:])
    query_result = duckduckgo.get_zci(query_string)

    redirect_result = await try_follow_redirect(query_result)
    if redirect_result is not None:
        query_result = redirect_result

    await msg.channel.send(embed=discord.Embed(
        title=f"DuckDuckGo: {query_string!r}",
        description=fix_links(query_result),
        colour=discord.Colour.orange()
    ))

bot.run(CONFIG['discord_token'])
