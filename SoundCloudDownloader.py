# Project Started: May 31, 2016

# Modules:
import webbrowser # This module can control the browser
import json # Json encoder/decoder
from bs4 import BeautifulSoup # Module to sort through HTML
import lxml # Module to prepare html for BeautifulSoup
import urllib2 # Gets html
import sys # Allow more control over printing
import string # More ways to manipulate strings
import unidecode # Decodes weird characters
import youtube_dl # For downloading YouTube (and Soundcloud) videos/audio
import eyed3 # For editing ID3 tags for mp3 file
import os # More control over Mac file system

# Prompt user for SoundCloud link
soundCloudLink = raw_input("SoundCloud Link: ") # Prompt for link (inputs as String type)

ydl_opts = { # Set options
    'format': 'bestaudio/best',
    # 'outtmpl': u'%(title)s-%(id)s.%(ext)s',
    'outtmpl': "~/Desktop/song.mp3",
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192' # 128, 160, 192, 210, 256
    }],
}

with youtube_dl.YoutubeDL(ydl_opts) as ydl:
    ydl.download([soundCloudLink]) # Download the song


# *******************   Update ID3 Tags   *******************

mp3Path = os.path.expanduser("~/Desktop/" + fileName + ".mp3")

audiofile = eyed3.load(mp3Path) # Load file

# Set data
audiofile.tag.title = "Name of Song"

audiofile.tag.save(); # Save meta data
