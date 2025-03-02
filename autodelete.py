import os
from dotenv import load_dotenv 
from discord.ext import commands, tasks
import discord
from datetime import timedelta

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True 

client = commands.Bot(command_prefix="!", intents=intents) 

@client.event
async def on_ready():
    print(f'Bot logged in as {client.user}')
    delete_old_messages.start()  

@tasks.loop(hours=1)
async def delete_old_messages():
    print(f"{discord.utils.utcnow()} - Checking for messages older than 14 days...")

    channel_id = 1345154695353733131
    channel = client.get_channel(channel_id)

    if not channel:
        print(f"Channel with ID {channel_id} not found! Make sure the bot has access.")
        return

    now = discord.utils.utcnow()
    cutoff = now - timedelta(days=14)  

    async for message in channel.history(limit=1000):
        if message.pinned:
            continue
        if message.created_at < cutoff:
            try:
                await message.delete()
                print(f"{now} - Deleted message: {message.content} (ID: {message.id}) from {message.created_at}")
            except (discord.Forbidden, discord.HTTPException) as e:
                print(f"Error deleting the message: {e}")

client.run(os.getenv('DISCORD_TOKEN'))
