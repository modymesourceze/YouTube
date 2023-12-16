import os


class Config(object):
    TG_BOT_TOKEN = os.environ.get("TG_BOT_TOKEN", "")

    APP_ID = int(os.environ.get("APP_ID", 25281175))

    API_HASH = os.environ.get("API_HASH", "6d99cb2b60a2c519fc1f99bd19565730")
