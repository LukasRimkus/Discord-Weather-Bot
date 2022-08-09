"""
This is the weather.py file which contains the method responsible for making an API request
to abtain data about the weather in the given location in parameters. 
"""


import aiohttp


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
