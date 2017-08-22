"""
The entry point for mallard.
This module enables you to start
mallard by using
    python3 -m mallard
from the parent directory.
"""

from discord.ext import commands

from .util import CONFIG


bot = commands.Bot(
    command_prefix=commands.when_mentioned_or(CONFIG['prefix']),
    description=CONFIG['description']
)


@bot.event
async def on_ready():
    """
    This coroutine is called by discord.py
    when the bot has finished logging in.
    """

    print("Logged in.")


bot.run(CONFIG['discord_token'])
