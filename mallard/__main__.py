"""
The entry point for mallard.
This module enables you to start
mallard by using
    python3 -m mallard
from the parent directory.
"""

import html
import json

import duckduckpy
import discord

from .util import CONFIG


bot = discord.Client()


@bot.event
async def on_ready():
    """
    This coroutine is called by discord.py
    when the bot has finished logging in.
    """

    print("Logged in.")


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
    # The Bot was not mentioned
    if not mention_id_string or int(''.join(mention_id_string)) != bot.user.id:
        return

    query_string = ''.join(content_list[1:])
    resp = duckduckpy.query(query_string)

    if not resp.abstract_source or not resp.related_topics:
        await msg.channel.send(embed=discord.Embed(
            title="Sorry, no results.", colour=discord.Colour.orange()
        ))
    else:
        embed = discord.Embed(colour=discord.Colour.orange())
        embed.set_author(
            name=f"DuckDuckGo: {resp.heading}",
            url=f"https://duckduckgo.com/?q={html.escape(query_string)}"
        )
        for result in resp.related_topics:
            if hasattr(result, 'first_url'):
                url = result.first_url + '#' if result.first_url.endswith(')') else result.first_url
                embed.add_field(
                    name=url,
                    value=result.text
                )
        await msg.channel.send(embed=embed)

bot.run(CONFIG['discord_token'])
