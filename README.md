# Music Downloader

A Python tool to download music from YouTube and automatically tag it with metadata from iTunes.

***This is not intended for illegal use***

## Features

- Search and fetch song metadata from iTunes Store API
- Interactive song selection from search results
- Download high-quality audio from YouTube videos
- Automatically apply metadata to MP3 files:
  - Song title
  - Artist name
  - Album name
  - Genre
  - Album artwork

## Installation

1. Clone the repository
2. Install the required dependencies:

```bash
pip install requests beautifulsoup4 yt-dlp eyed3 inquirer lxml
```

## Usage

1. Run the main script:

```bash
python main.py
```

2. Enter the song name when prompted. The tool will search iTunes and display matching results.

3. Select the correct song from the list using arrow keys and press Enter.

4. Enter the YouTube URL for the song.

5. The tool will:
   - Download the audio from YouTube
   - Convert it to MP3 format
   - Apply the iTunes metadata
   - Save the file to your Desktop

The final file will be named in the format: `ArtistName - SongTitle.mp3`

## Notes

- The tool saves downloaded music to the Desktop by default
- Make sure you have a stable internet connection for metadata fetching and downloading
- Only use this tool for content you have the right to download

## Development

This project was created as a Python learning exercise, exploring:

- Working with APIs (iTunes Store API)
- Web scraping
- Audio file manipulation
- Command-line interfaces
- Python package management

I wanted to practice my Python skills and decided this would be a cool project to take on.

I have traditionally worked in JavaScript, but I wanted to expand my programming skills.

I was able to learn about APIs, Web Scraping, lots of modules, etc.
