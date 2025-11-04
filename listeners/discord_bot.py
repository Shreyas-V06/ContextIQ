import os
import discord
import logging
from discord.ext import commands
from dotenv import load_dotenv
from memory.memory_client import *
from prompts.rag import *
from initializers.initialize_llm import *



load_dotenv()
discord_token = os.getenv("DISCORD_API_KEY")

handler = logging.FileHandler(filename="discord.log", encoding="utf-8", mode="w")
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="?", intents=intents)

conversation_since_last_command=""

@bot.event
async def on_ready():
    print()
    print("-------------------------")
    print("| DISCORD BOT IS LIVE ! |")
    print("-------------------------")
    print()

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    global conversation_since_last_command
    conversation_since_last_command+=f"{message.author}:{message.content}\n"
    await bot.process_commands(message)

@bot.command()
async def add(ctx): 
    await ctx.send("`Messages queued for reading. Context Synced`")
    global conversation_since_last_command
    if conversation_since_last_command=="":
        await ctx.send("No recent messages found to add.")
        return
    processed_context_string = invoke_conversation_processor(conversation=conversation_since_last_command)
    print(processed_context_string)
    processed_contexts=processed_context_string.split("###END OF TOPIC###")
    for context in processed_contexts:
        success = await add_single_memory(
        context=context,
        user_id=("central-memories")
        )
    conversation_since_last_command=""
    

@bot.command()
async def query(ctx,*,query):
    await ctx.send("`Searching the knowledge base..`")
    memories = await search_memory(
        query=query,
        user_id=str("central-memories")
    )    
    # print("memories recieved ", memories)
    if len(memories) > 1900:
        output = f"Relevant memories:\n{memories[:1900]}\n... (truncated)"
    else:
        output = f"Relevant memories:\n{memories}"
    rag_prompt=get_rag_prompt(context=output,query=query)
    llm=initialize_chat_llm()
    response=llm.invoke(rag_prompt)
    await ctx.send(response.content)


@bot.command()
async def introduce(ctx):
    help_message = f"""🤖 **Welcome to Wisdom!**

Hello {ctx.author.mention} ! I am **Wisdom**, an AI-powered knowledge base built by **Team Code Geass**.

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
* `?add`: add all the conversation to the knowledge base.

"""
    await ctx.send(help_message)

@bot.command()
async def reset(ctx):
    global conversation_since_last_command
    conversation_since_last_command=""
    await ctx.send("Conversation has been reset")

if __name__ == "__main__":
    if not discord_token:
        print("Error: DISCORD_API_KEY not found. Please check your .env file.")
    else:
        bot.run(discord_token, log_handler=handler, log_level=logging.DEBUG)
