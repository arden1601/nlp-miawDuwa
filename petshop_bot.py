import discord
import os
import re
from dotenv import load_dotenv
from googleapiclient.discovery import build

# Load environment variables from .env file
load_dotenv()

# YouTube Data API setup
youtube_api_key = os.getenv('youtube_api')
youtube = build('youtube', 'v3', developerKey=youtube_api_key)

# Function to search YouTube and return the first video link
def search_youtube(keyword):
    request = youtube.search().list(
        part="snippet",
        q=keyword,
        type="video",
        maxResults=1
    )
    response = request.execute()

    # If a video is found, return its link
    if response['items']:
        video_id = response['items'][0]['id']['videoId']
        return f"https://www.youtube.com/watch?v={video_id}"
    else:
        return "Sorry, I couldn't find a video for that."

# Define patterns and responses with support for callable functions
patterns_responses = {
    r'hi|hello|hey|halo|hai': lambda _: 'Hello, how can I assist you with learning programming today?',
    r'(.*)?(feeling|kabar)': lambda _: 'I am doing great! How about you?',
    r'(.*)?(name|nama)': lambda _: 'I am a rule-based chatbot created to help you learn programming, from basic concepts to advanced topics.',
    r'(.*)?(do|help|lakukan)': lambda _: 'I can help you provide YouTube Video. Just type "$i want to learn <keyword>" to get started!',
    r'(.*)?(pertanyaan|question)': lambda _: 'Sure, feel free to ask your programming-related question!',
    r'(.*)?(about|tentang)(.*)': lambda keyword: f"Do you find {keyword} interesting?",
    r'(.*)?(terjebak|stuck)(.*)': lambda _: 'Feeling stuck is normal in programming. Take a deep breath and let me help you figure it out!',
    r'(.*)?(menyenangkan|fun)(.*)': lambda _: 'Programming can be very rewarding! What aspect of it are you enjoying the most?',
    r'(.*)?error(.*)': lambda _: 'Encountering an error is part of the learning process',
    r'(.*)?(sulit|susah|hard|difficult)(.*)': lambda _: 'Programming can be challenging at times',
    r'(.*)?menurut (saya|aku),(.*)': lambda _: 'Would you like to explore this topic further?',
    r'\$i want to learn (.+)': lambda keyword: f"Searching for '{keyword}' YouTube video...\n{search_youtube(keyword)}",
    r'thank you|thanks|terimakasih|makasih': lambda _: 'You are welcome! If you have more questions, feel free to ask.',
    r'bye|goodbye': lambda _: 'Goodbye! Have a great day!',
}

# Default response for unmatched patterns
default_response = "I'm sorry, I don't understand that. Can you please rephrase?"

# Function to match user input to a pattern and return the corresponding response
def get_response(user_input):
    for pattern, func in patterns_responses.items():
        match = re.search(pattern, user_input, re.IGNORECASE)
        if match:
            # Call the function associated with the matched pattern
            return func(match.group(1) if match.groups() else None)
    return default_response

# Initialize the bot with intents
intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    # Ignore messages from the bot itself
    if message.author == client.user:
        return

    user_input = message.content

    # Get the response based on user input
    response = get_response(user_input)

    # Send the response back to the Discord channel
    await message.channel.send(response)

# Run the bot with the token from the .env file
token = os.getenv('token')
client.run(token)