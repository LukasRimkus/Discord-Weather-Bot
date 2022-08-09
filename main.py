"""
It it the main driver class which turns on the Discord bot. It contains all the bot events and commands. 
Also, environment variables are loaded here.
"""

from dotenv import load_dotenv
import discord
from discord.ext import commands
import os
from Utils.location import get_coordinates_data
from Utils.weather import get_weather_data
from Utils.forecast import process_weather_data_for_forecast, draw_forecast_graph


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
        raise Exception("Failed to load env variables!")


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
        to_send = f'Welcome {member.mention} to `{guild.name}`! Type in `.help` to receive available commands with descriptions!'
        await guild.system_channel.send(to_send)


@bot.command(name="hello")
async def hello(ctx):
    """Say hello to given person's name"""
    message = f"Hello, `{ctx.message.author}`! Ask me anything about the weather!"
    await ctx.send(message)


@bot.command(name="coordinates")
async def get_coordinates(ctx, *location):
    """Get the coordinates of the given location as a parameter."""

    latitude, longitude, timezone_offset_h, found_location = await get_coordinates_data(LOCATION_API_TOKEN, *location)
    message = f"Given location: `{' '.join(location)}`. The system found this location: `{found_location}`.\nLatitude = `{latitude}`, longitude = `{longitude}`, timezone = `{timezone_offset_h}` hours from UTC"

    await ctx.send(message)


@bot.command(name="weather")
async def get_weather(ctx, *location):
    """Get the weather of the given location as a parameter."""

    latitude, longitude, timezone_offset_h, found_location = await get_coordinates_data(LOCATION_API_TOKEN, *location)

    parameters = {
            "latitude": latitude,
            "longitude": longitude,
            "current_weather": "true"
        }

    response = await get_weather_data(parameters)

    try:
        temperature = response["current_weather"]["temperature"]
        windspeed = response["current_weather"]["windspeed"]
        winddirection = response["current_weather"]["winddirection"]
        time = response["current_weather"]["time"]
    except KeyError as e:
        print(e)
        raise Exception("Error occurred in the weather API.")

    location_string = " ".join(location)

    message = f"Given location: `{location_string}`. The system found this location: `{found_location}`.\nLatitude = `{latitude}`, longitude = `{longitude}`, " \
        f"timezone = `{timezone_offset_h}` hours from UTC.\nCurrent weather = `{temperature} °C`, windspeed = `{windspeed} km/h`, wind direction = `{winddirection}`, time slot in UTC = `{time}`."

    await ctx.send(message)


@bot.command(name="forecast")
async def get_forecast(ctx, *location):
    """Get the forecast for the five days of the given location as a parameter."""

    latitude, longitude, timezone_offset_h, found_location = await get_coordinates_data(LOCATION_API_TOKEN, *location)

    parameters = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": "temperature_2m,precipitation"
    }
    response = await get_weather_data(parameters)
    location_string = " ".join(location)

    hours, temperature, precipitation, time_string = process_weather_data_for_forecast(response, timezone_offset_h)
    title = f"Weather forecast for '{location_string}', latitude = {latitude:.2f}, longitude = {longitude:.2f}, {time_string}"

    draw_forecast_graph(hours, temperature, precipitation, title)
    
    await ctx.send(f"Weather forecast for `{location_string}`! The system found this location: `{found_location}`.", file=discord.File('forecast.png'))
    

@get_coordinates.error
@get_weather.error
@get_forecast.error
async def print_error(ctx, error):
    error_message = f"Error occurred: {error} Try again!"
    print(error_message)

    await ctx.send(error_message)


if __name__ == "__main__":
    set_constants_from_env_variables()
    bot.run(DISCORD_TOKEN)
