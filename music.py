import discord
from discord import Embed, VoiceClient
from discord.ext import commands, tasks

from yt_dlp import YoutubeDL, utils

import os

import asyncio

## Note: A lot of this code has been taken from https://github.com/Rapptz/discord.py/blob/v2.0.1/examples/basic_voice.py

# Init yt-dlp
utils.bug_reports_message = lambda: ''
ytdl_format_options = {
    'format': 'bestaudio/best',
    'noplaylist': True,
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0',  # bind to ipv4 since ipv6 addresses cause issues sometimes
}
ffmpeg_options = {
    'options': '-vn',
}
ytdl = YoutubeDL(ytdl_format_options)


class YTDLSource(discord.PCMVolumeTransformer):
  def __init__(self, source, *, data, filename, volume=0.5):
    super().__init__(source, volume)

    self.data = data

    self.filename = filename

    self.title = data.get('title')
    self.url = data.get('url')
    self.duration_string = data.get('duration_string')
    self.duration = data.get('duration')
    self.thumbnail = data.get('thumbnail')

  @classmethod
  async def from_url(cls, url, *, loop=None, stream=False):
    loop = loop or asyncio.get_event_loop()
    data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

    if 'entries' in data:
      # take first item from a playlist
      data = data['entries'][0]

    filename = data['url'] if stream else ytdl.prepare_filename(data)
    return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data, filename=filename)
  
  def after_play(self, e):
    # Report error if there was one
    print(f'Player error: {e}') if e else None

    try:
      os.remove(self.filename)
    except:
      print(f"Unable to remove file: {self.filename}")


class MusicQueue():
  update_rate = 1

  def __init__(self, bot: commands.Bot, vc: VoiceClient, ctx: commands.Context):
    self.bot = bot
    self.vc = vc
    self.ctx = ctx
    self.queue: list[YTDLSource] = list()

    self.currently_playing: YTDLSource = None
  
  async def add_url(self, url: str):
    player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=False)
    self.queue.append(player)
    return player
  
  def pop(self):
    if len(self.queue) == 0:
      return None
    
    self.currently_playing = self.queue.pop(0)
    return self.currently_playing
  
  def create_queue_embed(self):
    embed=discord.Embed(title="Currently Playing", description=f"{self.currently_playing.title} ({self.currently_playing.duration_string})", color=0xb853ee)
    embed.set_thumbnail(url=f"{self.currently_playing.thumbnail}")

    up_next_string = ""
    index = 1
    total_time_remaining = 0
    if len(self.queue) == 0:
      up_next_string = "No songs in queue."
    else:
      for source in self.queue:
        up_next_string += f"{index}. {source.title} ({source.duration_string})\n"
        total_time_remaining += source.duration
        index += 1
      embed.set_footer(text=f"Time left in queue: {int(total_time_remaining/60)}:{total_time_remaining%60}")

    embed.add_field(name="Up Next:", value=up_next_string, inline=True)
    return embed



class Music(commands.Cog):

  def __init__(self, bot: commands.Bot):
    self.bot = bot

    self.client_queues: dict[VoiceClient, MusicQueue] = {}

    self.update.start()
  
  async def cog_unload(self):
    await super().cog_unload()
    self.update.cancel()
  
  @tasks.loop(seconds=1.0)
  async def update(self):
    #print("Running update loop")
    for vc in list(self.client_queues.keys()):
      if not vc.is_playing(): # Only need to update if voice client is not currently playing something
        queue = self.client_queues[vc]
        player = queue.pop()
        async with queue.ctx.typing():
          if player is None: # Nothing left in the queue, disconnect the bot
            await queue.ctx.send("Queue has ended. Leaving voice channel.")
            await vc.disconnect()
            self.client_queues.pop(vc)
          else: # Play the next song
            vc.play(player, after=lambda e: player.after_play(e))
            await queue.ctx.send(f'Now playing: {player.title} ({player.duration_string})')
  
  @commands.command(name="play", help="Play a YouTube video")
  async def play(self, ctx: commands.Context, url: str):
    async with ctx.typing():
      queue = self.client_queues.get(ctx.voice_client, MusicQueue(self.bot, ctx.voice_client, ctx))
      player = await queue.add_url(url)
      if queue.currently_playing:
        await ctx.send(f'Added to queue: {player.title} ({player.duration_string})')
      else:
        player = queue.pop()
        ctx.voice_client.play(player, after=lambda e: player.after_play(e))
        await ctx.send(f'Now playing: {player.title} ({player.duration_string})')
        self.client_queues[ctx.voice_client] = queue

  @commands.command(name="skip", help="Skips the current video")
  async def skip(self, ctx: commands.Context):
    if ctx.voice_client.is_playing():
      await ctx.send("Skipping current song...")
      ctx.voice_client.stop()
  
  @commands.command(name="queue", help="Show the video queue")
  async def queue(self, ctx: commands.Context):
    async with ctx.typing():
      if ctx.voice_client in self.client_queues:
        embed = self.client_queues[ctx.voice_client].create_queue_embed()
        await ctx.send(content=None, embed=embed)
      else:
        await ctx.send("There is no music currently playing.")

  @commands.command(name="clear", help="Clears the video queue")
  async def clear(self, ctx: commands.Context):
    async with ctx.typing():
      if ctx.voice_client in self.client_queues:
        queue = self.client_queues[ctx.voice_client]
        num_songs = len(queue.queue)
        queue.queue = list()
        await ctx.send(f"Cleared {num_songs} song(s) from the queue.")
      else:
        await ctx.send("There is no music currently playing.")
  
  @commands.command(name="stop", help="Stops video playback")
  async def stop(self, ctx: commands.Context):
    async with ctx.typing():
      if ctx.voice_client in self.client_queues:
        self.client_queues.pop(ctx.voice_client)
        ctx.voice_client.stop()
        await ctx.voice_client.disconnect()
        await ctx.send("Video playback ended. Leaving voice channel.")
      else:
        await ctx.send("There is no music currently playing.")

  @play.before_invoke
  async def ensure_voice(self, ctx: commands.Context):
    if ctx.voice_client is None:
      if ctx.author.voice:
        await ctx.author.voice.channel.connect()
      else:
        async with ctx.typing():
          await ctx.send("You must be in a voice channel to use this command!")
          raise commands.CommandError("Author not connected to a voice channel.")
  