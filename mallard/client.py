#
# client.py
#
# mallard - DDG Instant Answers bot for the Programming Server
# Copyright (c) 2017 Johannes Christ, Ammon Smith et al.
#
# mallard is available free of charge under the terms of the MIT
# License. You are free to redistribute and/or modify it under those
# terms. It is distributed in the hopes that it will be useful, but
# WITHOUT ANY WARRANTY. See the LICENSE file for more details.
#

from datetime import datetime
from random import randint
from typing import Optional
import logging
import re
import traceback

import discord
import duckduckgo

from . import __name__, __version__
from .url import try_follow_redirect
from .util import NO_GUILD, plural

logger = logging.getLogger("mallard")

PROGRAMMING_GUILD_ID = 181866934353133570
USER_MENTION_REGEX = re.compile(r"<@!?([0-9]+)>")
MAWARE_COLOR = discord.Color.from_rgb(0xFF, 0xB7, 0xC5)
MEGANE_URL = "https://media.discordapp.net/attachments/320121669563842560/351817511823605770/Megane1.png"
DISCORD_COLORS = {
    "default",
    "blue",
    "blurple",
    "dark_blue",
    "dark_gold",
    "dark_green",
    "dark_grey",
    "dark_magenta",
    "dark_orange",
    "dark_purple",
    "dark_red",
    "dark_teal",
    "darker_grey",
    "gold",
    "green",
    "greyple",
    "light_grey",
    "lighter_grey",
    "magenta",
    "orange",
    "purple",
    "red",
    "teal",
}


def _get_color(color) -> discord.Color:
    if color is None:
        return discord.Color.default()
    elif isinstance(color, str):
        if color in DISCORD_COLORS:
            return getattr(discord.Color, color)()
        else:
            logger.error("Color not recognized: '%s'", color)
            return discord.Color.default()
    else:
        try:
            r = int(color["r"])
            g = int(color["g"])
            b = int(color["b"])
            return discord.Color.from_rgb(r, g, b)
        except (KeyError, ValueError) as _:
            logger.error("Bad RGB color in config")
            return discord.Color.default()


class Client(discord.Client):
    def __init__(self, config, ratelimit_handle):
        super().__init__()
        self.mentions = config["mentions"]
        self.color = _get_color(config.get("color", None))
        count = config["ratelimit"]["queries"]
        every = config["ratelimit"]["per_seconds"]
        self.rl = duckduckgo.Ratelimit(count, every)
        self.rl_handle = ratelimit_handle

    def __del__(self):
        self.rl_handle.close()

    async def on_ready(self):
        """
        The method that is invoked when the bot is
        ready to start accepting events.
        """

        if self.mentions:
            activity = discord.Game(name=self.mentions[0])
            await self.change_presence(activity=activity)

        guilds = len(self.guilds)
        channels = sum(1 for _ in self.get_all_channels())
        users = len(self.users)

        logger.info("Connected to:")
        logger.info(" - %d guild%s", guilds, plural(guilds))
        logger.info(" - %d channel%s", channels, plural(channels))
        logger.info(" - %d user%s", users, plural(users))
        logger.info("Ready! \U0001f986")

    def _clean(self, message) -> Optional[str]:
        if message.author == self.user:
            return None
        if not message.content:
            return None

        parts = message.content.split()
        mention = parts[0]
        query = " ".join(parts[1:])

        match = USER_MENTION_REGEX.match(mention)
        if match is not None:
            if int(match[1]) == self.user.id:
                return query

        if mention in self.mentions:
            return query

        return None

    async def on_message(self, message):
        logger.debug("Received message event for %d", message.id)

        query = self._clean(message)
        if not query:
            logger.debug("Not a query. Ignoring.")
            return

        if query in ("help", "info"):
            await self.bot_info(message.channel)
        elif query in ("megane", "maware"):
            await self.megane_easter_egg(message.channel)
        else:
            await self.search(query, message)

    async def search(self, query, message):
        logger.info(
            "Received DDG search from %s: '%s'", message.author.display_name, query
        )

        # pylint: disable=assigning-non-slot
        embed = discord.Embed(type="rich")
        embed.timestamp = datetime.now()
        embed.set_footer(
            text=f"Requested by {message.author.display_name}",
            icon_url=message.author.avatar_url,
        )

        try:
            guild = message.guild or NO_GUILD
            with self.rl.try_run(guild.id) as ok:
                if ok:
                    # Ok to send query
                    result = await duckduckgo.zci(query)
                else:
                    # This guild has hit the rate limit
                    user = f"{message.author.name}#{message.author.discriminator}"
                    logger.info("Rate limited! (guild: %s, user: %s)", guild.name, user)
                    self.rl_handle.write(f"{guild.id},{message.author.id}\n")
                    await message.add_reaction(self.clock_emoji())
                    return

        except duckduckgo.DuckDuckGoError:
            logger.warning("Query did not succeed", exc_info=True)

            embed.title = f"Query: `{query}`"
            embed.description = "No results."
            embed.color = discord.Color.red()
        except:
            logger.error("Error fetching DDG search results", exc_info=True)

            embed.title = "\U0001f986\U0001f4a2 Something went wrong!"
            embed.description = f"```py\n{traceback.format_exc()}\n```"
            embed.color = discord.Color.red()
        else:
            result = await try_follow_redirect(result, default=result)
            query = query.replace("`", "'")

            embed.title = f"Query: `{query}`"
            embed.description = result
            embed.color = self.color

        await message.channel.send(embed=embed)

    async def bot_info(self, channel):
        logger.info("Displaying bot info.")

        usage = (
            "To use me, just do an `@` mention or use one of the "
            "above, then tell me what you want to know about!"
        )

        embed = discord.Embed(type="rich", color=discord.Color.dark_purple())
        embed.title = self.user.display_name
        embed.description = "\n".join(
            (
                f"**{__name__} version {__version__}**",
                f"Created by members of the Programming Server.",
                "",
                "Enabled mentions for this server:",
                "\n".join(f"\\* `{mention}`" for mention in self.mentions),
                "",
                usage,
            )
        )
        embed.add_field(
            name="GitHub", value="https://github.com/strinking/mallard", inline=True
        )
        if getattr(channel.guild, "id", 0) != PROGRAMMING_GUILD_ID:
            embed.add_field(
                name="Discord Server",
                value="https://discord.gg/010z0Kw1A9ql5c1Qe",
                inline=True,
            )
        embed.set_thumbnail(url=self.user.avatar_url)
        await channel.send(embed=embed)

    async def megane_easter_egg(self, channel):
        logger.info("Displaying qt megane grilz.")

        embed = discord.Embed(type="rich", color=MAWARE_COLOR)
        embed.set_footer(text=":)")
        embed.set_image(url=MEGANE_URL)
        await channel.send(embed=embed)

    @staticmethod
    def clock_emoji():
        return chr(randint(0x1F550, 0x1F567))
