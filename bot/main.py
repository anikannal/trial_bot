import discord
import os
#import pynacl
#import dnspython
import server
import json
import requests
import psycopg2
import tweepy
from discord.ext import commands

## get the bot handle
bot = commands.Bot(command_prefix="!")  
TOKEN = os.getenv("DISCORD_TOKEN")

## get the twitter api handle
CONSUMER_KEY = 'tj2MHMY3MnHmyqiRPLOZIKZ3z'
CONSUMER_SECRET = 'k0qzJ3ZKyTAVna4TipLyCfwkaaluX40qTMDuxF7iZJzYLZ9dNh'
ACCESS_KEY = '1395235059087544323-Ofa3VCul9S2jdB5UTwfMKmFrKOsvPJ'
ACCEES_SECRET = 'eBlz1J8pbpmrC4dd4xJVPxd2M5K8lV5b3qDtJxD7Mh8Hx'
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_KEY, ACCEES_SECRET)


api = tweepy.API(auth)

with open('follow_list.txt', 'r') as filehandle:
      follow_list = [acct.rstrip() for acct in filehandle.readlines()]

#DATABASE_URL = os.environ['DATABASE_URL']
#conn = psycopg2.connect(DATABASE_URL, sslmode='require')

def getjoke():
  response = requests.get("https://icanhazdadjoke.com/",  headers={"Accept":"application/json"})
  json_data = json.loads(response.text)
  joke = json_data['joke']
  #joke = response.text
  #print(response)
  return joke

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}({bot.user.id})")

@bot.command()
async def ping(ctx):
  print()
  await ctx.send("pong")

@bot.command()
async def lol(ctx):
  joke = getjoke()
  await ctx.send(joke)

@bot.command()
async def read(ctx):
  list_of_tweets = []
  ## gather all the tweets
  for acct in follow_list:
    public_tweets = api.user_timeline(acct)
    for tweet in public_tweets:
      list_of_tweets.append("https://twitter.com/"+acct+"/status/"+str(tweet.id))
  ## show all the tweets
  for tweet in list_of_tweets:  
    await ctx.send(tweet)

@bot.command()
async def add(ctx, account_name):
  follow_list.append(account_name)
  ## add name to the follow list file
  with open('follow_list.txt', 'w') as filehandle:
    filehandle.writelines(account_name+"\n")
  send_str = "we are now following " + account_name
  await ctx.send(send_str)

## list all the accounts being followed
@bot.command()
async def list(ctx):
  for acct in follow_list:
    await ctx.send("https://twitter.com/"+acct)

## reply to a help message
@bot.event
async def on_message(message):
  await bot.process_commands(message)
  if message.author == bot.user:
    return
  if message.content.startswith("help"):
    await message.channel.send("hi, I am the twitter bot. I can follow twitter handles for you.\n 1. To read the latest tweets type - !read \n 2. To look at the list of handles I am following type - !list \n 3. To add a handle for me to follow type - !add <handle>")


server.server()
bot.run(TOKEN)
