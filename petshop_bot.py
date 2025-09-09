import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timedelta
import pytz

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
    'address': "Our vet clinic is located at 123 Pet Lane, Animal City.",
    'products': "We sell a variety of pet food, toys, and grooming supplies for cats, dogs, birds, and fish.",
    'fallback': "I'm sorry, I didn't understand that. You can ask me about our hours, vet, address, or products!",
    'greeting': "Hello there! I'm the Vet Clinic bot. How can I help you today?"
}

# Add this near the top with other constants
TIMESLOTS = [
    "09:00", "10:00", "11:00", "12:00", "14:00", "15:00", "16:00", "17:00"
]

# --- Define the rules/keywords for each response ---
RULES = {
    'hours': ['hours', 'open', 'closed', 'time', 'when'],
    'vet': ['vet', 'veterinarian', 'doctor', 'on duty'],
    'address': ['address', 'location', 'where', 'find'],
    'products': ['products', 'food', 'toys', 'supplies', 'sell'],
    'greeting': ['hello', 'hi', 'hey'],
    'booking': ['book', 'appointment', 'schedule', 'booking'],
    'doctors': ['available', 'doctors', 'who']
}

# Add MongoDB connection
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
client = AsyncIOMotorClient(MONGO_URI)
db = client.vet_clinic

# Add doctor schedules
DOCTORS = {
    "Dr. Emily Roberts": "General Veterinarian",
    "Dr. John Smith": "Surgery Specialist",
    "Dr. Sarah Chen": "Pet Dentistry"
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
    """This event fires whenever a message is sent in a channel the bot can see."""
    if message.author == bot.user:
        return

    content = message.content.lower()

    # First, process commands
    await bot.process_commands(message)

    # Then process rule-based responses
    for intent, keywords in RULES.items():
        if any(keyword in content for keyword in keywords):
            if intent == 'booking':
                await message.channel.send(
                    "To book an appointment, use: !book <doctor name> <time> example: !book 'Dr. John Smith' '10:00'\n"
                    "To see available doctors, use: !doctors"
                )
            elif intent == 'doctors':
                await doctors(message.channel)
            else:
                await message.channel.send(INFO[intent])
            return

    # If no rule was matched, send the fallback message
    # In the on_message event, update the booking message
    if intent == 'booking':
        await message.channel.send(
            "To book an appointment, use: !book \"doctor name\" \"time\"\n"
            "To see available doctors and times, use: !doctors\n"
            "To check your appointments, use: !myappointments"
        )
    # You can add a greeting check here for a more refined response
    if any(keyword in content for keyword in ['hello', 'hi', 'hey']):
        await message.channel.send("Hello there! I'm the Vet Clinic bot. How can I help you today?")
    else:
        await message.channel.send(INFO['fallback'])

async def get_available_doctors(date):
    """Get available doctors and their free time slots for a specific date"""
    bookings = await db.appointments.find({"date": date}).to_list(None)
    booked_slots = {(b['doctor'], b['time']) for b in bookings}
    
    available_doctors = {}
    for doc, spec in DOCTORS.items():
        free_slots = []
        for time in TIMESLOTS:
            if (doc, time) not in booked_slots:
                free_slots.append(time)
        if free_slots:  # Only include doctors with available slots
            available_doctors[doc] = {"specialty": spec, "slots": free_slots}
    
    return available_doctors

async def create_booking(user_id, doctor, date, time):
    """Create a booking in MongoDB"""
    booking = {
        "user_id": user_id,
        "doctor": doctor,
        "date": date,
        "time": time,
        "created_at": datetime.utcnow()
    }
    await db.appointments.insert_one(booking)

@bot.command()
async def doctors(ctx):
    """Show available doctors and their time slots for today"""
    if ctx.author == bot.user:
        return

    today = datetime.now(pytz.UTC).strftime("%Y-%m-%d")
    available = await get_available_doctors(today)
    
    if available:
        response = "Available appointments today:\n"
        for doctor, info in available.items():
            response += f"\n{doctor} ({info['specialty']})\n"
            response += "Available times: " + ", ".join(info['slots']) + "\n"
    else:
        response = "No doctors available today. Please try another day."
    
    await ctx.send(response)

@bot.command()
async def book(ctx, doctor_name: str, time: str):
    """Book an appointment with a doctor at a specific time"""
    if ctx.author == bot.user:
        return

    today = datetime.now(pytz.UTC).strftime("%Y-%m-%d")
    
    if doctor_name not in DOCTORS:
        await ctx.send("Doctor not found. Please use !doctors to see available doctors.")
        return

    if time not in TIMESLOTS:
        await ctx.send(f"Invalid time slot. Available slots are: {', '.join(TIMESLOTS)}")
        return
        
    available = await get_available_doctors(today)
    if doctor_name not in available or time not in available[doctor_name]['slots']:
        await ctx.send(f"Sorry, {doctor_name} is not available at {time} today.")
        return
    
    try:
        await create_booking(ctx.author.id, doctor_name, today, time)
        await ctx.send(f"Appointment booked with {doctor_name} for today at {time}!")
    except Exception as e:
        await ctx.send("Sorry, there was an error booking your appointment.")

@bot.command()
async def myappointments(ctx):
    """Check your appointments"""
    if ctx.author == bot.user:
        return

    try:
        # Get all appointments for the user
        appointments = await db.appointments.find(
            {"user_id": ctx.author.id}
        ).sort("date", 1).to_list(None)
        
        if not appointments:
            await ctx.send("You have no upcoming appointments.")
            return
            
        response = "Your appointments:\n"
        for appt in appointments:
            response += f"- {appt['date']} at {appt['time']} with {appt['doctor']}\n"
        
        await ctx.send(response)
    except Exception as e:
        await ctx.send("Sorry, there was an error fetching your appointments.")
# Run the bot with your token
# Make sure to replace 'YOUR_BOT_TOKEN' with your actual token
bot.run(token)