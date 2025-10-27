import os
import discord
import logging
from discord.ext import commands
from dotenv import load_dotenv
from memory.memory_client import *
from prompts.rag_prompt import *
from initializers.initialize_llm import *


load_dotenv()
discord_token = os.getenv("DISCORD_API_KEY")

handler = logging.FileHandler(filename="discord.log", encoding="utf-8", mode="w")
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="?", intents=intents)


@bot.event
async def on_ready():
    print("Booting up your system")
    print(f"I am running on {bot.user.name}")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    await bot.process_commands(message)

@bot.command()
async def add_context(ctx): 
    await ctx.send("`Fetching channel history... This may take a moment.`")
    history_limit = 50
    messages = []
    async for msg in ctx.channel.history(limit=history_limit):
        if (msg.author == bot.user or 
            msg.id == ctx.message.id or 
            msg.content.startswith(bot.command_prefix)):
            continue
        messages.append(f"{msg.author.name}: {msg.content}")
    messages.reverse()
    full_context = "\n".join(messages)

    if not full_context:
        await ctx.send("No recent messages found to add.")
        return
    success = await add_single_memory(
        context=full_context,
        user_id=("testing") 
    )
    if success.get("status") == "success":
        await ctx.send(f"✅ **Context Synced!**")
    else:
        await ctx.send("An error occurred while adding context.")


@bot.command()
async def query(ctx,*,query):
    await ctx.send("`Searching the knowledge base..`")
    memories = await search_memory(
        query=query,
        user_id=str("testing")
    )    
    print("memories recieved ", memories)
    if len(memories) > 1900:
        output = f"Relevant memories:\n{memories[:1900]}\n... (truncated)"
    else:
        output = f"Relevant memories:\n{memories}"
    prompt=rag_prompt(context=output,query=query)
    llm=initialize_chat_llm()
    response=llm.invoke(prompt)
    await ctx.send(response.content)



@bot.command()
async def introduce(ctx):
    help_message = f"""🤖 **Welcome to ContextIQ!**

Hello {ctx.author.mention} ! I am **ContextIQ**, an AI-powered knowledge base built by **Team Code Geass**.

I'm designed to work like a smart new teammate: one that **listens, remembers, and keeps your team on track**.

### 🎯 The Problem I Solve
In busy projects, vital information often gets lost in the flood of messages. This creates confusion about key tasks, decisions, and who is responsible for what.

### 🤔 How I Work
My primary role in this server is to act as a **Chat Listener**.

* I automatically capture information from our conversations here, as well as from meetings and shared files.
* I organize everything into a single, centralized knowledge base.
* This allows our team to find any detail later using simple, natural language queries.

Beyond just remembering, I will also help **automatically track tasks** , highlight project updates, and **send personal reminders** to make sure nothing slips through the cracks.

> **🔒 Your Privacy is Our Priority**
> Our system uses a strict **privacy-first design**. You have complete control over what data is shared , and all associated data is automatically deleted once a project is completed.

### 🛠️ Available Commands
* `?query [your question]`: Ask a question to the team's knowledge base.
* `?tasks`: See all tasks extracted from the conversations.
* `?add_context`: add all the memories to the knowledge base.

"""
    await ctx.send(help_message)

if __name__ == "__main__":
    if not discord_token:
        print("Error: DISCORD_API_KEY not found. Please check your .env file.")
    else:
        bot.run(discord_token, log_handler=handler, log_level=logging.DEBUG)
