"""MP3 tagging functionality."""

import requests
import eyed3


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
