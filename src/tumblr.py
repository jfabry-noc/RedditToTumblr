import requests
import logging

from requests_oauthlib import OAuth1



logger = logging.getLogger()

class TumblrError(Exception):
    pass

class Tumblr:
    def __init__(self, consumer_key: str, consumer_secret: str, oauth_key: str, oauth_secret: str, instance: str) -> None:
        """
        Class to manage communication with the Tumblr API. Passed values are
        self-explanatory from the registration process with Tumblr.

        Attributes:
            instance (str): The Tumblr instance to target.
            oauth_package (OAuth1): OAuth1 bundle with the API information.
        """
        self.instance = instance
        self.oauth_package = OAuth1(
            client_key=consumer_key,
            client_secret=consumer_secret,
            resource_owner_key=oauth_key,
            resource_owner_secret=oauth_secret)

    def new_photo(self, image_url: str, og_link: str, title: str, author_name: str) -> None:
        """
        Creates a new photo post.

        Args:
            image_url (str): URL to the image.
            og_link (str): Link to the original post on Reddit.
            title (str): Title from the original Reddit post.
            author_name (str): Name of the original post's author on Reddit.
        """
        image_params = {
            "state": "published",
            "type": "photo",
            "source": image_url,
            "caption": f"{title}, from <a href=\"{og_link}\">/u/{author_name}</a>."
            }
        retry_counter = 3
        attempts = 0
        while attempts < retry_counter:
            attempts += 1
            try:
                image_response = requests.post(
                    url=f"https://api.tumblr.com/v2/blog/{self.instance}/post",
                    auth=self.oauth_package,
                    data=image_params
                    )
            except Exception as e:
                logger.error(f"Failed to make the post with error: {e}")
                continue

            if image_response.status_code == 201:
                try:
                    logger.info(f"Posted successfully with message: {image_response.json()['response']['display_text']}")
                    break
                except Exception as e:
                    logger.error(f"Image posted successfully, but failed to process response with error: {e}")
                    continue
            else:
                logger.error(f"Image not posted successfully. Response code was: {image_response.status_code}")
                continue

        # There's a problem if we made it this far without success.
        logger.error("Unable to post to Tumblr.")
        raise TumblrError

