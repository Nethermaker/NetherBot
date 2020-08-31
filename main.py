# bot.py
import os
import random
from dotenv import load_dotenv
import destiny
from netherbot_db import NetherbotDatabase, User

from discord.ext import commands
from discord import Member, DMChannel, Embed

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
PREFIX = os.getenv('PREFIX')
OWNER_ID = os.getenv('OWNER_ID')
PID = os.getpid()

bot = commands.Bot(command_prefix=PREFIX)

active_stick_channels = dict()


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


@bot.command(name='search', help='Search the Destiny 2 API for a user')
async def search(ctx, player: str):
    result = destiny.search_player(player)
    await ctx.send(result)


@bot.command(name='light', help='Find the max light level of a player')
async def light(ctx, player: str):
    result = destiny.max_light_level(player)
    await ctx.send(result)


@bot.command(name='register', help='Associate your discord user with a bungie.net profile')
async def register(ctx):
    netherbot_db = NetherbotDatabase()
    session = netherbot_db.create_session()
    user = session.query(User).filter(User.discord_id == ctx.author.id)
    if user.count() > 0:
        await ctx.send('User already registered.')
    else:
        await ctx.send('Beginning registration. Check your private messages for further info.')
        channel = await ctx.author.create_dm()
        await channel.send('Please follow this link and sign into your Bungie profile in order to link your discord and Bungie profiles:\n'
                           'https://www.bungie.net/en/oauth/authorize?client_id=32452&response_type=code&state=' + str(ctx.author.id))


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


@bot.command(name='stick')
async def stick(ctx):
    voice_channel = ctx.message.author.voice.channel
    members = voice_channel.members
    if voice_channel not in active_stick_channels and len(members) > 1:
        await ctx.message.delete()
        talking_stick = TalkingStick(voice_channel, ctx.message.channel, ctx.message.author)
        active_stick_channels[voice_channel] = talking_stick
        await talking_stick.update()
    elif len(members) <= 1:
        await ctx.channel.send('Cannot use talking stick on channel with less than 2 members')
    elif len(members) >= 10:
        await ctx.channel.send('Cannot use talking stick on channel with more than 9 members')
    elif str(ctx.author.id) == str(OWNER_ID):
        await ctx.message.delete()
        await active_stick_channels[voice_channel].end()


@bot.event
async def on_voice_state_update(member, before, after):
    if before.channel != after.channel:
        await TalkingStick.handle_channel_switch(member, before, after)
    if after.mute is False:
        for voice_channel in active_stick_channels:
            talking_stick = active_stick_channels[voice_channel]
            if member in talking_stick.members and member != talking_stick.holder:
                await member.edit(mute=True)
    elif after.mute is True:
        for voice_channel in active_stick_channels:
            talking_stick = active_stick_channels[voice_channel]
            if member in talking_stick.members and member == talking_stick.holder:
                await member.edit(mute=False)
    if after.channel is None:
        # Need to check user was in a talking stick channel
        await member.edit(mute=False)


@bot.event
async def on_reaction_add(reaction, user):
    for voice_channel in active_stick_channels:
        talking_stick = active_stick_channels[voice_channel]
        if reaction.message.id == talking_stick.msg.id and user.id == talking_stick.holder.id:
            await talking_stick.handle_reaction(reaction.emoji)


class TalkingStick:
    emoji_nums = ['0️⃣', '1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔄', '❌']

    def __init__(self, voice_channel, text_channel, holder):
        self.voice_channel = voice_channel
        self.text_channel = text_channel
        self.holder = holder
        self.members = self.voice_channel.members
        self.msg = None

    def create_embed(self):
        embed = Embed(title="The talking stick has spoken!", description=f"Channel: {self.voice_channel.name}\nStarted by: <@{self.holder.id}>")
        embed.set_thumbnail(
            url="https://cdn.discordapp.com/attachments/100242574907826176/748605002045456384/unknown.png")
        users = ''
        for i in range(len(self.members)):
            users += f'{self.emoji_nums[i + 1]}: {self.members[i].display_name} \n'
        embed.add_field(name="Channel Members", value=users, inline=True)
        embed.add_field(name="Stick Holder", value=f'<@{self.holder.id}>', inline=True)
        embed.set_footer(text="React to a number to pass the stick or ❌ to end the session.")
        return embed

    def pass_stick(self, num):
        pass

    async def update(self):
        if self.msg is None:
            self.msg = await self.text_channel.send(f'Activating talking stick for voice channel: {self.voice_channel.name}')
        await self.msg.clear_reactions()
        for member in self.members:
            await member.edit(mute=True)
        await self.holder.edit(mute=False)
        new_embed = self.create_embed()
        await self.msg.edit(content=None, embed=new_embed)
        for i in range(len(self.members)):
            await self.msg.add_reaction(self.emoji_nums[i + 1])
        await self.msg.add_reaction('🔄')
        await self.msg.add_reaction('❌')

    async def end(self):
        for member in self.members:
            await member.edit(mute=False)
        await self.msg.delete()
        active_stick_channels.pop(self.voice_channel)

    async def handle_reaction(self, emoji):
        if isinstance(emoji, str):
            if emoji[0] in '01234566789':
                self.holder = self.members[int(emoji[0]) - 1]
                await self.update()
            elif emoji == '🔄':
                self.holder = random.choice(self.members)
                await self.update()
            elif emoji == '❌':
                await self.end()

    @staticmethod
    async def handle_channel_switch(member, before, after):
        for voice_channel in active_stick_channels:
            talking_stick = active_stick_channels[voice_channel]
            if before.channel == talking_stick.voice_channel:
                talking_stick.members.remove(member)
                if member == talking_stick.holder:
                    talking_stick.holder = random.choice(talking_stick.members)
                await talking_stick.update()
            elif after.channel == talking_stick.voice_channel:
                talking_stick.members.append(member)
                await talking_stick.update()


bot.run(TOKEN)
