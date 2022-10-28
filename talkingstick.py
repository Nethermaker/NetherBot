import random

from discord import Embed
from discord.ext import commands

class TalkingStickChannel:
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

    async def handle_reaction(self, emoji):
        if isinstance(emoji, str):
            if emoji[0] in '01234566789':
                self.holder = self.members[int(emoji[0]) - 1]
                await self.update()
            elif emoji == '🔄':
                self.holder = random.choice(self.members)
                await self.update()
            elif emoji == '❌':
                # await self.end()
                return True # Indicate ended
        return False


class TalkingStick(commands.Cog):
  
  def __init__(self, bot, owner_id):
    self.bot = bot
    self.owner_id = owner_id

    self.active_stick_channels = dict()

  @commands.command(name='stick')
  async def stick(self, ctx):
    voice_channel = ctx.message.author.voice.channel
    members = voice_channel.members
    if voice_channel not in self.active_stick_channels and len(members) > 1:
      await ctx.message.delete()
      talking_stick = TalkingStickChannel(voice_channel, ctx.message.channel, ctx.message.author)
      self.active_stick_channels[voice_channel] = talking_stick
      await talking_stick.update()
    elif len(members) <= 1:
      await ctx.channel.send('Cannot use talking stick on channel with less than 2 members')
    elif len(members) >= 10:
      await ctx.channel.send('Cannot use talking stick on channel with more than 9 members')
    elif str(ctx.author.id) == str(self.owner_id):
      await ctx.message.delete()
      await self.active_stick_channels[voice_channel].end()
      self.active_stick_channels.pop(voice_channel)
  
  @commands.Cog.listener()
  async def on_voice_state_update(self, member, before, after):
    if member.bot:
      return
    if before.channel != after.channel:
      await self._handle_channel_switch(member, before, after)
    if after.mute is False:
      for voice_channel in self.active_stick_channels:
        talking_stick = self.active_stick_channels[voice_channel]
        if member in talking_stick.members and member != talking_stick.holder:
          await member.edit(mute=True)
    elif after.mute is True:
      for voice_channel in self.active_stick_channels:
        talking_stick = self.active_stick_channels[voice_channel]
        if member in talking_stick.members and member == talking_stick.holder:
          await member.edit(mute=False)
    if after.channel is None:
      # Need to check user was in a talking stick channel
      await member.edit(mute=False)
  
  @commands.Cog.listener()
  async def on_reaction_add(self, reaction, user):
    for voice_channel in self.active_stick_channels:
      talking_stick = self.active_stick_channels[voice_channel]
      if reaction.message.id == talking_stick.msg.id and user.id == talking_stick.holder.id:
        should_end = await talking_stick.handle_reaction(reaction.emoji)
        if should_end:
          self.active_stick_channels.pop(voice_channel)
          await talking_stick.end()
          return
  
  async def _handle_channel_switch(self, member, before, after):
    for voice_channel in self.active_stick_channels:
      talking_stick = self.active_stick_channels[voice_channel]
      if before.channel == talking_stick.voice_channel:
        talking_stick.members.remove(member)
        if member == talking_stick.holder:
          talking_stick.holder = random.choice(talking_stick.members)
        await talking_stick.update()
      elif after.channel == talking_stick.voice_channel:
        talking_stick.members.append(member)
        await talking_stick.update()