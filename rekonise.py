"""
rekonise_utils.py - Utility functions for interacting with the Rekonise API.

This module provides utility functions for expanding shortened URLs, removing 
domain names from URLs, fetching download URLs from the Rekonise API, and reading links from a file.

Functions:
    expand_short_url(short_url: str) -> str:
        Expand a shortened URL to its full form.

    remove_domain(url: str) -> str:
        Remove a specific domain from a URL.

    get_download_url(plug_id: str) -> str:
        Get the download URL associated with a plug from the Rekonise API.

    read_links_from_file(file_path: str) -> List[Dict[str, str]]:
        Read links from a file and construct a list of dictionaries.

    process_link(link: Dict[str, str]) -> Dict[str, str]:
        Process a link by expanding its URL, removing the domain, and retrieving the download URL.
"""

from typing import List, Dict
from concurrent.futures import ThreadPoolExecutor, as_completed
import os
import requests
from tqdm import tqdm

REKONISE_DOMAIN: str = "https://rekonise.com/"
UNLOCK_URL_TEMPLATE: str = "https://api.rekonise.com/social-unlocks/{}/unlock"
MAX_WORKERS: int = int(0.8 * os.cpu_count())


def expand_short_url(short_url: str) -> str:
    """
    Expand a shortened URL to its full form.

    Args:
        short_url (str): The shortened URL to be expanded.

    Returns:
        str: The expanded URL.

    Raises:
        requests.exceptions.RequestException: If an error occurs while expanding the URL.
    """
    response = requests.head(short_url, allow_redirects=True, timeout=30)
    return response.url


def remove_domain(url: str) -> str:
    """
    Remove a specific domain from a URL.

    Args:
        url (str): The URL from which the domain will be removed.

    Returns:
        str: The URL with the specified domain removed.
    """
    return str.replace(url, REKONISE_DOMAIN, "")


def get_download_url(plug_id: str) -> str:
    """
    Get the download URL associated with a plug from the Rekonise API.

    Args:
        plug_id (str): The plug identifier.

    Returns:
        str: The download URL retrieved from the Rekonise API.

    Raises:
        requests.exceptions.RequestException: If an error occurs while fetching the download URL.
    """
    unlock_url = UNLOCK_URL_TEMPLATE.format(plug_id)
    return requests.get(unlock_url, timeout=30).json()["url"]


def read_links_from_file(file_path: str) -> List[Dict[str, str]]:
    """
    Read links from a file and construct a list of dictionaries.

    Each line in the file should contain a name and a URL separated by a colon and a space (: ).
    The function parses each non-blank line that contains a link and constructs a dictionary with
    keys 'name', 'url', and 'download_url', where 'name' corresponds to the name extracted from the
    file, 'url' corresponds to the URL extracted from the file, and 'download_url' is initially set
    to an empty string.

    Args:
        file_path (str): The path to the file containing the links.

    Returns:
        list: A list of dictionaries, where each dictionary represents a link with keys 'name',
        'url', and 'download_url'.

    Note:
        Specify the appropriate encoding if the file contains non-ASCII characters, e.g., 'utf-8'.
    """
    links = []
    with open(file_path, "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if not line or ": " not in line:
                continue  # Skip blank lines or lines without a link
            name, url = line.split(": ")
            links.append({"name": name.strip(), "url": url.strip(), "download_url": ""})
    return links


def process_link(link: Dict[str, str]) -> Dict[str, str]:
    """
    Process a link by expanding its URL, removing the domain, and retrieving the download URL.

    Args:
        link (dict): A dictionary representing a link with keys 'name' and 'url'.

    Returns:
        dict: The processed link dictionary with an additional key 'download_url' containing the
        download URL.

    Raises:
        requests.exceptions.RequestException: If an error occurs while processing the link.
    """
    expanded_url = expand_short_url(link["url"])
    plug = remove_domain(expanded_url)
    download_url = get_download_url(plug)
    link["download_url"] = download_url
    return link


def print_links(links: List[Dict[str, str]]) -> None:
    """
    Print the names and download URLs of links in a list of dictionaries.

    Args:
        links (List[Dict[str, str]]): A list of dictionaries representing links,
            where each dictionary contains 'name' and 'download_url' keys.

    Returns:
        None

    Example:
        >>> links = [{'name': 'Link 1', 'download_url': 'http://example.com/link1'},
                    {'name': 'Link 2', 'download_url': 'http://example.com/link2'}]
        >>> print_links(links)
        Link 1: http://example.com/link1
        Link 2: http://example.com/link2
    """
    for link in links:
        print(f"{link['name']}: {link['download_url']}")


def main(file=None, link=None) -> None:
    """
    Main function for processing links using the Rekonise API.

    This function accepts either a file name containing links or an individual link,
    processes each link, and prints the processed links.

    Args:
        file (str): Input file name containing links.
        link (str): Individual link to process.

    Returns:
        None
    """
    if link:
        # Individual link provided
        link_dict = {"name": "Individual Link", "url": link, "download_url": ""}
        link_dict = process_link(link_dict)
        print_links([link_dict])
    elif file:
        # File name provided
        links = read_links_from_file(file)
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = [executor.submit(process_link, link) for link in links]

            for future in tqdm(
                as_completed(futures), total=len(links), desc="Processing links"
            ):
                future.result()

        processed_links = [future.result() for future in futures]
        print_links(processed_links)
