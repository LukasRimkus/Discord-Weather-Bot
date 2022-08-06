from dotenv import load_dotenv, dotenv_values
import discord
from discord.ext import commands
import requests
import json


load_dotenv()

DISCORD_TOKEN = ""
GUILD = ""

description = '''This bot is responsible for giving data regarding weather all over the world!'''
intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix='.', description=description, intents=intents)


def set_constants_from_env_variables():
    global DISCORD_TOKEN, GUILD

    env_variables = dotenv_values(".env")

    try:
        DISCORD_TOKEN = env_variables["DISCORD_TOKEN"]
        GUILD = env_variables["DISCORD_GUILD"]
    except KeyError as e:
        print(f"Please set all environment variables. Error: {e}")


@bot.event
async def on_ready():
    guild = discord.utils.get(bot.guilds, name=GUILD)

    if not guild:
        print(f"There is no such GUILD = {GUILD}. Try again after updating GUILD.")
        exit()

    print(f'We have logged in as {bot.user} (ID: {bot.user.id}). The guild connected to is {guild.name} (ID: {guild.id})')


@bot.event
async def on_member_join(member):
    guild = member.guild
    if guild.system_channel is not None:
        to_send = f'Welcome {member.mention} to {guild.name}!'
        await guild.system_channel.send(to_send)


@bot.command()
async def hello(ctx, name="stranger"):
    """Say hello"""
    message = f"Hello, {name}!"
    await ctx.send(message)


if __name__ == "__main__":
    set_constants_from_env_variables()
    bot.run(DISCORD_TOKEN)
