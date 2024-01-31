
from multiprocessing.connection import Client, answer_challenge
import discord
import os
from discord.ext import commands
import random
from discord import app_commands
from discord import FFmpegPCMAudio, PCMVolumeTransformer
import ffmpeg
from discord.utils import get
from discord import FFmpegPCMAudio
from youtube_dl import YoutubeDL
from discord import opus
import asyncio
import yt_dlp as youtube_dl
import datetime
from bottoken import token
import urllib.parse, urllib.request, re

#cogs = [music]

url_prefix = 'http://www.youtube.com/watch?v='


OPUS_LIBS = ['libopus-0.x86.dll', 'libopus-0.x64.dll', 'libopus-0.dll', 'libopus.so.0', 'libopus.0.dylib']


def load_opus_lib(opus_libs=OPUS_LIBS):
    if opus.is_loaded():
        return True

    for opus_lib in opus_libs:
        try:
            opus.load_opus(opus_lib)
            return
        except OSError:
            pass

        raise RuntimeError('Could not load an opus lib. Tried %s' % (', '.join(opus_libs)))


intents = discord.Intents().all()
client = commands.Bot(command_prefix='!', intents=intents, description="HandiBot")
#tree = app_commands.CommandTree(client)



emoji = '\n{THUMBS UP SIGN}'


#Initial Setup

@client.event
async def on_ready():
    activity = discord.Activity(name="/help", type=discord.ActivityType.listening)
    await client.change_presence(status=discord.Status.online, activity=activity)
    print('Logged into HandiBot'.format(client))
    activity = discord.Activity(name='with Code', type=discord.ActivityType.listening)
    try:
        synced = await client.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(e)
async def on_connect():
    print('Connected to discord'.format(client))


#Random Commands

@client.command()
async def hellWorld(ctx):
    await ctx.send("Hello World, I Am HandiBot!")


@client.command()
async def ping(ctx):
     message = await ctx.send("pong! \n :thumbsup:")
     await message.add_reaction(emoji)

    

@client.command()
async def load(ctx, extension):
    client.load_extension(f'cogs.{extension}')
    ctx.send("Loaded in")

@client.command()
async def unload(ctx, extension):
    client.unload_extension(f'cogs.{extension}')
    ctx.send("Out Loaded")

for filename in os.listdir('./cogs'):
    if filename.startswith('.py'):
        client.load_extension(f'cogs.{filename[:-3]}')




#Music Commands


@client.command(pass_context=True)
async def join(ctx):
   if ctx.author.voice == None:
    await ctx.send("***You Are not in a voice channel!***")
   author = ctx.message.author
   voice_channel = ctx.author.voice.channel
   voice2 = await voice_channel.connect(self_deaf=True)

@client.command()
async def leave(ctx):
    await ctx.voice_client.disconnect()



@client.command()
async def playlink(ctx, url):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)

    if ctx.author.voice == None:
        await ctx.send("***You are not in a voice channel!***")

    if voice == None:
        author = ctx.message.author
        voice_channel = ctx.author.voice.channel
        voice = await voice_channel.connect(self_deaf=True)
    else:
        pass
    ctx.voice_client.stop() 
    FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
    YDL_OPTIONS = {'format':"m4a/bestaudio/best"}
    vc = ctx.voice_client

    with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
        info = ydl.extract_info(url, download=False)
        url2 = info['url']
        source = await discord.FFmpegOpusAudio.from_probe(url2, **FFMPEG_OPTIONS)
        vc.play(source)

    await ctx.send("Currently playing: " + url)
    

@client.command()
async def play(ctx, *, search):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)

    if ctx.author.voice == None:
        await ctx.send("***You are not in a voice channel!***")

    if voice == None:
        author = ctx.message.author
        voice_channel = ctx.author.voice.channel
        voice = await voice_channel.connect(self_deaf=True)
    else:
        pass

    query_string = urllib.parse.urlencode({
        'search_query': search
    })
    htm_content = urllib.request.urlopen(
        'http://www.youtube.com/results?' + query_string
    )
    search_results = re.findall(r'/watch\?v=(.{11})', htm_content.read().decode())
    print(search_results[0])
    url = url_prefix + search_results[0]

    



    ctx.voice_client.stop() 
    FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
    YDL_OPTIONS = {'format':"m4a/bestaudio/best"}
    vc = ctx.voice_client

    with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
        info = ydl.extract_info(url, download=False)
        url2 = info['url']
        source = await discord.FFmpegOpusAudio.from_probe(url2, **FFMPEG_OPTIONS)
        vc.play(source)

    
    await ctx.send("Currently playing: " + url)

@client.command()
async def pause(ctx):
    ctx.voice_client.pause()
    await ctx.send("***Paused!***")


@client.command()
async def resume(ctx):
    ctx.voice_client.resume()
    await ctx.send("***Resumed!***")

@client.command()
async def stop(ctx):
    ctx.voice_client.stop()
    await ctx.send("***Stopped!***")

@client.event
async def on_voice_state_update(member, before, after):
    voice_state = member.guild.voice_client
    if voice_state is None:
        return
   
    if len(voice_state.channel.members) == 1:
        await voice_state.disconnect()

#Moderation Commands

@client.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member:discord.Member, *, reason):
    if reason == None:
        reason = "***This user was banned by ***" + ctx.message.author.name
    await member.ban(reason=reason)
    await ctx.send("***Ban done!***")

@client.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member:discord.Member, *, reason):
    if reason == None:
        reason = "***This user was kicked by ***" + ctx.message.author.name
    await member.kick(reason=reason)
    await ctx.send("***Kick done!***")

@client.command()
@commands.has_permissions(mute_members=True)
async def mute(ctx, member:discord.Member, *, timelimit):
    if "s" in timelimit:
        gettime = timelimit.strip("s")
        newtime = datetime.timedelta(seconds=int(gettime))
        await member.edit(timed_out_until=discord.utils.utcnow() + newtime)
        await ctx.send("***Mute done!***")


#Slash Commands



@client.tree.command(name="help", description="Displays help for Handi")
async def help(interaction: discord.Interaction):
    lines = open('help.txt')
    await interaction.response.send_message(lines.read())
    lines.close()




client.run(token)
