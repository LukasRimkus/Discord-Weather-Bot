# Discord Weather Bot
---------------------------------------------
### Description
---------------------------------------------
This project is about the Discord Bot which is able to tell current weather regarding the given location. The library used to communicate with the Discord API is [Discordpy](https://discordpy.readthedocs.io/en/latest/). Two public APIs are used to fetch the data - the first is [Open Meteo](https://open-meteo.com/en/doc) which is used to fetch data about the weather given latitude and longitude. The second is [positionstack](https://positionstack.com/) which is used to obtain the latitude and longitude from a description of a location. 

### How to start
---------------------------------------------
First of all, you have to configure everything on the [Discord Portal side](https://discord.com/developers/docs/intro). You have to create an application, then a bot and add to a chosen guild. Then the fun part begins - python programming.

### How to run the code
---------------------------------------------
Firstly, check if you have Python version at least 3.8 and pip installed. Then create a virtual environment and run on the console in the project directory `pip install -r requirements.txt` to download all the required libraries for the project. 
On Windows, run in the console in the project directory `python main.py`. On Linux or Mac, run `python3 main.py`, then the bot starts working. 

© Lukas Rimkus 2022