"""
This is the location.py file which contains the methods responsible for making an API request
to abtain data about the given location like coordinates. 
"""


import aiohttp


async def get_coordinates_data(LOCATION_API_TOKEN, *location):
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
