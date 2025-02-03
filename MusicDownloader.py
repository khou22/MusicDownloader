#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
MusicDownloader: A tool to download and tag music from YouTube using iTunes metadata.
Started: February 7, 2016
"""

import requests
import json
from bs4 import BeautifulSoup
from urllib.request import urlopen
import yt_dlp as youtube_dl
import eyed3
import os
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


def download_youtube_audio(
    song_data: dict, youtube_url: str, file_path: str = "~/Desktop/"
) -> str:
    """
    Download YouTube video as MP3 using specified quality settings.

    Args:
        song_data (dict): iTunes metadata for the song
        youtube_url (str): YouTube URL to download from
        file_path (str): Directory to save the MP3 file

    Returns:
        str: Path to the downloaded MP3 file
    """
    file_name = f"{song_data['artistName']} - {song_data['trackName']}"

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": file_path + file_name + ".%(ext)s",
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
        # Add cookies and headers to mimic browser
        "http_headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-us,en;q=0.5",
            "Sec-Fetch-Mode": "navigate",
        },
        # Add options to bypass restrictions
        "quiet": False,
        "no_warnings": True,
        "nocheckcertificate": True,
        "prefer_insecure": True,
        "geo_bypass": True,
        "geo_bypass_country": "US",
        "extractor_retries": 3,
        "file_access_retries": 3,
        "fragment_retries": 3,
        "skip_download": False,
        "rm_cachedir": True,
        "force_generic_extractor": False,
        "sleep_interval": 2,  # Add delay between retries
        "max_sleep_interval": 5,
    }

    max_retries = 3
    retry_count = 0
    formats_to_try = ["bestaudio/best", "worstaudio/worst", "251/250/249"]

    while retry_count < max_retries:
        try:
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                print(f"\nAttempt {retry_count + 1} of {max_retries}")
                ydl.download([youtube_url])
                return os.path.expanduser(file_path + file_name + ".mp3")
        except Exception as e:
            print(f"\nError on attempt {retry_count + 1}: {str(e)}")
            retry_count += 1
            if retry_count < max_retries:
                print(f"Retrying with different format...")
                # Try different format on each retry
                ydl_opts["format"] = formats_to_try[retry_count % len(formats_to_try)]
                # Add some delay between retries
                import time

                time.sleep(2 * retry_count)
            else:
                print("\nFailed to download after all attempts.")
                raise

    return os.path.expanduser(file_path + file_name + ".mp3")


def apply_metadata(mp3_path: str, song_data: dict) -> None:
    """
    Apply iTunes metadata to the MP3 file including artwork.

    Args:
        mp3_path (str): Path to the MP3 file
        song_data (dict): iTunes metadata to apply
    """
    year = int(str(song_data["releaseDate"])[:4])

    audiofile = eyed3.load(mp3_path)
    audiofile.tag.title = song_data["trackName"]
    audiofile.tag.artist = song_data["artistName"]
    audiofile.tag.album = song_data["collectionName"]
    audiofile.tag.album_artist = song_data["artistName"]
    audiofile.tag.track_num = (song_data["trackNumber"], song_data["trackCount"])
    audiofile.tag.disc_num = (song_data["discNumber"], song_data["discCount"])
    audiofile.tag.genre = song_data["primaryGenreName"]

    # Set all date tags
    for date_tag in [
        "release_date",
        "orig_release_date",
        "recording_date",
        "encoding_date",
        "taggin_date",
    ]:
        setattr(audiofile.tag, date_tag, year)

    # Add album artwork
    image_url = song_data["artworkUrl100"].replace("100x100", "500x500")
    response = requests.get(image_url)
    if response.status_code == 200:
        # Set the image in the MP3
        audiofile.tag.images.set(3, response.content, "image/jpeg")
    else:
        print(f"Failed to download artwork: HTTP {response.status_code}")

    audiofile.tag.save(version=(2, 3, 0))


def main():
    """Main function to orchestrate the music download process."""
    # Get song search from user
    search_query = input("Search for song: ").strip()

    # Get iTunes metadata
    song_data = get_itunes_metadata(search_query)
    if song_data is None:
        return
    print(f"\nSelected: {song_data['trackName']} by {song_data['artistName']}\n")

    # Get YouTube URL
    youtube_url = input("Enter YouTube URL for the song: ")

    # Download and process
    mp3_path = download_youtube_audio(song_data, youtube_url)
    apply_metadata(mp3_path, song_data)

    print("\n**************   Complete   **************")


if __name__ == "__main__":
    main()
