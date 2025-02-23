import logging

from logging import config
from src.settings.slack import SlackLoader, SLACK_CONFIG


LOGGING_CONFIG = {
    "version": 1,
    "formatters": {"detail": {"format": "[%(levelname)s|%(filename)s:%(lineno)s] %(asctime)s > %(message)s"}},
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "detail",
            "stream": "ext://sys.stdout",
        },
    },
    "loggers": {
        "": {
            "handlers": ["console"],
            "level": "INFO",
        }
    }
}


def logger_setting(brand_name=None):
    if brand_name:
        setattr(logging.LogRecord, "brand_name", brand_name)

    config.dictConfig(LOGGING_CONFIG)
    SlackLoader.set_config(SLACK_CONFIG)