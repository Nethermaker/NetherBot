# bot.py
import os
from dotenv import load_dotenv
import destiny
from netherbot_db import NetherbotDatabase, User

from discord.ext import commands

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


@bot.command(name='register', help='Associate your discord user with a bungie.net profile')
async def register(ctx, profile_id: int):
    netherbot_db = NetherbotDatabase()
    session = netherbot_db.create_session()
    new_user = User(discord_id=ctx.author.id, bng_profile_id=str(profile_id))
    session.add(new_user)
    session.commit()
    await ctx.send('User successfully registered')


@bot.command(name='list', help='Lists all registered users')
async def list_users(ctx):
    netherbot_db = NetherbotDatabase()
    session = netherbot_db.create_session()
    user = session.query(User).filter(User.discord_id == ctx.author.id).one()
    result = user.bng_profile_id
    await ctx.send(result)


@bot.command(name='update')
async def update(ctx):
    if int(ctx.author.id) == int(OWNER_ID):
        await ctx.send('Beginning update...')
        os.system(f'python3 update.py {PID} {ctx.channel.id}')
    else:
        await ctx.send('Invalid permissions')


bot.run(TOKEN)
