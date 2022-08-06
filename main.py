from dotenv import load_dotenv, dotenv_values
import discord
from discord.ext import commands
import requests
import json


load_dotenv()

# description = '''This bot is responsible for giving data reagrding weather all over the world!'''
# intents = discord.Intents.default()
# intents.members = True
# intents.dm_messages = True
# bot = commands.Bot(command_prefix='.', description=description, intents=intents)


class WeatherBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.set_constants_from_env_variables()
        self.description = '''This bot is responsible for giving data regarding weather all over the world!'''

        self.run(self.DISCORD_TOKEN)

    def set_constants_from_env_variables(self):
        env_variables = dotenv_values(".env")

        try:
            self.DISCORD_TOKEN = env_variables["DISCORD_TOKEN"]
            self.GUILD = env_variables["DISCORD_GUILD"]
        except KeyError as e:
            print(f"Please set all environment variables. Error: {e}")
    
    async def on_ready(self):
        # made an assumption that bot joined only one server 
        guild = discord.utils.get(self.guilds, name=self.GUILD)

        if not guild:
            print(f"There is no such GUILD = {self.GUILD}. Try again after updating GUILD.")
            exit()
        print("TEST")
        # print(f'We have logged in as {bot.user} (ID: {bot.user.id}). The guild connected to is {guild.name} (ID: {guild.id})')


# @bot.command()
# async def hello(ctx, name: str):
#     """Say hello"""
#     message = f"Hello, {name}!"
#     await ctx.send(message)



if __name__ == "__main__":
    bot = WeatherBot(command_prefix='.', intents=discord.Intents.default())

    # bot.run(bot.DISCORD_TOKEN)
