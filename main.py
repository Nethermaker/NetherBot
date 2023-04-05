# bot.py
import os
import random
from dotenv import load_dotenv

from nextcord.ext import commands
from nextcord import DMChannel, Embed, Message
from nextcord import Intents

from talkingstick import TalkingStick
from music import Music

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
PREFIX = os.getenv('PREFIX')
OWNER_ID = os.getenv('OWNER_ID')
YOUTUBE_API_TOKEN = os.getenv('YOUTUBE_API_TOKEN')
BAN_WORDS = os.getenv('BAN_WORDS').split(',')
PID = os.getpid()

intents = Intents.default()
intents.message_content = True
intents.presences = True
intents.members = True

bot = commands.Bot(command_prefix=commands.when_mentioned_or(PREFIX), intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user.name} has successfully connected to Discord.')
    print(f'\tCurrently connected to {len(bot.guilds)} servers.')

    bot.add_cog(TalkingStick(bot, OWNER_ID))
    bot.add_cog(Music(bot, YOUTUBE_API_TOKEN))


@bot.event
async def on_message(message: Message):
    if message.author == bot.user:
        return

    if isinstance(message.channel, DMChannel):
        # Message was sent as a DM to the bot
        pass

    await bot.process_commands(message)

    for banned_word in BAN_WORDS:
        if banned_word.lower() in message.content.lower():
            await message.delete()
            break


@bot.command(name='update')
async def update(ctx):
    if int(ctx.author.id) == int(OWNER_ID):
        # TODO: Implement this (https://stackoverflow.com/questions/1750757/restarting-a-self-updating-python-script)
        pass
    else:
        await ctx.send('Invalid permissions')


if __name__ == "__main__":
    bot.run(TOKEN)