from dotenv import load_dotenv, dotenv_values


load_dotenv()
env_variables = dotenv_values(".env")


DISCORD_TOKEN = None


def set_env_variables():
    try:
        DISCORD_TOKEN = env_variables["DISCORD_TOKEN"]

    except KeyError as e:
        print(f"Please set all environment variables. Error: {e}")


if __name__ == "__main__":
    set_env_variables()
