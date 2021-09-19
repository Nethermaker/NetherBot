from discord import Embed, VoiceChannel, FFmpegAudio
from discord.ext import commands

import youtube_dl


class MusicQueue():

  def __init__(self, bot: commands.Bot, vc: VoiceChannel):
    self.bot = bot
    self.vc = vc
  
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

    self.queues: dict[VoiceChannel, MusicQueue] = {}
  
  @commands.command(name="play", help="Play a YouTube video")
  async def play(self, ctx: commands.Context):
    pass

  @commands.command(name="skip", help="Skips the current video")
  async def skip(self, ctx: commands.Context):
    pass
  
  @commands.command(name="queue", help="Show the video queue")
  async def queue(self, ctx: commands.Context):
    pass
  