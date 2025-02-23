import json
import logging

from logging.handlers import HTTPHandler
from typing import Dict, Any
from urllib.parse import urlparse
from settings.env import SLACK_HOOK_URL, BOT_NAME, CHANNEL

SLACK_CONFIG = {
    "handlers": {
        "slack": {
            "webhook_url": SLACK_HOOK_URL,
            "user_name": BOT_NAME,
            "channel": CHANNEL,
            "level": "INFO",
            "option": {"slack_filter": True, "level_emoji": True},
        }
    },
    "loggers": {
        "": {"handlers": ["slack"], "level": "INFO"},
    },
}


class SlackLoader:
    @staticmethod
    def set_config(log_config):

        handlers = dict()
        slack_list = log_config
        slack_formatter = SlackFormatter()

        for handle_name, handle_info in slack_list.get("handlers", {}).items():
            _url = handle_info["webhook_url"]
            _user_name = handle_info["user_name"]
            _channel = handle_info["channel"]
            _level = handle_info["level"]
            _option = handle_info.get("option", {})

            tmp_handlers = SlackHandler(_level, _url, _user_name, _channel, **_option)
            tmp_handlers.setFormatter(slack_formatter)

            if tmp_handlers.slack_filter:
                tmp_filter = SlackLogFilter()
                tmp_handlers.addFilter(tmp_filter)

            handlers[handle_name] = tmp_handlers

        for slacker_name, slacker_info in slack_list.get("loggers", {}).items():
            tmp_logger = logging.getLogger(slacker_name)

            for slack_handler in slacker_info["handlers"]:
                if slack_handler in handlers.keys():
                    tmp_logger.addHandler(handlers[slack_handler])


class SlackHandler(HTTPHandler):
    def __init__(self, level, webhook_url, user_name, channel, **kwargs):
        o = urlparse(webhook_url)
        is_secure = o.scheme == "https"
        HTTPHandler.__init__(self, o.netloc, o.path, method="POST", secure=is_secure)

        self.setLevel(level)
        self._user_name = user_name
        self._channel = channel

        self._icon_url = kwargs.get("icon_url")
        self._icon_emoji = kwargs.get("icon_emoji")
        self._level_emoji = kwargs.get("level_emoji")
        self._slack_filter = kwargs.get("slack_filter")
        self._mention = kwargs.get("mention") and kwargs.get("mention").lstrip("@")

        # NOTE: 커스텀 변수
        self._brand_name = ""
        self._emoji = ""

    @property
    def slack_filter(self):
        return self._slack_filter

    def mapLogRecord(self, record: logging.LogRecord) -> Dict[str, str | Dict]:
        text_format: str | Dict = self.format(record)
        self._emoji: str = ":pencil2:"
        self._brand_name: str = getattr(record, "brand_name", None)

        if dict == type(text_format):
            text = text_format.get("text")
        else:
            text = text_format

        if isinstance(self.formatter, SlackFormatter):
            text_format = self.set_attachments(text_format, text)
            payload = {
                "attachments": [
                    text_format,
                ],
            }
            if self._mention:
                payload["text"] = "<@{0}>".format(self._mention)
        else:
            if self._mention:
                text = "<@{0}> {1}".format(self._mention, text)
            payload = {
                "text": text,
            }

        if self._user_name:
            payload["username"] = self._user_name

        if self._icon_url:
            payload["icon_url"] = self._icon_url

        if self._icon_emoji:
            payload["icon_emoji"] = self._icon_emoji

        if self._channel:
            payload["channel"] = self._channel

        ret = {
            "payload": json.dumps(payload),
        }
        return ret

    def set_attachments(self, record: Dict[str, Any], message: str) -> Dict[str, Any]:
        record["text"] = message
        record["author_name"] = f"{self._emoji} {record.get('author_name')}"
        record["title"] = f"{self._brand_name.upper()}"

        return record


class SlackFormatter(logging.Formatter):
    def format(self, record):
        ret = {}
        if record.levelname == "INFO":
            ret["color"] = "good"
        elif record.levelname == "WARNING":
            ret["color"] = "warning"
        elif record.levelname == "ERROR":
            ret["color"] = "#E91E63"
        elif record.levelname == "CRITICAL":
            ret["color"] = "danger"

        ret["author_name"] = record.levelname
        ret["title"] = record.name
        ret["ts"] = record.created
        ret["text"] = super().format(record)
        ret["footer"] = "daily report process"
        ret["footer_icon"] = "https://platform.slack-edge.com/img/default_application_icon.png"
        return ret


class SlackLogFilter(logging.Filter):
    """
    Logging filter to decide when logging to Slack is requested, using
    the `extra` kwargs:

        `logger.info("...", extra={'notify_slack': True, brand_name: ""})`
    """

    def filter(self, record):
        return getattr(record, "notify_slack", False)
