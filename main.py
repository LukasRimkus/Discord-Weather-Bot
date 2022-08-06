from dotenv import load_dotenv, dotenv_values


load_dotenv()

DISCORD_TOKEN = None


def set_constants_from_env_variables():
    env_variables = dotenv_values(".env")

    try:
        DISCORD_TOKEN = env_variables["DISCORD_TOKEN"]
        print("Success")
    except KeyError as e:
        print(f"Please set all environment variables. Error: {e}")


if __name__ == "__main__":
    set_constants_from_env_variables()
