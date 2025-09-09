import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
load_dotenv()

token = os.getenv("DISCORD_TOKEN")
# Enable the required intents, including message_content
intents = discord.Intents.default()
intents.message_content = True

# Set the command prefix. We won't use it for our rule-based system, but it's good practice.
bot = commands.Bot(command_prefix='!', intents=intents)

# --- Define the data for your bot's responses ---
# You can easily change these without touching the code logic.
INFO = {
    'hours': "We are open from 9:00 AM to 6:00 PM, Monday to Saturday. We are closed on Sundays.",
    'vet': "Dr. Emily Roberts is our veterinarian on duty today! You can book an appointment through our website.",
    'address': "Our vet clinic is located at 123 Pet Lane, Animal City.",
    'products': "We sell a variety of pet food, toys, and grooming supplies for cats, dogs, birds, and fish.",
    'fallback': "I'm sorry, I didn't understand that. You can ask me about our hours, vet, address, or products!"
}

# --- Define the rules/keywords for each response ---
RULES = {
    'hours': ['hours', 'open', 'closed', 'time', 'when'],
    'vet': ['vet', 'veterinarian', 'doctor', 'on duty'],
    'address': ['address', 'location', 'where', 'find'],
    'products': ['products', 'food', 'toys', 'supplies', 'sell'],
    'greeting': ['hello', 'hi', 'hey']
}

# --- Bot Events and Commands ---

@bot.event
async def on_ready():
    """This event fires when the bot is connected to Discord."""
    print(f'{bot.user} has connected to Discord!')

@bot.event
async def on_message(message):
    """This event fires whenever a message is sent in a channel the bot can see."""
    
    # Ignore messages from the bot itself to prevent an infinite loop
    if message.author == bot.user:
        return

    # Convert the message content to lowercase to make keyword matching case-insensitive
    content = message.content.lower()

    # --- Rule-Based Logic ---
    # Loop through our defined rules and check for a match
    for intent, keywords in RULES.items():
        if any(keyword in content for keyword in keywords):
            await message.channel.send(INFO[intent])
            # Stop checking after the first match
            return

    # If no rule was matched, send the fallback message
    # You can add a greeting check here for a more refined response
    if any(keyword in content for keyword in ['hello', 'hi', 'hey']):
        await message.channel.send("Hello there! I'm the Pet Shop bot. How can I help you today?")
    else:
        await message.channel.send(INFO['fallback'])

    # This is important to allow other bot commands to be processed.
    # In a more complex bot, you'd want this line. For this simple case, it's optional.
    await bot.process_commands(message)

# Run the bot with your token
# Make sure to replace 'YOUR_BOT_TOKEN' with your actual token
bot.run(token)