import discord
from discord import Embed, VoiceClient
from discord.ext import commands

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

  @classmethod
  async def from_url(cls, url, *, loop=None, stream=False):
    loop = loop or asyncio.get_event_loop()
    data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

    if 'entries' in data:
      # take first item from a playlist
      data = data['entries'][0]

    filename = data['url'] if stream else ytdl.prepare_filename(data)
    return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)


class MusicClient():
  update_rate = 1

  def __init__(self, bot: commands.Bot, vc: VoiceClient):
    self.bot = bot
    self.vc = vc
    self.queue: list[str] = list()

    #self.loop = asyncio.get_event_loop()
    #self.loop.run_until_complete(self._update())
  
  # Update Loop
  async def _update(self):
    while True:
      if not self.vc.is_playing() and len(self.queue) == 0:
        await self.vc.disconnect()
        break
      
      await asyncio.sleep(1)
      
  async def add_to_queue(self, url: str):
    pass

  async def skip(self):
    pass
  
  async def print_queue(self):
    pass

  async def _download_video(self, url: str):
    pass


class Music(commands.Cog):

  def __init__(self, bot: commands.Bot):
    self.bot = bot

    self.clients: dict[VoiceClient, MusicClient] = {}
  
  @commands.command(name="play", help="Play a YouTube video")
  async def play(self, ctx: commands.Context, url: str):
    
    async with ctx.typing():
      player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
      ctx.voice_client.play(player, after=lambda e: print(f'Player error: {e}') if e else None)
    
    await ctx.send(f'Now playing: {player.title}')

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
        self.clients[ctx.voice_client] = MusicClient(self.bot, ctx.voice_client)
      else:
        await ctx.send("You must be in a voice channel to use this command!")
        raise commands.CommandError("Author not connected to a voice channel.")
    
    elif ctx.voice_client.is_playing():
      # TODO: Queue it up baby
      ctx.voice_client.stop()
  