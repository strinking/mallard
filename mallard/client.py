#
# client.py
#
# mallard - DDG Instant Answers bot for the Programming Server
# Copyright (c) 2017 Ammon Smith et al.
#
# mallard is available free of charge under the terms of the MIT
# License. You are free to redistribute and/or modify it under those
# terms. It is distributed in the hopes that it will be useful, but
# WITHOUT ANY WARRANTY. See the LICENSE file for more details.
#

from datetime import datetime
import logging
import re
import traceback

from typing import Optional
import discord
import duckduckgo

from .url import try_follow_redirect
from .util import plural

logger = logging.getLogger('mallard')

USER_MENTION_REGEX = re.compile(r'<@!?([0-9]+)>')
DISCORD_COLORS = {
    'default',
    'blue',
    'blurple',
    'dark_blue',
    'dark_gold',
    'dark_green',
    'dark_grey',
    'dark_magenta',
    'dark_orange',
    'dark_purple',
    'dark_red',
    'dark_teal',
    'darker_grey',
    'gold',
    'green',
    'greyple',
    'light_grey',
    'lighter_grey',
    'magenta',
    'orange',
    'purple',
    'red',
    'teal',
}

def _get_color(color) -> discord.Color:
    if color is None:
        return discord.Color.default()
    elif isinstance(color, str):
        if color in DISCORD_COLORS:
            return getattr(discord.Color, color)()
        else:
            logger.error(f"Color not recognized: '{color}'")
            return discord.Color.default()
    else:
        try:
            r = int(color['r'])
            g = int(color['g'])
            b = int(color['b'])
            return discord.Color.from_rgb(r, g, b)
        except (KeyError, ValueError) as _:
            logger.error(f"Bad RGB color in config")
            return discord.Color.default()

class Client(discord.Client):
    def __init__(self, config):
        discord.Client.__init__(self)
        self.mentions = config['mentions']
        self.color = _get_color(config.getattr('color', None))

    async def on_ready(self):
        """
        The method that is invoked when the bot is
        ready to start accepting events.
        """

        if self.mentions:
            game = discord.Game(name=self.mentions[0])
            await self.change_presence(game=game)

        guilds = len(self.guilds)
        channels = len(self.get_all_channels())
        users = len(self.users)

        logger.info("Connected to:")
        logger.info(f" {guilds} guild{plural(guilds)}")
        logger.info(f" {channels} channel{plural(channels)}")
        logger.info(f" {users} user{plural(users)}")
        logger.info("Ready! \U0001f986")

    def _clean(self, message) -> Optional[str]:
        if message.author == self.user:
            return None
        if not message.content:
            return None

        parts = message.content.split()
        mention = parts[0]
        query = ' '.join(parts[1:])

        match = USER_MENTION_REGEX.match(mention)
        if match is not None:
            if int(match[1]) == self.user.id:
                return query

        if mention in self.mentions:
            return query

        return None

    async def on_message(self, message):
        logger.debug(f"Received message event for {message.id}")

        query = self._clean(message)
        if query is None:
            logger.debug("Not a query. Ignoring.")
            return

        logger.info(f"Received DDG search: '{query}'")

        embed = discord.Embed(type='rich')
        embed.timestamp = datetime.now()
        embed.set_footer(
                text=f"Searched by {message.author.mention}",
                icon_url=message.author.avatar_url,
        )

        try:
            result = await duckduckgo.get_zci(query)
        except ValueError:
            logger.error("Error fetching DDG search results", exc_info=True)

            embed.title = "\U0001f986\U0001f4a2 Something went wrong!"
            embed.description = f"```py\n{traceback.format_exc()}\n```"
            embed.color = discord.Color.red()
        else:
            result = await try_follow_redirect(result, default=result)
            query = query.replace("`", "'")

            embed.title = f"DuckDuckGo: `{query}`"
            embed.description = result
            embed.color = self.color

        await message.channel.send(embed=embed)
