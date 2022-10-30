#!/usr/bin/env python3
import logging
import os

from logging.handlers import RotatingFileHandler
from dotenv import load_dotenv

from reddit import Reddit, RedditPost

MAX_LOG_SIZE = 5 * 1024 * 1024    # 5 MB

class ConfigError(Exception):
    pass

def main():
    # Log the script start.
    logger.info("Starting Reddit To Tumblr.")

    # Get the authentication fields.
    reddit_client = os.environ.get("reddit_client_id")
    reddit_secret = os.environ.get("reddit_client_secret")
    reddit_user = os.environ.get("reddit_username")
    reddit_password = os.environ.get("reddit_password")
    reddit_sub = os.environ.get("reddit_sub")

    # Validate everything is in place.
    if not reddit_client or not reddit_secret or not reddit_user or not reddit_password or not reddit_sub:
        logger.error("Missing Reddit configuration information!")
        raise ConfigError
    logger.info(f"Targetting sub-Reddit: {reddit_sub}")

    # Instantiate a Reddit client.
    reddit_client = Reddit(
            client_id=reddit_client,
            client_secret=reddit_secret,
            username=reddit_user,
            password=reddit_password,
            target_sub=reddit_sub)

    top_details = reddit_client.get_top()
    logger.info(f"Found top post: {top_details}")

if __name__ == "__main__":
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    log_format = logging.Formatter('%(asctime)s - [%(filename)s] - %(levelname)s - %(message)s')
    file_handler = RotatingFileHandler(
            "/tmp/toptotumblr.log",
            mode="a+",
            maxBytes=MAX_LOG_SIZE,
            encoding=None,
            delay=False)
    file_handler.setFormatter(log_format)
    logger.addHandler(file_handler)

    # Load the environment variables.
    load_dotenv()

    # Call the entrypoint function.
    main()

