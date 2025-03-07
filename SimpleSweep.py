import os
from dotenv import load_dotenv 
from discord.ext import commands, tasks
import discord
from datetime import timedelta

load_dotenv()

# Lade Konfiguration aus .env Datei
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID", "0"))  # Default to 0 if not found

intents = discord.Intents.default()
intents.message_content = True 

client = commands.Bot(command_prefix="!", intents=intents) 

@client.event
async def on_ready():
    print(f'Bot logged in as {client.user}')
    delete_old_messages.start()  

@tasks.loop(hours=1)
async def delete_old_messages():
    print(f"{discord.utils.utcnow()} - Checking for messages and threads older than 14 days...")

    channel_id = CHANNEL_ID
    channel = client.get_channel(channel_id)

    if not channel:
        print(f"Channel with ID {channel_id} not found! Make sure the bot has access and CHANNEL_ID is correctly set in .env file.")
        return

    now = discord.utils.utcnow()
    cutoff = now - timedelta(hours=333)  # Adds buffer time of 3hours to avoid conflicts with Discord's message deletion limit... it's nearly 14 days

    # Delete old messages
    async for message in channel.history(limit=1000):
        if message.pinned:
            continue
        if message.created_at < cutoff:
            try:
                await message.delete()
                print(f"{now} - Deleted message: {message.content} (ID: {message.id}) from {message.created_at}")
            except (discord.Forbidden, discord.HTTPException) as e:
                print(f"Error deleting the message: {e}")
    
    # Delete old threads
    try:
        # Get the guild (server) from the channel
        guild = channel.guild
        
        # Get all threads in the guild
        threads = await guild.active_threads()
        
        # Check and delete threads in the specified channel
        for thread in threads:
            # Only delete threads in our target channel
            if thread.parent_id == channel_id and thread.created_at < cutoff:
                try:
                    await thread.delete()
                    print(f"{now} - Deleted thread: {thread.name} (ID: {thread.id}) from {thread.created_at}")
                except (discord.Forbidden, discord.HTTPException) as e:
                    print(f"Error deleting the thread: {e}")
    
    except Exception as e:
        print(f"Error handling threads: {e}")

client.run(DISCORD_TOKEN)
