"""YouTube download functionality."""

import os
import time
import yt_dlp as youtube_dl


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
                time.sleep(2 * retry_count)
            else:
                print("\nFailed to download after all attempts.")
                raise

    return os.path.expanduser(file_path + file_name + ".mp3")
