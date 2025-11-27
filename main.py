**main.py**
```python
import logging
from logging.handlers import RotatingFileHandler
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import requests
from crawler_utils import get_all_website_links, is_valid_url

class WebCrawler:
    """
    A class used to crawl a website and extract all links.

    Attributes:
    ----------
    start_url : str
        The URL where the web crawler starts.
    max_depth : int
        The maximum depth the web crawler will go.
    crawled_links : set
        A set of all crawled links.
    """

    def __init__(self, start_url, max_depth):
        self.start_url = start_url
        self.max_depth = max_depth
        self.crawled_links = set()

    def crawl(self):
        """
        Start the web crawler.
        """
        self._crawl(self.start_url, 0)

    def _crawl(self, url, depth):
        """
        Crawl the website recursively.

        Parameters:
        ----------
        url : str
            The current URL.
        depth : int
            The current depth.
        """
        try:
            if depth > self.max_depth:
                return

            logging.info(f"Crawling {url} at depth {depth}")

            response = requests.get(url)
            response.raise_for_status()  # Raise an exception for HTTP errors

            soup = BeautifulSoup(response.text, 'html.parser')
            links = get_all_website_links(soup, url)

            for link in links:
                if link not in self.crawled_links and is_valid_url(link):
                    self.crawled_links.add(link)
                    self._crawl(link, depth + 1)

        except requests.exceptions.RequestException as e:
            logging.error(f"Request error: {e}")
        except Exception as e:
            logging.error(f"Error: {e}")


def main():
    # Set up logging
    logging.basicConfig(
        handlers=[RotatingFileHandler('crawler.log', maxBytes=100000, backupCount=10)],
        format='%(asctime)s %(levelname)s: %(message)s',
        level=logging.INFO
    )

    start_url = "http://example.com"
    max_depth = 2

    crawler = WebCrawler(start_url, max_depth)
    crawler.crawl()

    # Print all crawled links
    for link in crawler.crawled_links:
        print(link)


if __name__ == "__main__":
    main()
```

**crawler_utils.py**
```python
from urllib.parse import urljoin, urlparse

def get_all_website_links(soup, url):
    """
    Get all links from a webpage.

    Parameters:
    ----------
    soup : BeautifulSoup
        The BeautifulSoup object of the webpage.
    url : str
        The URL of the webpage.

    Returns:
    -------
    list
        A list of all links on the webpage.
    """
    links = []
    for link in soup.find_all('a'):
        href = link.get('href')
        if href:
            # Convert relative URLs to absolute URLs
            absolute_url = urljoin(url, href)
            links.append(absolute_url)
    return links


def is_valid_url(url):
    """
    Check if a URL is valid.

    Parameters:
    ----------
    url : str
        The URL to check.

    Returns:
    -------
    bool
        True if the URL is valid, False otherwise.
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False