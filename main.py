# bot.py
import os
import random
from dotenv import load_dotenv

from discord.ext import commands
from discord import DMChannel, Embed

from talkingstick import TalkingStick
from music import Music

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
PREFIX = os.getenv('PREFIX')
OWNER_ID = os.getenv('OWNER_ID')
PID = os.getpid()

bot = commands.Bot(command_prefix=PREFIX)

@bot.event
async def on_ready():
    print(f'{bot.user.name} has successfully connected to Discord.')
    print(f'\tCurrently connected to {len(bot.guilds)} servers.')


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if isinstance(message.channel, DMChannel):
        if True:  # If user is in registration process
            response = 'Thanks for registering! This doesn\'t actually work yet idiot, but at least you tried.'
            await message.channel.send(response)

    await bot.process_commands(message)


@bot.command(name='hi', help='Greets the user')
async def hi(ctx):
    response = f'How\'s it going, <@{ctx.author.id}>?'
    await ctx.send(response)


@bot.command(name='update')
async def update(ctx):
    if int(ctx.author.id) == int(OWNER_ID):
        # TODO: Implement this (https://stackoverflow.com/questions/1750757/restarting-a-self-updating-python-script)
        pass
    else:
        await ctx.send('Invalid permissions')


if __name__ == "__main__":
    bot.add_cog(TalkingStick(bot, OWNER_ID))
    bot.add_cog(Music(bot))

    bot.run(TOKEN)