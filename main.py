# bot.py
import os
from dotenv import load_dotenv
import destiny

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


@bot.command(name='search', help='Search the Destiny 2 API for a user')
async def search(ctx, player: str):
    result = destiny.search_player(player)
    await ctx.send(result)


@bot.command(name='light', help='Find the max light level of a player')
async def light(ctx, player: str):
    result = destiny.max_light_level(player)
    await ctx.send(result)

bot.run(TOKEN)
