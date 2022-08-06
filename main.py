from unicodedata import name
from dotenv import load_dotenv, dotenv_values
import discord
from discord.ext import commands
import aiohttp


load_dotenv()

DISCORD_TOKEN = ""
GUILD = ""
LOCATION_API_TOKEN = ""

description = '''This bot is responsible for giving data regarding weather all over the world!'''
intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix='.', description=description, intents=intents)


def set_constants_from_env_variables():
    global DISCORD_TOKEN, GUILD, LOCATION_API_TOKEN

    env_variables = dotenv_values(".env")

    try:
        DISCORD_TOKEN = env_variables["DISCORD_TOKEN"]
        GUILD = env_variables["DISCORD_GUILD"]
        LOCATION_API_TOKEN = env_variables["LOCATION_API_TOKEN"]
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


@bot.command(name="hello")
async def hello(ctx):
    """Say hello to given person's name"""
    message = f"Hello, {ctx.message.author}! Ask me anything about the weather!"
    await ctx.send(message)


# TODO: add error handling
async def get_coordinates_data(*location):
    async with aiohttp.ClientSession() as session:
        base_url = "http://api.positionstack.com/v1/forward"
        location_string = " ".join(location)
        params = {
            "access_key": LOCATION_API_TOKEN,
            "query": location_string,
            "limit": 1,
            "timezone_module": 1
        }

        async with session.get(base_url, params=params) as response:
            if response.status == 200:
                json_response = await response.json()
                data = json_response["data"]
                latitude, longitude, timezone_offset_sec = data[0]["latitude"], data[0]["longitude"], data[0]["timezone_module"]["offset_sec"]
            else:
                response.raise_for_status()
    
    timezone_offset_h = int(timezone_offset_sec)//3600

    return latitude, longitude, timezone_offset_h


@bot.command(name="coordinates")
async def get_coordinates(ctx, *location):
    """Get the coordinates of the location"""

    latitude, longitude, timezone_offset_h = await get_coordinates_data(*location)
    message = f"Given location: {' '.join(location)}.\nLatitude = {latitude}, longitude = {longitude}, timezone = {timezone_offset_h} hours"

    await ctx.send(message)


# TODO: add error handling
@bot.command(name="weather")
async def get_weather(ctx, *location):
    """Get the weather of the location"""

    latitude, longitude, timezone_offset_h = await get_coordinates_data(*location)

    async with aiohttp.ClientSession() as session:
        base_url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "current_weather": "true"
        }

        async with session.get(base_url, params=params) as response:
            if response.status == 200:
                json_response = await response.json()
                temperature = json_response["current_weather"]["temperature"]
                windspeed = json_response["current_weather"]["windspeed"]
                winddirection = json_response["current_weather"]["winddirection"]
                time = json_response["current_weather"]["time"]
            else:
                response.raise_for_status()

    location_string = " ".join(location)

    message = f"Given location: {location_string}.\nLatitude = {latitude}, longitude = {longitude}, timezone = {timezone_offset_h} hours from UTC.\n" \
        f"Current weather = {temperature} °C, windspeed = {windspeed} km/h, winddirection = {winddirection}, UTC time slot = {time}."

    await ctx.send(message)


if __name__ == "__main__":
    set_constants_from_env_variables()
    bot.run(DISCORD_TOKEN)
