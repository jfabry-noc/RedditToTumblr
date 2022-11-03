# https://github.com/reddit-archive/reddit/wiki/OAuth2
import logging
import requests
import requests.auth

from dataclasses import dataclass


logger = logging.getLogger()

IMAGES = [
            "ai",
            "arw",
            "bmp",
            "dip",
            "eps",
            "gif",
            "heic",
            "heif",
            "jfi",
            "jfif",
            "jif",
            "jpe",
            "jpeg",
            "jpg",
            "nrw",
            "png",
            "raw",
            "svg",
            "svgz",
            "tif",
            "tiff",
            "webp"
            ]

class RedditAuthError(Exception):
    pass
class RedditResponseError(Exception):
    pass

@dataclass
class RedditPost:
    """
    Data structure representing an individual post, containing:

    Attributes:
        url (str): The URL to the post target.
        title (str): Post title.
        permalink (str): Permalink to the post on Reddit.
        author_name (str): Username of the author.
        author_url (str): URL to the author's Reddit profile.
    """
    url: str
    title: str
    permalink: str
    author_name: str
    author_url: str

class Reddit:
    def __init__(self, client_id: str, client_secret: str, username: str, password: str, target_sub: str) -> None:
        """
        Client for accessing Reddit content. Designed to only account for
        script-based listings rather than leveraging true OAuth. Most of this
        is unnecessary since the content can be gathered publicly and is
        unlikely to run into any sort of rate-limiting.

        Attributes:
            target_sub (str): The sub-Reddit to target.
            access_token (str): Access token after authenticating.
        """
        self.target_sub = target_sub

        self.access_token = self.get_access_token(
                client_id=client_id,
                client_secret=client_secret,
                username=username,
                password=password
                )

    def get_access_token(self, client_id: str, client_secret: str, username: str, password: str) -> None:
        """
        Gets an access token for subsequent Reddit requests.

        Args:
            client_id (str): API client ID.
            client_secret (str): Secret for the above client.
            username (str): Reddit account username.
            password (str): Password for the above user.
        """
        client_auth = requests.auth.HTTPBasicAuth(
                username=client_id,
                password=client_secret)
        user_data = {
                "grant_type": "password",
                "username": username,
                "password": password
                }

        headers = {"User-Agent": "TopToTumblr/0.1 by GreedyLeek"}
        try:
            response = requests.post(
                    url="https://www.reddit.com/api/v1/access_token",
                    auth=client_auth,
                    data=user_data,
                    headers=headers
                    )
        except Exception as e:
            logger.error(f"Failed to get a Reddit token with error: {e}")
            raise RedditAuthError

        if response.status_code != 200:
            logger.error(f"Failed to authenticate with code: {response.status_code}")
            raise RedditAuthError

        try:
            return response.json()['access_token']
        except KeyError:
            logger.error(f"Authentication response was successful, but no access token was returned! Response: {response.json()}")
            raise RedditAuthError

    def get_top(self) -> RedditPost:
        """
        Gets the top post for the past 1 day from the sub associated with this
        instance of the Reddit client.

        Returns:
            dict: Containing the image URL, title, author, and Reddit URL.
        """
        url = f"https://reddit.com/r/{self.target_sub}/top/.json?t=day&limit=1"
        logger.debug(f"Fetching top post using URL: {url}")

        new_headers = {
                "User-Agent": "TopToTumblr/0.1 by GreedyLeek",
                "Authorization": f"bearer {self.access_token}"}

        try:
            top_post = requests.get(
                url=url,
                headers=new_headers)
        except Exception as e:
            logger.error(f"Failed to retrieve top posts from {self.target_sub} with error: {e}")
            raise RedditResponseError

        if top_post.status_code == 200:
            try:
                post_dict = top_post.json()
                post_details = RedditPost(
                        url=post_dict["data"]["children"][0]["data"]["url"],
                        title=post_dict["data"]["children"][0]["data"]["title"],
                        permalink=f"https://reddit.com{post_dict['data']['children'][0]['data']['permalink']}",
                        author_name=post_dict["data"]["children"][0]["data"]["author"],
                        author_url=f"https://reddit.com/u/{post_dict['data']['children'][0]['data']['author']}")

                # Validate the URL is an image.
                if not post_details.url.split(".")[-1].lower() in IMAGES:
                    logger.error(f"Top post's target URL has file format of: {post_details.url.split('.')[-1].lower()}")
                    raise RedditResponseError
                return post_details
            except Exception as e:
                logger.error(f"Failed to get the details of the top post with error: {e}")
                raise RedditResponseError
        else:
            logger.error(f"Received response error: {top_post.status_code}")
            raise RedditResponseError

