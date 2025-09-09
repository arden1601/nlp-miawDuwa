import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import logging
from logging.handlers import TimedRotatingFileHandler
from motor.motor_asyncio import AsyncIOMotorClient

# Load .env
load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

# --- Logging setup ---
if not os.path.exists("logs"):
    os.makedirs("logs")

log_handler = TimedRotatingFileHandler(
    "logs/bot.log", when="midnight", interval=1, backupCount=7, encoding="utf-8"
)
log_handler.suffix = "%Y-%m-%d"

# Setup logging
logging.basicConfig(
    handlers=[log_handler],
    level=logging.INFO, 
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Enable intents
intents = discord.Intents.default()
intents.message_content = True

# Bot setup
bot = commands.Bot(command_prefix='!', intents=intents)

# --- Define the data for your bot's responses ---
INFO = {
    'hours': "We are open from 9:00 AM to 6:00 PM, Monday to Saturday. We are closed on Sundays.",
    'vet': "Dr. Emily Roberts is our veterinarian on duty today! You can book an appointment through our website.",
    'address': "Our vet clinic is located at 123 Pet Lane, Animal City.",
    'products': "We sell a variety of pet food, toys, and grooming supplies for cats, dogs, birds, and fish.",
    'fallback': "I'm sorry, I didn't understand that. You can ask me about our hours, vet, address, or products!",
    'greeting': "Hello there! I'm the Pet Shop bot. How can I help you today?",
}

# --- Define the rules/keywords for each response ---
RULES = {
    'hours': ['hours', 'open', 'closed', 'time', 'when'],
    'vet': ['vet', 'veterinarian', 'doctor', 'on duty'],
    'address': ['address', 'location', 'where', 'find'],
    'products': ['products', 'food', 'toys', 'supplies', 'sell', 'buy'],
    'greeting': ['hello', 'hi', 'hey']
}

# --- Bot Events and Commands ---

# Add MongoDB connection
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
client = AsyncIOMotorClient(MONGO_URI)
db = client.vet_clinic

# Add doctor schedules
DOCTORS = {
    "Dr. Emily Roberts": "General Veterinarian",
    "Dr. John Smith": "Surgery Specialist",
    "Dr. Sarah Chen": "Pet Dentistry"
}
@bot.event
async def on_ready():
    """This event fires when the bot is connected to Discord and sets up the database."""
    try:
        # Test database connection
        await client.admin.command('ping')
        print("MongoDB connection successful!")

        # Create indexes for better query performance
        await db.appointments.create_index([("date", 1), ("doctor", 1)])
        await db.appointments.create_index([("user_id", 1)])

        # Initialize working hours in the database if they don't exist
        working_hours = {
            "monday": {"start": "09:00", "end": "18:00"},
            "tuesday": {"start": "09:00", "end": "18:00"},
            "wednesday": {"start": "09:00", "end": "18:00"},
            "thursday": {"start": "09:00", "end": "18:00"},
            "friday": {"start": "09:00", "end": "18:00"},
            "saturday": {"start": "09:00", "end": "18:00"},
            "sunday": {"start": "00:00", "end": "00:00"}  # Closed
        }
        
        await db.settings.update_one(
            {"type": "working_hours"},
            {"$setOnInsert": working_hours},
            upsert=True
        )

        # Initialize doctors in the database if they don't exist
        for doctor, specialty in DOCTORS.items():
            await db.doctors.update_one(
                {"name": doctor},
                {"$setOnInsert": {
                    "name": doctor,
                    "specialty": specialty,
                    "active": True
                }},
                upsert=True
            )

        print(f'{bot.user} has connected to Discord!')
        print('Database initialization completed!')

    except Exception as e:
        print(f"Error setting up database: {str(e)}")
        # You might want to exit the bot if database setup fails
        import sys
        sys.exit(1)

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    try:
        content = message.content.lower()
        logging.info(f"Message from {message.author}: {content}")

        # --- Rule-Based Logic ---
        for intents, keywords in RULES.items():
            if any(keyword in content for keyword in keywords):
                response = INFO[intents]
                await message.channel.send(response)
                logging.info(f"Responded with: {response}")
                return

        if any(keyword in content for keyword in ['hello', 'hi', 'hey']):
            response = "Hello there! I'm the Pet Shop bot. How can I help you today?"
            await message.channel.send(response)
            logging.info(f"Responded with: {response}")
        else:
            response = INFO['fallback']
            await message.channel.send(response)
            logging.info(f"Responded with: {response}")

        await bot.process_commands(message)

    except Exception as e:
        logging.error("Error handling message", exc_info=True)

@bot.event
async def on_command_error(ctx, error):
    """Tangkap error command"""
    logging.error(f"Command error in {ctx.command}: {error}", exc_info=True)
    await ctx.send("Oops! Something went wrong. Please try again later.")

# Run bot
bot.run(DISCORD_TOKEN)
