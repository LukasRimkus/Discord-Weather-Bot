"""
This is the forecast.py file which contains the methods responsible for processing weather data and
plotting a graph with that data.
"""


import matplotlib.pyplot as plt
from datetime import datetime, timedelta


def process_weather_data_for_forecast(response, timezone_offset_h):
    """The method used to return required data for plotting a weather graph."""

    try:
        time = response["hourly"]["time"]
        number_of_hours = len(time)
        current_hour = int(datetime.utcnow().strftime("%H"))

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


def draw_forecast_graph(hours, temperature, precipitation, title):
    """
    Method to plot a forecast graph with temperature and precipitation in y axes and time in x axis.
    The image is saved and used to send to the Discord channel. 
    """

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
