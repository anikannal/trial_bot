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

## create DB connection
DATABASE_URL = os.environ['DATABASE_URL']
conn = psycopg2.connect(DATABASE_URL, sslmode='require')
cursor = conn.cursor()

s = "SELECT twitter_account FROM follow_list"
cursor.execute(s)
follow_list = cursor.fetchall()
print(follow_list)

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
    public_tweets = api.user_timeline(acct[0])
    for tweet in public_tweets:
      list_of_tweets.append("https://twitter.com/"+acct[0]+"/status/"+str(tweet.id))
  ## show all the tweets
  for tweet in list_of_tweets:
    await ctx.send(tweet)

@bot.command()
async def add(ctx, account_name):
  follow_list.append((account_name,))
  ## add name to the follow list file
  s = ""
  s += "INSERT INTO follow_list"
  s += "("
  s += "twitter_account"
  s += ") VALUES (\""
  s += account_name
  s += "\");"
  cursor.execute(s)
  send_str = "we are now following " + account_name
  await ctx.send(send_str)

## list all the accounts being followed
@bot.command()
async def list(ctx):
  guild = ctx.guild
  channel = ctx.message.channel
  print(str(guild)+" : "+str(channel))
  for acct in follow_list:
    await ctx.send("https://twitter.com/"+acct[0])

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
