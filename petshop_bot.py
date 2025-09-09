import discord
from discord.ext import commands
from dotenv import load_dotenv
import os

load_dotenv()  # Load environment variables from .env file

token = os.getenv('DISCORD_TOKEN')

# Enable the required intents
intents = discord.Intents.default()
intents.message_content = True

# Set the command prefix (e.g., your bot responds to !hello)
bot = commands.Bot(command_prefix='!', intents=intents)

# Event for when the bot is ready
@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')

# Command to respond to a user message
@bot.command()
async def hello(ctx):
    await ctx.send(f'Hello, {ctx.author.name}!')

# Run the bot with your token
bot.run(token)