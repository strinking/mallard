"""
The entry point for mallard.
This module enables you to start
mallard by using
    python3 -m mallard
from the parent directory.
"""


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
    await msg.channel.send(embed=discord.Embed(
        title=f"DuckDuckGo: {query_string!r}",
        description=query_result,
        colour=discord.Colour.orange()
    ))

bot.run(CONFIG['discord_token'])
