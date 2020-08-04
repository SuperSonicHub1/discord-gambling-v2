import discord
from discord.ext import commands
import os
import logging
import json
import random
from keep_alive import keep_alive

# LOGGING START
logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(
    filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(
    logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)
# LOGGING END

f = open('logbook.json', 'r')
logbook = json.load(f)

bot = commands.Bot(
    command_prefix='!', 
    activity=discord.Activity(name='!gamble', type=discord.ActivityType.listening)
)

@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))

@bot.command()
async def gamble(ctx, guess):
    if str(ctx.message.channel) != "virtual-gambling":
        return
    try:
        logbook[ctx.message.author.name]
    except KeyError:
        logbook[ctx.message.author.name] = {
            'credits': 0,
            'wins': 0,
            'losses': 0
        }
    rnjesus = random.randrange(1, 100)
    try:
        answer = int(guess)
    except ValueError:
        await ctx.send(f"@{ctx.message.author.name}, please use a number as your guess.")
        return
    if not 1 <= answer <= 100:
        await ctx.send(f"@{ctx.message.author.name}, please use a number between 1 and 100 as your guess.")
        return
    if not rnjesus == answer:
        logbook[ctx.message.author.name]['losses']+=1
        logbook[ctx.message.author.name]['credits']-=answer
        await ctx.send(f"@{ctx.message.author.name}, you guessed incorectly; the number was {rnjesus}.")
    else:
        logbook[ctx.message.author.name]['wins']+=1
        logbook[ctx.message.author.name]['credits']+=(2*answer)
        await ctx.send(f"@{ctx.message.author.name}, you guessed incorectly!")
    json.dump(logbook, open('logbook.json', 'w'))

@gamble.error
async def gamble_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"@{ctx.message.author.name}, please include a guess.")

@bot.command()
async def stats(ctx):
    if str(ctx.message.channel) != "virtual-gambling":
        return
    try:
        log = logbook[ctx.message.author.name]
    except KeyError:
        logbook[ctx.message.author.name] = {
            'credits': 0,
            'wins': 0,
            'losses': 0
        }
        json.dump(logbook, open('logbook.json', 'w'))
        log = logbook[ctx.message.author.name]
    await ctx.send(f"""Stats for @{ctx.message.author.name}:
    Credits: {log['credits']}
    Wins: {log['wins']}
    Losses: {log['losses']}""")

keep_alive()
bot.run(os.environ.get('DISCORD_BOT_SECRET'))