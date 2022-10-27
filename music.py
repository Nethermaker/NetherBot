import discord
from discord import Embed, VoiceClient
from discord.ext import commands, tasks

from yt_dlp import YoutubeDL, utils

import asyncio

## Note: A lot of this code has been taken from https://github.com/Rapptz/discord.py/blob/v2.0.1/examples/basic_voice.py

# Init yt-dlp
utils.bug_reports_message = lambda: ''
ytdl_format_options = {
    'format': 'bestaudio/best',
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
  def __init__(self, source, *, data, volume=0.5):
    super().__init__(source, volume)

    self.data = data

    self.title = data.get('title')
    self.url = data.get('url')
    self.duration_string = data.get('duration_string')
    self.duration = data.get('duration')

  @classmethod
  async def from_url(cls, url, *, loop=None, stream=False):
    loop = loop or asyncio.get_event_loop()
    data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

    if 'entries' in data:
      # take first item from a playlist
      data = data['entries'][0]

    filename = data['url'] if stream else ytdl.prepare_filename(data)
    return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)


class MusicQueue():
  update_rate = 1

  def __init__(self, bot: commands.Bot, vc: VoiceClient, ctx: commands.Context):
    self.bot = bot
    self.vc = vc
    self.ctx = ctx
    self.queue: list[YTDLSource] = list()
  
  async def add_url(self, url: str):
    player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
    self.queue.append(player)
  
  def pop(self):
    if len(self.queue) == 0:
      return None
    
    return self.queue.pop(0)
  
  async def print_queue(self):
    pass


class Music(commands.Cog):

  def __init__(self, bot: commands.Bot):
    self.bot = bot

    self.clients: dict[VoiceClient, MusicQueue] = {}

    self.update.start()
  
  def cog_unload(self):
    self.update.cancel()
  
  @tasks.loop(seconds=5.0)
  async def update(self):
    print("Running update loop")
    for vc in list(self.clients.keys()):
      if not vc.is_playing():
        queue = self.clients[vc]
        next_song = queue.pop()
        if next_song is None:
          await vc.disconnect()
          self.clients.pop(vc)
        else:
          vc.play(next_song, after=lambda e: print(f'Player error: {e}') if e else None)
          await queue.ctx.send(f'Now playing: {next_song.title} ({next_song.duration_string})')
    
    await asyncio.sleep(1)
  
  @commands.command(name="play", help="Play a YouTube video")
  async def play(self, ctx: commands.Context, url: str):

    if ctx.voice_client in self.clients:
      queue = self.clients[ctx.voice_client]
      async with ctx.typing():
        await queue.add_url(url)
        await ctx.send(f"Added to queue: {queue.queue[0].title} ({queue.queue[0].duration_string})")
        return
    
    async with ctx.typing():
      player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
      ctx.voice_client.play(player, after=lambda e: print(f'Player error: {e}') if e else None)
      self.clients[ctx.voice_client] = MusicQueue(self.bot, ctx.voice_client, ctx)
    
    await ctx.send(f'Now playing: {player.title} ({player.duration_string})')

  @commands.command(name="skip", help="Skips the current video")
  async def skip(self, ctx: commands.Context):
    if ctx.voice_client.is_playing():
      ctx.voice_client.stop()
  
  @commands.command(name="queue", help="Show the video queue")
  async def queue(self, ctx: commands.Context):
    pass

  @play.before_invoke
  async def ensure_voice(self, ctx: commands.Context):
    if ctx.voice_client is None:
      if ctx.author.voice:
        await ctx.author.voice.channel.connect()
      else:
        await ctx.send("You must be in a voice channel to use this command!")
        raise commands.CommandError("Author not connected to a voice channel.")
  