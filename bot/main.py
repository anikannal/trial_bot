import os
import server
import discord
#import datetime
from discord.ext import commands, tasks
#from discord.ext import timers
from dotenv import load_dotenv
from Riddler import Riddler
import asyncio

## get the bot handle
bot = commands.Bot(command_prefix="!")
#bot.timer_manager = timers.TimerManager(bot)
load_dotenv('.env') 
TOKEN = os.environ['DISCORD_TOKEN']

rules = {
    "multi" : "- This is a riddle with multiple clues.\n- I will give you one clue at a time and wait.\n- You have to guess the answer before I run out of clues.\n- Here comes the first clue...",
    "single" : "Here comes your riddle - "
}

@tasks.loop(seconds=5.0, count=4)
async def slow_count():
    print('waiting for the anwer...')

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}({bot.user.id})")
    
@bot.event
async def on_message(message):
    await bot.process_commands(message)
    if message.author == bot.user:
        return
    if "riddle" in message.content.lower():
        
        await message.channel.send(f"Hi {message.author}, I am the Riddler Bot. Would you like to play?")
        
        def check(m):
            return "yes" in m.content and m.channel == message.channel

        try:
            msg = await bot.wait_for("message", check=check,timeout=10)
        except:
            await message.channel.send("Ok then, maybe some other time.")
            return
            
            
        await message.channel.send(f"The game is on, {msg.author}!")
        
        riddler = Riddler()
        riddle = riddler.get_riddle()
        embed = discord.Embed(title="Read...Steady...Go!", description=f"{rules[riddle.get_type()]}", color=0x00008B)
        await message.channel.send(embed=embed)
        await asyncio.sleep(10)
        counter = 1
        while (True):
            clue = riddle.next_clue()
            if clue==0:
                embed = discord.Embed(title="Time Up!", description=f"The answer is {riddle.get_answer()}.", color=0xff0000)
                # await message.channel.send('You are out of time! Better luck next time.')
                # await message.channel.send(f"The answer is {riddle.get_answer()}.")
                embed.set_footer(text='Better luck next time.',icon_url='https://cdn0.iconfinder.com/data/icons/emojis-with-black-line/744/EmojiOuch01-512.png')
                await message.channel.send(embed=embed)
                break
            if riddle.get_type() == "multi":
                embed = discord.Embed(title="Clue "+str(counter), description=clue[0], color=0x0000ff)
                embed.set_image(url = f"{clue[1]}")
                embed.set_footer(text=f"You have {riddle.get_time()} seconds.",icon_url="https://cdn1.iconfinder.com/data/icons/tourism-travel-1-3/65/29-512.png")
                counter+=1
                await message.channel.send(embed=embed)
            else:
                embed = discord.Embed(title="Riddle Diddle", description=clue[0], color=0x0000ff)
                embed.set_image(url = f"{clue[1]}")
                embed.set_footer(text=f"You have {riddle.get_time()} seconds.",icon_url="https://cdn1.iconfinder.com/data/icons/tourism-travel-1-3/65/29-512.png")
                await message.channel.send(embed=embed)
            
            try:
                def answer_check(m):
                    return m.content.lower() in riddle.get_answer().lower() and m.channel == message.channel
                msg = await bot.wait_for("message", check=answer_check,timeout=riddle.get_time())
                embed = discord.Embed(title="That's Correct!", description=f"Great going, {message.author}. That is the correct answer!", color=0x00ff00)
                embed.set_footer(text='Well done!',icon_url='https://d1nhio0ox7pgb.cloudfront.net/_img/g_collection_png/standard/256x256/ok.png')
                #await message.channel.send(f"Great going, {message.author}. That is the correct answer!")
                await message.channel.send(embed=embed)
                break
            except:
                await message.channel.send("Seems like nobody got it.")

server.server()
bot.run(TOKEN)
        
            
        
                    
        
        
        
    
  

  

# @bot.command()
# async def read(ctx):
#   ## identify the source - which guild and which channel
#   guild = str(ctx.guild)
#   channel = str(ctx.message.channel)
#   #print("inside read "+str(guild)+" "+str(channel))
#   ## get all the relevant tweets for this guild and channel
#   list_of_tweets = twitter_handler.get_tweets(guild, channel)
#   if list_of_tweets==0:
#     await ctx.send('You have not added any accounts to follow. \nYou can use the !add command to add accounts to follow.')
#   ## share all the tweets
#   elif list_of_tweets==1:
#     await ctx.send('No new tweets found for the accounts you are following.')
#   else:
#     for tweet in list_of_tweets:
#       await ctx.send(tweet)

# @bot.command()
# async def add(ctx, account_name):
#   ## check if account is already being followed by this guild and channel
#   ## identify the source - which guild and which channel
#   guild = str(ctx.guild)
#   channel = str(ctx.message.channel)
#   #print("inside add "+guild+" "+channel)
#   ## add account to the follow list for this guild and channel
#   response = twitter_handler.add_account(account_name, guild, channel)
#   await ctx.send(response)

# ## list all the accounts being followed
# @bot.command()
# async def list(ctx):
#   ## identify the source - which guild and which channel
#   guild = str(ctx.guild)
#   channel = str(ctx.message.channel)
#   #print("inside list "+guild+" "+channel)
#   ## find all the accounts followed by this guild and channel
#   accounts_list = twitter_handler.get_follow_list(guild,channel)
#   ## share the list of accounts being followed
#   if accounts_list == 0:
#     await ctx.send("You are not following any accounts yet. \nUse the !add command to follow accounts.")
#   else:
#     for acct in accounts_list:
#       await ctx.send(acct)

# @bot.command()
# async def count(ctx,i=0):
#   guild = str(ctx.guild)
#   channel = str(ctx.message.channel)
#   response = twitter_handler.set_count(guild,channel,i)
#   await ctx.send(response)

# ## reply to a help message
# @bot.event
# async def on_message(message):
#   await bot.process_commands(message)
#   if message.author == bot.user:
#     return
#   if message.content.startswith("help"):
#     await message.channel.send("hi, I am your twitter bot. I can follow twitter handles for you.\n 1. To read the latest tweets type - !read \n 2. To look at the list of handles I am following type - !list \n 3. To add a handle for me to follow type - !add <handle>")

#   if message.content.startswith('hello'):
#         embedVar = discord.Embed(title="Title", description="Desc", color=0x00ff00)
#         embedVar.add_field(name="Field1", value="hi", inline=False)
#         embedVar.add_field(name="Field2", value="hi2", inline=True)
#         embedVar.set_footer(text="footer")
#         await message.channel.send(embed=embedVar)

# @bot.command(name="remind")
# async def remind(ctx, time, *, text):
#     """Remind to do something on a date.

#     The date must be in ``Y/M/D`` format."""
#     date = datetime.datetime(*map(int, time.split("/")))

#     bot.timer_manager.create_timer("reminder", date, args=(ctx.channel.id, ctx.author.id, text))
#     # or without the manager
#     timers.Timer(bot, "reminder", date, args=(ctx.channel.id, ctx.author.id, text)).start()

# @bot.event
# async def on_reminder(channel_id, author_id, text):
#     channel = bot.get_channel(channel_id)

#     await channel.send("Hey, <@{0}>, remember to: {1}".format(author_id, text))

