import discord
import asyncio
import random
import config as cfg
import os
from discord.ext import commands
from gtts import gTTS
from dotenv import load_dotenv
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

async def text_to_speech(voice_client, text, lang = 'ru', volume = 0.5):
    if voice_client.is_playing():
        voice_client.stop()
    tts = gTTS(text, lang = lang)
    tts.save("tts.mp3")
    voice = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio("tts.mp3"))
    voice.volume = volume
    voice_client.play(voice)
    while voice_client.is_playing():
        await asyncio.sleep(0.1)
    voice_client.stop()


@client.command()
async def join(ctx):
    #check if user in whitelist
    if ctx.author.id not in allowed_users:
        return
    #check if user is connected to a voice channel. exit if not
    try:
        channel = ctx.author.voice.channel
    except:
        await ctx.send("You are not connected to a voice channel.")
        return
    #check for active voice client in context
    if ctx.voice_client is None:
        #if none => connect to channel
        voice_client = await channel.connect()
    #if there is an active voice client => disconnect, connect to new channel
    else:
        #await ctx.voice_client.move_to(channel)
        await ctx.voice_client.disconnect()
        voice_client = await channel.connect()
    return voice_client
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
async def members(ctx):
    if ctx.author.id not in allowed_users:
        return
    channel = ctx.author.voice.channel
    members = channel.members
    for member in members:
        print(member.name)

@client.event
async def on_voice_state_update(member, before, after):
    #check if user from watchlist updated it's status
    if member.id in watched_users:
        #user connected to another voice channel
        if before.channel != after.channel and after.channel is not None: 
            #user connected to one of watched channels
            if after.channel.id in watched_channels:
                if not member.guild.voice_client:
                    voice_client = await after.channel.connect()
                elif member.guild.voice_client.channel != after.channel:
                    await member.guild.voice_client.disconnect()
                    voice_client = await after.channel.connect()
                else: 
                    voice_client = member.guild.voice_client
                text = random.choice(announcements[0])
                await text_to_speech(voice_client, text, 'ru', 0.1)
                #client.loop.create_task(keep_alive())
        #watched user disconnected from one of watched channels
        elif before.channel.id == watched_channels[0] and after.channel != before.channel: 
            if not member.guild.voice_client:
                voice_client = await before.channel.connect()
            elif member.guild.voice_client.channel != before.channel:
                await member.guild.voice_client.disconnect()
                voice_client = await before.channel.connect()
            else: 
                voice_client = member.guild.voice_client
            text = random.choice(announcements[1])
            await text_to_speech(voice_client, text, 'ru', 0.1)
            #client.loop.create_task(keep_alive())

@client.command()
async def speak(ctx, *, text):
    if ctx.author.id not in allowed_users:
        return
    voice_client = await join(ctx)
    await text_to_speech(voice_client, text, 'ru', 0.5)

@client.command()
async def ask(ctx, *, text):
    if ctx.author.id not in allowed_users:
        return
    voice_client = await join(ctx)
    #chatgpt request goes here
    await text_to_speech(voice_client, text, 'ru', 0.5)

###############################################################################
@client.command()
async def start_daily(ctx):
    await join(ctx)
    embed = discord.Embed(title="Планёрка", description="...")
    embed.add_field(name="TTS", value="This is a TTS message", inline=False)
    embed.set_footer(text="Click the button below to hear TTS text.")
    msg = await ctx.send(embed=embed)
    await msg.add_reaction("▶")
    await msg.add_reaction("⏭")
    await msg.add_reaction("🔁")

@client.event
async def on_reaction_add(reaction, user):
    if reaction.message.embeds and reaction.emoji == "▶" and user.id in allowed_users :
        channel = reaction.message.channel
        #reaction.count = 1
        await text_to_speech(user.guild.voice_client, 'test start', 'ru', 0.5)
        #await channel.send(content="start", tts=True)
    elif reaction.message.embeds and reaction.emoji == "⏭" and user.id in allowed_users :
        channel = reaction.message.channel
        #reaction.count = 1
        await text_to_speech(user.guild.voice_client, 'test next', 'ru', 0.5)
        #await channel.send(content="next", tts=True)
    elif reaction.message.embeds and reaction.emoji == "🔁" and user.id in allowed_users :
        channel = reaction.message.channel
        #reaction.count = 1
        await text_to_speech(user.guild.voice_client, 'test repeat', 'ru', 0.5)
        #await channel.send(content="repeat", tts=True)
    elif reaction.message.embeds and reaction.emoji in ['▶','⏭','🔁'] and user.id not in allowed_users :
        #reaction.count = 1
        pass;

###############################################################################
@client.command()
async def test(ctx):
    async def button_callback(interaction):
        await interaction.response.edit_message(content='Button clicked!', view=None)
    button = Button(custom_id='button1', label='WOW button!', style=discord.ButtonStyle.green)
    button.callback = button_callback
    await ctx.send('Hello World!', view=View(button))

###############################################################################
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

###############################################################################
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