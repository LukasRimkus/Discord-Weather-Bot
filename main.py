from cProfile import label
from unicodedata import name
from dotenv import load_dotenv, dotenv_values
import discord
from discord.ext import commands
import aiohttp
import os
import matplotlib.pyplot as plt
from datetime import datetime, timedelta


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


async def get_coordinates_data(*location):
    """Method to make ayncronous request to fetch coordinates from the given location."""
    if len(location) == 0:
        raise Exception("provide at least one parameter for location")

    timeout = aiohttp.ClientTimeout(total=60)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        base_url = "https://api.opencagedata.com/geocode/v1/json"
        location_string = " ".join(location)
        params = {
            "key": LOCATION_API_TOKEN,
            "q": location_string,
            "limit": 1
        }

        async with session.get(base_url, params=params) as response:
            json_response = await response.json()
            
            if response.status == 200:
                try:
                    data = json_response["results"][0]
                    coordinates = data['geometry']
                    latitude, longitude = coordinates["lat"], coordinates["lng"]
                    timezone_offset_sec = data["annotations"]["timezone"]["offset_sec"]
                    found_location = data["formatted"]
                except KeyError as e:
                    print(e)
                    raise Exception("There was an error with fetching the data.")
                except Exception as e:
                    print(e)
                    raise Exception("Unexpected error!")
            else:
                try:
                    error_message = f"{json_response['status']['message']}"
                    raise Exception(error_message)
                except Exception as e:
                    print(e)
                    raise Exception("Unexpected error with the bad response from the API!")

    timezone_offset_h = float(timezone_offset_sec)/3600

    return latitude, longitude, timezone_offset_h, found_location


@bot.command(name="coordinates")
async def get_coordinates(ctx, *location):
    """Get the coordinates of the given location as a parameter."""

    latitude, longitude, timezone_offset_h, found_location = await get_coordinates_data(*location)
    message = f"Given location: `{' '.join(location)}`. The system found this location: `{found_location}`.\nLatitude = `{latitude}`, longitude = `{longitude}`, timezone = `{timezone_offset_h}` hours"

    await ctx.send(message)


async def get_weather_data(parameters):
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

    latitude, longitude, timezone_offset_h, found_location = await get_coordinates_data(*location)

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

    latitude, longitude, timezone_offset_h, found_location = await get_coordinates_data(*location)

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
    

def process_weather_data_for_forecast(response, timezone_offset_h):
    """The method used to return required data for plotting a weather graph."""

    time = response["hourly"]["time"]
    number_of_hours = len(time)
    current_hour = int(datetime.utcnow().strftime("%H"))

    try:
        hours = list(range(number_of_hours-current_hour))
        temperature = response["hourly"]["temperature_2m"][current_hour:]
        precipitation = response["hourly"]["precipitation"][current_hour:]
    except KeyError as e:
        print(e)
        raise Exception("Error occurred in the weather API.")

    current_time = (datetime.utcnow() + timedelta(hours=timezone_offset_h)).strftime("%H:%M")
    
    timezone = "UTC" + (f"+{timezone_offset_h:.1f}" if timezone_offset_h >= 0 else f"{timezone_offset_h:.1f}")

    time_string = f"{current_time} {timezone}"
    return hours, temperature, precipitation, time_string


# TODO: move code into several files
# TODO: logging
def draw_forecast_graph(hours, temperature, precipitation, title):
    plt.rcParams["figure.autolayout"] = True

    fig, ax1 = plt.subplots(figsize=(10.0, 6.0))

    ax1.plot(hours, temperature, color='red')
    ax1.set_ylabel('Temperature (°C)', color='red')
    ax1.tick_params(axis ='y', labelcolor = 'red') 

    ax2 = ax1.twinx()

    ax2.plot(hours, precipitation, color='blue')
    ax2.set_ylabel('Precipitation (mm)', color='blue')
    ax2.tick_params(axis ='y', labelcolor = 'blue') 

    ax1.set_xlabel('Hours from the current moment')
    
    plt.title(title, wrap=True)
    fig.tight_layout()
    plt.savefig("forecast.png")
    plt.close()


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
