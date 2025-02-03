#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Main entry point for the music downloader application."""

from itunes import get_itunes_metadata
from youtube import download_youtube_audio
from tagger import apply_metadata


def main():
    """Main function to run the music downloader."""
    # Get song name
    search_query = input("Enter song name to search: ")

    # Get iTunes metadata
    song_data = get_itunes_metadata(search_query)
    if song_data is None:
        return
    print(f"\nSelected: {song_data['trackName']} by {song_data['artistName']}\n")

    # Get YouTube URL
    youtube_url = input("Enter YouTube URL for this song: ")

    # Download audio
    try:
        mp3_path = download_youtube_audio(song_data, youtube_url)
    except Exception as e:
        print(f"\nFailed to download: {str(e)}")
        return

    # Apply metadata
    print("\nApplying metadata...")
    apply_metadata(mp3_path, song_data)
    print(f"\nDone! File saved to: {mp3_path}")


if __name__ == "__main__":
    main()
