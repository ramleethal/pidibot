import discord
from discord.ext import commands
import asyncio
from gtts import gTTS
import random
import data.config as cfg
from dotenv import load_dotenv
import os
#from discord.ui import Button, View

load_dotenv()
token = os.getenv('TOKEN')
allowed_users = cfg.allowed_users
watched_users = cfg.watched_users
announcements = cfg.announcements
watched_channels = cfg.watched_channels

intents = discord.Intents().all()
client = commands.Bot(command_prefix='!', intents=intents)

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')
    # Start the keep-alive task
    #add to every funcion that connects to VC
    #client.loop.create_task(keep_alive())

async def keep_alive():
    try:
        while True:
            await client.change_presence(status=discord.Status.online)
            print('keep_alive 30')
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
    #client.loop.create_task(keep_alive())

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
    if member.id in watched_users:
        if before.channel != after.channel and after.channel is not None: 
            if after.channel.id in watched_channels:
                text = random.choice(announcements[0])
                tts = gTTS(text, lang='ru')
                tts.save("tts.mp3")
                voice = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio("tts.mp3"))
                voice.volume = 0.1
                if not member.guild.voice_client:
                    voice_client = await after.channel.connect()
                elif member.guild.voice_client.channel.id != after.channel.id:
                    await member.guild.voice_client.disconnect()
                    #if voice_client.is_playing():
                    #    voice_client.stop()
                    #await voice_client.disconnect()
                    voice_client = await after.channel.connect()
                else: 
                    voice_client = member.guild.voice_client
                #if voice_client.is_connected():
                voice_client.play(voice)
                while voice_client.is_playing():
                    await asyncio.sleep(0.1)
                voice_client.stop()
                #client.loop.create_task(keep_alive())
        elif before.channel.id == watched_channels[0]: 
            text = random.choice(announcements[1])
            tts = gTTS(text, lang='ru')
            tts.save("tts.mp3")
            voice = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio("tts.mp3"))
            voice.volume = 0.1
            if not member.guild.voice_client:
                voice_client = await before.channel.connect()
            elif member.guild.voice_client.channel.id != before.channel.id:
                await member.guild.voice_client.disconnect()
                voice_client = await before.channel.connect()
            else: 
                voice_client = member.guild.voice_client
            voice_client.play(voice)
            while voice_client.is_playing():
                await asyncio.sleep(0.1)
            voice_client.stop()
        #client.loop.create_task(keep_alive())

@client.command()
async def leave(ctx):
    """Leave the current voice channel."""
    if ctx.author.id not in allowed_users:
        return
    voice_client = ctx.voice_client
    if voice_client and voice_client.is_connected():
        await voice_client.disconnect()
    voice_client.stop()

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
            #voice_client = await ctx.voice_client.move_to(channel)
            await ctx.voice_client.disconnect()
            voice_client = await channel.connect()
        else:
            voice_client = await channel.connect()
    tts = gTTS(text=text, lang='ru')
    tts.save("tts.mp3")
    voice = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio("tts.mp3"))
    voice.volume = 0.5
    voice_client.play(voice)
    while voice_client.is_playing():
        await asyncio.sleep(1)
    voice_client.stop()

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
            #voice_client = await ctx.voice_client.move_to(channel)
            await ctx.voice_client.disconnect()
            voice_client = await channel.connect()
        else:
            voice_client = await channel.connect()
    #chatgpt request should be here
    tts = gTTS(text=text, lang='ru')
    tts.save("tts.mp3")
    source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio("tts.mp3"))
    source.volume = 0.5
    voice_client.play(source)
    while voice_client.is_playing():
        await asyncio.sleep(1)
    voice_client.stop()

@client.command()
async def test(ctx):

    async def button_callback(interaction):
        await interaction.response.edit_message(content='Button clicked!', view=None)

    button = Button(custom_id='button1', label='WOW button!', style=discord.ButtonStyle.green)
    button.callback = button_callback

    await ctx.send('Hello World!', view=View(button))

class Menu(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.value = None
    
    @discord.ui.button(label = 'Send Message', style = discord.ButtonStyle.grey)
    async def menu1(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.author.send('Button clicked')

@client.command()
async def menu(ctx):
    if ctx.author.id not in allowed_users:
        return
    view = Menu()
    await ctx.reply(view = view)

# Define a simple View that gives us a counter button
class Counter(discord.ui.View):

    # Define the actual button
    # When pressed, this increments the number displayed until it hits 5.
    # When it hits 5, the counter button is disabled and it turns green.
    # note: The name of the function does not matter to the library
    @discord.ui.button(label='0', style=discord.ButtonStyle.red)
    async def count(self, button: discord.ui.Button, interaction: discord.Interaction):
        number = int(button.label) if button.label else 0
        if number + 1 >= 5:
            button.style = discord.ButtonStyle.green
            button.disabled = True
        button.label = str(number + 1)

        # Make sure to update the message with our updated selves
        await interaction.response.edit_message(view=self)

@client.command()
async def counter(ctx: commands.Context):
    """Starts a counter for pressing."""
    await ctx.send('Press!', view=Counter())

client.run(token)