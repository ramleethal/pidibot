import discord
import asyncio
import random
import config as cfg
import os
import gspread
import pandas as pd
from discord.ext import commands
from discord.ext import tasks
from gtts import gTTS
from dotenv import load_dotenv
#from discord import app_commands
#from discord.ui import Button, View

load_dotenv()
token = os.getenv('TOKEN')
allowed_users = cfg.allowed_users
watched_users = cfg.watched_users
announcements = cfg.announcements
watched_channels = cfg.watched_channels

##TODO      create a class for bot to store configs and data
intents = discord.Intents().all()
client = commands.Bot(command_prefix='!', intents=intents)
gc = gspread.service_account(filename = 'pidibot-sheets.json')

#load staff data from gSheets
def GoogleSheet(key):
    doc_empl = gc.open_by_key(os.getenv(key))
    sh_empl = doc_empl.get_worksheet(0)
    df = pd.DataFrame(sh_empl.get_all_values())
    df = df.rename(columns=df.iloc[0])
    df = df.drop(df.index[0]).reset_index(drop=True)
    return df

ppl = GoogleSheet('EMPL_DOC_KEY')
scr = GoogleSheet('SCORES_DOC_KEY')


@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')
    # Start the keep-alive task
    #add to every funcion that connects to VC
    #client.loop.create_task(keep_alive())

#TODO       FIX KEPALIVE FUNC
###############################################################
async def keep_alive():
    try:
        while True:
            await client.change_presence(status=discord.Status.online)
            print('keep_alive 30')
            await asyncio.sleep(30)
    except:
        pass
###############################################################

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

#TODO   fix incorrect VC reconnects when moved to another channel
#       add notification when VTB staff enters server
###############################################################
@client.event
async def on_voice_state_update(member, before, after):
    #check if user from watchlist updated it's status
    #if member.id in watched_users:
    #user connected to another voice channel
    if before.channel != after.channel and after.channel is not None and after.channel.id in watched_channels: 
        #user connected to one of watched channels
        if member.id in watched_users:
            if after.channel.id == watched_channels[0]: user = client.get_user(allowed_users[0])
            elif after.channel.id ==watched_channels[1]: user = client.get_user(allowed_users[1])
            await user.send(random.choice[':):',':(:'])
            return
        if not member.guild.voice_client:
            voice_client = await after.channel.connect()
        elif member.guild.voice_client.channel != after.channel:
            await member.guild.voice_client.disconnect()
            voice_client = await after.channel.connect()
        else: 
            voice_client = member.guild.voice_client
        text = random.choice(announcements[1])
        await text_to_speech(voice_client, text, 'ru', 0.05)
        #client.loop.create_task(keep_alive())
    #watched user disconnected from one of watched channels
    elif after.channel != before.channel and before.channel is not None: 
        if before.channel.id == watched_channels[0]:
            if member.id in watched_users:
                if not member.guild.voice_client:
                    voice_client = await before.channel.connect()
                elif member.guild.voice_client.channel != before.channel:
                    await member.guild.voice_client.disconnect()
                    voice_client = await before.channel.connect()
                else: 
                    voice_client = member.guild.voice_client
                text = random.choice(announcements[2])
                await text_to_speech(voice_client, text, 'ru', 0.05)
                #client.loop.create_task(keep_alive())
###############################################################

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

###################################################################################################
#works
#loop function
@tasks.loop(count = 30) # repeat after every 10 seconds
async def myloop(ctx, ppl):
    text = ppl.loc[myloop.current_loop,[2,3,4]]
    await ctx.send(text)
    if myloop.current_loop == ppl.shape[0]:
        return


#loop-calling procedure
@client.command()
async def load_empl(ctx, *, id=1):
    if ctx.author.id not in allowed_users:
        return
    myloop.start(ctx, ppl)
    
