import discord
import os
#import pynacl
#import dnspython
import server
import json
import requests
#import psycopg2
#import tweepy
#from supporting_func import postgresql_to_dataframe
#import pandas as pd 
from discord.ext import commands
from TwitterHandler import TwitterHandler

## get the bot handle
bot = commands.Bot(command_prefix="!")  
TOKEN = os.getenv("DISCORD_TOKEN")

twitter_handler = TwitterHandler()

#DATABASE_URL = 'dbname=d5bk5r7n25mmri host=ec2-18-214-140-149.compute-1.amazonaws.com port=5432 user=yzfmvjdylfyenu password=2f863c383a3f16b84e9957490cdb9193d850dceee26d157f19991a4c51236e62 sslmode=require'

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}({bot.user.id})")

@bot.command()
async def read(ctx):
  ## identify the source - which guild and which channel
  guild = ctx.guild
  channel = ctx.message.channel
  ## get all the relevant tweets for this guild and channel
  list_of_tweets = twitter_handler.get_tweets(guild, channel)
  ## share all the tweets
  for tweet in list_of_tweets:
    await ctx.send(tweet)

@bot.command()
async def add(ctx, account_name):
  ## check if account is already being followed by this guild and channel
  ## identify the source - which guild and which channel
  guild = ctx.guild
  channel = ctx.message.channel
  ## add account to the follow list for this guild and channel
  response = twitter_handler.add_account(account_name, guild, channel)
  await ctx.send(response)

## list all the accounts being followed
@bot.command()
async def list(ctx):
  ## identify the source - which guild and which channel
  guild = ctx.guild
  channel = ctx.message.channel
  ## find all the accounts followed by this guild and channel
  accounts_list = twitter_handler.get_follow_list(guild,channel)
  ## share the list of accounts being followed
  for acct in accounts_list:
    await ctx.send(acct)

## reply to a help message
@bot.event
async def on_message(message):
  await bot.process_commands(message)
  if message.author == bot.user:
    return
  if message.content.startswith("help"):
    await message.channel.send("hi, I am your twitter bot. I can follow twitter handles for you.\n 1. To read the latest tweets type - !read \n 2. To look at the list of handles I am following type - !list \n 3. To add a handle for me to follow type - !add <handle>")

server.server()
bot.run(TOKEN)
