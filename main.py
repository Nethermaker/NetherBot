# bot.py
import os
from dotenv import load_dotenv

from discord.ext import commands

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
PREFIX = os.getenv('PREFIX')

bot = commands.Bot(command_prefix=PREFIX)


@bot.event
async def on_ready():
    print(f'{bot.user.name} has successfully connected to Discord.')
    print(f'\tCurrently connected to {len(bot.guilds)} servers.')


@bot.command(name='hi', help='Greets the user')
async def hi(ctx):
    response = f'How\'s it going, <@{ctx.author.id}>?'
    await ctx.send(response)

bot.run(TOKEN)
