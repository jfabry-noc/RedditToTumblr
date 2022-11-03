#!/usr/bin/env python3
import logging
import os

from logging.handlers import RotatingFileHandler
from dotenv import load_dotenv

from reddit import Reddit
from tumblr import Tumblr

MAX_LOG_SIZE = 5 * 1024 * 1024    # 5 MB

class ConfigError(Exception):
    pass

def main():
    # Log the script start.
    logger.info("Starting Reddit To Tumblr.")

    # Get the Reddit authentication fields.
    reddit_client = os.environ.get("reddit_client_id")
    reddit_secret = os.environ.get("reddit_client_secret")
    reddit_user = os.environ.get("reddit_username")
    reddit_password = os.environ.get("reddit_password")
    reddit_sub = os.environ.get("reddit_sub")

    # Validate everything is in place for Reddit.
    if not reddit_client or not reddit_secret or not reddit_user or not reddit_password or not reddit_sub:
        logger.error("Missing Reddit configuration information!")
        raise ConfigError
    logger.info(f"Targetting sub-Reddit: {reddit_sub}")

    # Get the Tumblr authentication fields.
    tumblr_key = os.environ.get("tumblr_key")
    tumblr_secret = os.environ.get("tumblr_secret")
    tumblr_oauth_token = os.environ.get("tumblr_oauth_token")
    tumblr_oauth_secret = os.environ.get("tumblr_oauth_secret")
    tumblr_instance = os.environ.get("tumblr_blog")

    # Validate everything is in place for Tumblr.
    if not tumblr_key or not tumblr_secret or not tumblr_oauth_token or not tumblr_oauth_secret or not tumblr_instance:
        logger.error("Missing Tumblr configuration information!")
        raise ConfigError
    logger.info(f"Targetting Tumblr blog: {tumblr_instance}")

    # Instantiate a Reddit client.
    reddit_client = Reddit(
            client_id=reddit_client,
            client_secret=reddit_secret,
            username=reddit_user,
            password=reddit_password,
            target_sub=reddit_sub)

    top_details = reddit_client.get_top()
    logger.info(f"Found top post: {top_details}")

    # Create the Tumblr client.
    tumblr_client = Tumblr(
            consumer_key=tumblr_key,
            consumer_secret=tumblr_secret,
            oauth_key=tumblr_oauth_token,
            oauth_secret=tumblr_oauth_secret,
            instance=tumblr_instance
            )

    tumblr_client.new_photo(
            image_url=top_details.url,
            og_link=top_details.permalink,
            title=top_details.title,
            author_name=top_details.author_name
            )

    logger.info("Script completed. Daily post successful.")

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

