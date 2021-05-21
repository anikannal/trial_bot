import discord
import os
#import pynacl
#import dnspython
import server
import json
import requests
import psycopg2
from discord.ext import commands

bot = commands.Bot(command_prefix="!")
TOKEN = os.getenv("DISCORD_TOKEN")

DATABASE_URL = os.environ['DATABASE_URL']
conn = psycopg2.connect(DATABASE_URL, sslmode='require')

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

@bot.event
async def on_message(message):
  await bot.process_commands(message)
  if message.author == bot.user:
    return
  if message.content.startswith("$hello"):
    await message.channel.send("https://twitter.com/BonhamClive/status/1395807408635535364")


server.server()
bot.run(TOKEN)
