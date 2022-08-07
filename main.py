from unicodedata import name
from dotenv import load_dotenv, dotenv_values
import discord
from discord.ext import commands
import aiohttp
import os
import matplotlib.pyplot as plt


load_dotenv()

DISCORD_TOKEN = ""
GUILD = ""
LOCATION_API_TOKEN = ""

description = '''This bot is responsible for giving data regarding weather all over the world!'''
intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix='.', description=description, intents=intents)


def set_constants_from_env_variables():
    """Method to set environment variables."""
    global DISCORD_TOKEN, GUILD, LOCATION_API_TOKEN

    try:
        DISCORD_TOKEN = os.environ["DISCORD_TOKEN"]
        GUILD = os.environ["DISCORD_GUILD"]
        LOCATION_API_TOKEN = os.environ["LOCATION_API_TOKEN"]
    except KeyError as e:
        print(f"Please set all environment variables. Error: {e}")


@bot.event
async def on_ready():
    """Print some data to the console when the bot turns on."""
    guild = discord.utils.get(bot.guilds, name=GUILD)

    if not guild:
        print(f"There is no such GUILD = {GUILD}. Try again after updating GUILD.")
        exit()

    print(f'We have logged in as {bot.user} (ID: {bot.user.id}). The guild connected to is {guild.name} (ID: {guild.id})')


@bot.event
async def on_member_join(member):
    """Welcome message for the new member of the guild."""
    guild = member.guild
    if guild.system_channel is not None:
        to_send = f'Welcome {member.mention} to {guild.name}!'
        await guild.system_channel.send(to_send)


@bot.command(name="hello")
async def hello(ctx):
    """Say hello to given person's name"""
    message = f"Hello, {ctx.message.author}! Ask me anything about the weather!"
    await ctx.send(message)


async def get_coordinates_data(*location):
    """Method to make ayncronous request to fetch coordinates from the given location."""
    if len(location) == 0:
        raise Exception("provide at least one parameter for location")

    timeout = aiohttp.ClientTimeout(total=60)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        base_url = "http://api.positionstack.com/v1/forward"
        location_string = " ".join(location)
        params = {
            "access_key": LOCATION_API_TOKEN,
            "query": location_string,
            "limit": 1,
            "timezone_module": 1
        }

        async with session.get(base_url, params=params) as response:
            json_response = await response.json()

            if response.status == 200 and json_response["data"]:
                data = json_response["data"]
                latitude, longitude, timezone_offset_sec = data[0]["latitude"], data[0]["longitude"], data[0]["timezone_module"]["offset_sec"]
            else:
                error_message = "Some Error!"
                if 'error' in json_response:
                    error_message = f"{json_response['error']['message']}. {json_response['error']['context']['query']['message']}."
                elif "data" in json_response and not json_response["data"]:
                    error_message = "There are no results given the location!"
                
                raise Exception(error_message)

    timezone_offset_h = int(timezone_offset_sec)//3600

    return latitude, longitude, timezone_offset_h


@bot.command(name="coordinates")
async def get_coordinates(ctx, *location):
    """Get the coordinates of the given location as a parameter."""

    latitude, longitude, timezone_offset_h = await get_coordinates_data(*location)
    message = f"Given location: {' '.join(location)}.\nLatitude = {latitude}, longitude = {longitude}, timezone = {timezone_offset_h} hours"

    await ctx.send(message)


async def get_weather_data(latitude, longitude, timezone_offset_h, parameters):
    """Method to make ayncronous request to fetch weather data from the given coordinates."""

    timeout = aiohttp.ClientTimeout(total=60)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        base_url = "https://api.open-meteo.com/v1/forecast"

        async with session.get(base_url, params=parameters) as response:
            json_response = await response.json()

            if response.status == 200:
                return json_response
            else:
                error_message = "Some Error!"
                if 'error' in json_response:
                    error_message = f"{json_response['reason']}."

                raise Exception(error_message)


@bot.command(name="weather")
async def get_weather(ctx, *location):
    """Get the weather of the given location as a parameter."""

    latitude, longitude, timezone_offset_h = await get_coordinates_data(*location)

    parameters = {
            "latitude": latitude,
            "longitude": longitude,
            "current_weather": "true"
        }

    response = await get_weather_data(latitude, longitude, timezone_offset_h, parameters)

    temperature = response["current_weather"]["temperature"]
    windspeed = response["current_weather"]["windspeed"]
    winddirection = response["current_weather"]["winddirection"]
    time = response["current_weather"]["time"]

    location_string = " ".join(location)

    message = f"Given location: {location_string}.\nLatitude = {latitude}, longitude = {longitude}, timezone = {timezone_offset_h} hours from UTC.\n" \
        f"Current weather = {temperature} °C, windspeed = {windspeed} km/h, winddirection = {winddirection}, UTC time slot = {time}."

    await ctx.send(message)


@bot.command(name="forecast")
async def get_forecast(ctx, *location):
    """Get the forecast for the five days of the given location as a parameter."""

    latitude, longitude, timezone_offset_h = await get_coordinates_data(*location)

    parameters = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": "temperature_2m,precipitation"
    }
    response = await get_weather_data(latitude, longitude, timezone_offset_h, parameters)

    time = response["hourly"]["time"]
    temperature = response["hourly"]["temperature_2m"]
    precipitation = response["hourly"]["precipitation"]

    location_string = " ".join(location)

    await ctx.send("TEST")


@get_coordinates.error
@get_weather.error
@get_forecast.error
async def print_error(ctx, error):
    error_message = f"Error occurred: {error} Try again!"
    
    await ctx.send(error_message)


if __name__ == "__main__":
    set_constants_from_env_variables()
    bot.run(DISCORD_TOKEN)
