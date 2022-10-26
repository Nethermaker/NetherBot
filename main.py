# bot.py
import os
import random
from dotenv import load_dotenv

from discord.ext import commands
from discord import DMChannel, Embed
from discord import Intents

from talkingstick import TalkingStick
from music import Music

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
PREFIX = os.getenv('PREFIX')
OWNER_ID = os.getenv('OWNER_ID')
PID = os.getpid()

intents = Intents.default()
intents.message_content = True
intents.presences = True
intents.members = True

bot = commands.Bot(command_prefix=PREFIX, intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user.name} has successfully connected to Discord.')
    print(f'\tCurrently connected to {len(bot.guilds)} servers.')

    await bot.add_cog(TalkingStick(bot, OWNER_ID))
    await bot.add_cog(Music(bot))


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if isinstance(message.channel, DMChannel):
        # Message was sent as a DM to the bot
        pass

    await bot.process_commands(message)


@bot.command(name='update')
async def update(ctx):
    if int(ctx.author.id) == int(OWNER_ID):
        # TODO: Implement this (https://stackoverflow.com/questions/1750757/restarting-a-self-updating-python-script)
        pass
    else:
        await ctx.send('Invalid permissions')


if __name__ == "__main__":
    bot.run(TOKEN)