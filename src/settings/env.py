from environs import env

env.read_env()

SLACK_HOOK_URL = env.str("SLACK_HOOK_URL")
CHANNEL = env.str("CHANNEL")
BOT_NAME = env.str("BOT_NAME")