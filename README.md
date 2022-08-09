# Discord Weather Bot
---------------------------------------------
### Description
---------------------------------------------
This project is about the Discord Bot which is able to tell current weather and weather forecast regarding the given location. The library used to communicate with the Discord API is [Discordpy](https://discordpy.readthedocs.io/en/latest/). API key is also necessary to acquire from Discord. What is more, two public APIs are used to fetch the data - the first is [Open Meteo](https://open-meteo.com/) which is used to fetch data about the weather given latitude and longitude. The second is [OpenCage](https://opencagedata.com/api) which is used to obtain the latitude and longitude from a description of a location. You will need to obtain the key for the latter API.

### How to start
---------------------------------------------
First of all, you have to configure everything on the [Discord Portal side](https://discord.com/developers/docs/intro). You have to create an application, then a bot and add to a chosen guild. Then the fun part begins - python programming which you have to be comfortable with.

### How to run the code
---------------------------------------------
Firstly, check if you have Python version at least `3.8` and `pip` installed. Then create a virtual environment and run on the console in the project directory `pip install -r requirements.txt` to download all the required libraries for the project. Also, you will need to create an file containing all the environment variables called `.env`. There are three of them: `DISCORD_TOKEN`, `GUILD`, and `LOCATION_API_TOKEN`.
On Windows, run in the console in the project directory `python main.py`. On Linux or Mac, run `python3 main.py`, then the bot starts. 

### Implemented Commands
---------------------------------------------
All the commands start with a dot `.`. 

##### Command help
To obtain all the implemented commands on Discord server, type in `.help` on the chosen text channel, as the bot prints out all the available commands with some description.

##### Command hello
Type in `.hello`, then the bot is going to say hi to you!

##### Command .coordinates
Type in `.coordinates <location>`, then the bot is going to provide you with the coordinates and time zone regarding the given location.

##### Command weather
Type in `.weather <location>`, then the bot is going to give the data (e.g. temperature) about the current weather in the given location. 

##### Command forecast
Type in `.forecast <location>`, then the bot is going to supply you with a graph with the temperature and precipitation forecast for the following week. 

### Deployment
---------------------------------------------
Follow this [tutorial](https://discord.com/developers/docs/tutorials/hosting-on-heroku) to deploy the application on Heroku.

---------------------------------------------
© Lukas Rimkus 2022