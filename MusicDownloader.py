#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
MusicDownloader: A tool to download and tag music from YouTube using iTunes metadata.
Started: February 7, 2016
"""

import requests
from io import BytesIO
import json
from bs4 import BeautifulSoup
from urllib.request import urlopen
import yt_dlp as youtube_dl
import eyed3
import os


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

    # Show results to user
    print("\n*********** Found iTunes data ***********\n")
    for i in range(min(num_results, len(results))):
        print(f"({i}) Track Name: {results[i]['trackName']}")
        print(f"    Artist: {results[i]['artistName']}")
        print(f"    Album: {results[i]['collectionName']}")
        print(f"    Genre: {results[i]['primaryGenreName']}\n")

    # Get user selection
    selection = int(
        input("Which song is the one you were looking for? Type the index: ")
    )
    return results[selection]


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
        "quiet": False,
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([youtube_url])

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
    print(f"Applying album artwork from: {image_url}")
    response = requests.get(image_url)
    audiofile.tag.images.set(
        3, BytesIO(response.content).read(), "image/jpeg", "Album Artwork"
    )

    audiofile.tag.save()
    print("\nUpdated ID3 Tags")


def main():
    """Main function to orchestrate the music download process."""
    # Get song search from user
    search_query = input("Search for song: ").strip()

    # Get iTunes metadata
    song_data = get_itunes_metadata(search_query)
    print(f"\nSelected: {song_data['trackName']} by {song_data['artistName']}\n")

    # Get YouTube URL
    youtube_url = input("Enter YouTube URL for the song: ")

    # Download and process
    mp3_path = download_youtube_audio(song_data, youtube_url)
    apply_metadata(mp3_path, song_data)

    print("\n**************   Complete   **************")


if __name__ == "__main__":
    main()