###################################################################################################
#works
#Menu ui view with buttons
class Menu(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.value = None

    @discord.ui.button(label = '[1]', style = discord.ButtonStyle.grey)
    async def menu_1(self, interaction: discord.Interaction, button: discord.ui.Button):
        button.disabled = True
        await interaction.response.edit_message(view = self)
    @discord.ui.button(label = '[2]', style = discord.ButtonStyle.grey)
    async def menu_2(self, interaction: discord.Interaction, button: discord.ui.Button):
        button.disabled = True
        await interaction.response.edit_message(view = self)
    @discord.ui.button(label = '[3]', style = discord.ButtonStyle.grey)
    async def menu_3(self, interaction: discord.Interaction, button: discord.ui.Button):
        button.disabled = True
        await interaction.response.edit_message(view = self)
    @discord.ui.button(label = '[4]', style = discord.ButtonStyle.grey)
    async def menu_4(self, interaction: discord.Interaction, button: discord.ui.Button):
        button.disabled = True
        await interaction.response.edit_message(view = self)
    @discord.ui.button(label = '[5]', style = discord.ButtonStyle.grey)
    async def menu_5(self, interaction: discord.Interaction, button: discord.ui.Button):
        button.disabled = True
        await interaction.response.edit_message(view = self)
    @discord.ui.button(label = '[6]', style = discord.ButtonStyle.grey)
    async def menu_6(self, interaction: discord.Interaction, button: discord.ui.Button):
        button.disabled = True
        await interaction.response.edit_message(view = self)
    @discord.ui.button(label = '[7]', style = discord.ButtonStyle.grey)
    async def menu_7(self, interaction: discord.Interaction, button: discord.ui.Button):
        button.disabled = True
        await interaction.response.edit_message(view = self)
    @discord.ui.button(label = '[8]', style = discord.ButtonStyle.grey)
    async def menu_8(self, interaction: discord.Interaction, button: discord.ui.Button):
        button.disabled = True
        await interaction.response.edit_message(view = self)
    @discord.ui.button(label = '[9]', style = discord.ButtonStyle.grey)
    async def menu_9(self, interaction: discord.Interaction, button: discord.ui.Button):
        button.disabled = True
        await interaction.response.edit_message(view = self)
    @discord.ui.button(label = '[10]', style = discord.ButtonStyle.grey)
    async def menu_10(self, interaction: discord.Interaction, button: discord.ui.Button):
        button.disabled = True
        await interaction.response.edit_message(view = self)
    
    @discord.ui.button(label = 'Send Message', style = discord.ButtonStyle.grey)
    async def menu_send(self, interaction: discord.Interaction, button: discord.ui.Button):
        button.label = 'Message sent!'
        button.disabled = True
        await interaction.channel.send('This is the message text')
        await interaction.response.edit_message(view = self)

    @discord.ui.button(label = 'Throw a dice', style = discord.ButtonStyle.grey)
    async def menu_dice(self, interaction: discord.Interaction, button: discord.ui.Button):
        button.label = 'check the result'
        button.disabled = True
        await interaction.channel.send('Throw result: '+ str(random.randint(1, 6)))
        await interaction.response.edit_message(view = self)
    #@discord.ui.text_input()
    
#func that calls menu view
@client.command()
async def menu(ctx):
    if ctx.author.id not in allowed_users:
        return
    view = Menu()
    await ctx.reply(view = view)
###################################################################################################
#todo discord modals & slash commands + discord.app_commands
class Questionnaire(discord.ui.Modal, title='Questionnaire Response'):
    name = discord.ui.TextInput(label='Name')
    answer = discord.ui.TextInput(label='Answer', style=discord.TextStyle.paragraph)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message(f'Thanks for your response, {self.name}!', ephemeral=True)
@client.command()
async def testt(ctx):
    if ctx.author.id not in allowed_users:
        return
    modal = Questionnaire()
    await ctx.send_modal(modal = modal)

###################################################################################################
#works
#interactive button view
class Counter(discord.ui.View):
    @discord.ui.button(label='0', style=discord.ButtonStyle.red)
    async def count(self, interaction: discord.Interaction, button: discord.ui.Button):
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

###################################################################################################
#works
#first daily attempt with emoji reactions
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
        pass

###################################################################################################
client.run(token)

#NOT WORKING
###################################################################################################
#todo another discord.modal
class Feedback(discord.ui.Modal, title='Feedback'):
    # Our modal classes MUST subclass `discord.ui.Modal`,
    # but the title can be whatever you want.

    # This will be a short input, where the user can enter their name
    # It will also have a placeholder, as denoted by the `placeholder` kwarg.
    # By default, it is required and is a short-style input which is exactly
    # what we want.
    name = discord.ui.TextInput(
        label='Name',
        placeholder='Your name here...',
    )

    # This is a longer, paragraph style input, where user can submit feedback
    # Unlike the name, it is not required. If filled out, however, it will
    # only accept a maximum of 300 characters, as denoted by the
    # `max_length=300` kwarg.
    feedback = discord.ui.TextInput(
        label='What do you think of this new feature?',
        style=discord.TextStyle.long,
        placeholder='Type your feedback here...',
        required=False,
        max_length=300,
    )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message(f'Thanks for your feedback, {self.name.value}!', ephemeral=True)

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        await interaction.response.send_message('Oops! Something went wrong.', ephemeral=True)

        # Make sure we know what the error actually is
        traceback.print_exception(type(error), error, error.__traceback__)


@client.tree.command(guild=TEST_GUILD, description="Submit feedback")
async def feedback(interaction: discord.Interaction):
    # Send the modal with an instance of our `Feedback` class
    # Since modals require an interaction, they cannot be done as a response to a text command.
    # They can only be done as a response to either an application command or a button press.
    await interaction.response.send_modal(Feedback())


###################################################################################################
#some button attempt
@client.command()
async def test(ctx):
    async def button_callback(interaction):
        await interaction.response.edit_message(content='Button clicked!', view=None)
    button = discord.ui.button(custom_id='button1', label='WOW button!', style=discord.ButtonStyle.green)
    button.callback = button_callback
    await ctx.send('Hello World!', view=discord.ui.View(button))

