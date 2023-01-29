import discord
from discord.ext import commands
import asyncio
from gtts import gTTS
import random
import data.config as cfg

token = cfg.token
allowed_users = cfg.allowed_users
announcements = cfg.announcements

intents = discord.Intents().all()
client = commands.Bot(command_prefix='!', intents=intents)

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')
    # Start the keep-alive task
    #add to every funcion that connects to VC
    client.loop.create_task(keep_alive())

async def keep_alive():
    try:
        while True:
            await client.change_presence(status=discord.Status.online)
            await asyncio.sleep(30)
    except:
        pass

@client.command()
async def join(ctx):
    if ctx.author.id not in allowed_users:
        return
    channel = ctx.author.voice.channel
    if ctx.voice_client is None:
        client.voice_client = await channel.connect()
    else:
        await ctx.voice_client.move_to(channel)

@client.command()
async def members(ctx):
    if ctx.author.id not in allowed_users:
        return
    channel = ctx.author.voice.channel
    members = channel.members
    for member in members:
        print(member.name)

@client.event
async def on_voice_state_update(member, before, after):
    if member.id in  allowed_users and before.channel != after.channel: 
        channel = after.channel
        if not channel:
            return
        text = random.choice(announcements[1])
        tts = gTTS(text, lang='ru')
        tts.save("tts.mp3")
        voice = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio("tts.mp3"))
        voice.volume = 0.5
        #channel = member.guild.get_channel(after.channel.id)
        #voice_client = await channel.connect()
        if not member.guild.voice_client:
            voice_client = await channel.connect()
        voice_client.play(voice)
        while voice_client.is_playing():
            await asyncio.sleep(1)
        await voice_client.disconnect()
        voice_client.stop()

@client.command()
async def leave(ctx):
    """Leave the current voice channel."""
    if ctx.author.id not in allowed_users:
        return
    voice_client = ctx.voice_client
    if voice_client and voice_client.is_connected():
        await voice_client.disconnect()

@client.command()
async def speak(ctx, *, text):
    if ctx.author.id not in allowed_users:
        return
    channel = ctx.author.voice.channel
    if channel is None:
        await ctx.send("You are not connected to a voice channel.")
        return
    else:
        if ctx.voice_client:
            await ctx.voice_client.move_to(channel)
        else:
            voice_client = await channel.connect()
    tts = gTTS(text=text, lang='ru')
    tts.save("tts.mp3")
    source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio("tts.mp3"))
    source.volume = 0.5
    ctx.voice_client.play(source)
    while ctx.voice_client.is_playing():
        await asyncio.sleep(1)
    ctx.voice_client.stop()

@client.command()
async def ask(ctx, *, text):
    if ctx.author.id not in allowed_users:
        return
    channel = ctx.author.voice.channel
    if channel is None:
        await ctx.send("You are not connected to a voice channel.")
        return
    else:
        if ctx.voice_client:
            await ctx.voice_client.move_to(channel)
        else:
            voice_client = await channel.connect()
    tts = gTTS(text=text, lang='ru')
    tts.save("tts.mp3")
    source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio("tts.mp3"))
    source.volume = 0.5
    ctx.voice_client.play(source)
    while ctx.voice_client.is_playing():
        await asyncio.sleep(1)
    ctx.voice_client.stop()

client.run(token)