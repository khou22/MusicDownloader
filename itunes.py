"""iTunes metadata retrieval functionality."""

import json
from bs4 import BeautifulSoup
from urllib.request import urlopen
import inquirer


def get_itunes_metadata(search_query: str, num_results: int = 5) -> dict:
    """
    Search iTunes for song metadata and let user select the correct match.

    Args:
        search_query (str): The song to search for
        num_results (int): Number of results to show user

    Returns:
        dict: iTunes metadata for the selected song
    """
    # Search iTunes Store API
    base_url = "https://itunes.apple.com/search?"
    search_keys = [
        ["term", search_query],
        ["country", "US"],
        ["media", "music"],
        ["entity", "song"],
        ["limit", "50"],
        ["lang", "en_us"],
        ["explicit", "yes"],
    ]

    final_url = base_url
    for i, (key, value) in enumerate(search_keys):
        criteria = str(value).replace(" ", "%20")
        append_str = f"{key}={criteria}"
        if i < (len(search_keys) - 1):
            append_str += "&"
        final_url += append_str

    # Get iTunes data
    response = urlopen(final_url)
    html = response.read()
    soup = BeautifulSoup(html, "lxml")
    raw_json = soup.find("p").text.strip()

    # Parse results
    itunes_obj = json.loads(raw_json)
    results = itunes_obj["results"]

    if not results:
        print("No results found.")
        return None

    # Create choices for inquirer
    choices = []
    for i in range(min(num_results, len(results))):
        song = results[i]
        display_name = f"{song['trackName']} - by {song['artistName']} (Album: {song['collectionName']}, Genre: {song['primaryGenreName']})"
        choices.append((display_name, i))

    # Create and show selection prompt
    questions = [
        inquirer.List(
            "song", message="Select the correct song", choices=choices, carousel=True
        )
    ]

    # Get user selection
    answers = inquirer.prompt(questions)
    if not answers:
        print("Selection cancelled.")
        return None

    return results[answers["song"]]
