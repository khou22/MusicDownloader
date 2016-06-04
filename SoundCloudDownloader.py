# Project Started: May 31, 2016

# Modules:
import webbrowser  # This module can control the browser
import json  # Json encoder/decoder
from bs4 import BeautifulSoup  # Module to sort through HTML
import lxml  # Module to prepare html for BeautifulSoup
import urllib2  # Gets html
import sys  # Allow more control over printing
import string  # More ways to manipulate strings
import unidecode  # Decodes weird characters
import youtube_dl  # For downloading YouTube (and Soundcloud) videos/audio
import eyed3  # For editing ID3 tags for mp3 file
import os  # More control over Mac file system
import re  # More functions for manipulating string types

# iTunes API Documentation: http://www.apple.com/itunes/affiliates/resources/documentation/itunes-store-web-service-search-api.html

# Prompt user for SoundCloud link
# soundCloudLink = raw_input("SoundCloud Link: ")  # Prompt for link (inputs as String type)
# soundCloudLink = "https://soundcloud.com/donnietrumpet/the-first-time"  # For testing
soundCloudLink = "https://soundcloud.com/descentintonice/justin-timberlake-cant-stop-the-feeling"  # For testing name of song in listed track name

# *******************   Get Track Data   *******************
response = urllib2.urlopen(soundCloudLink)  #Get HTML source code
html = response.read()  #HTML source code
soup = BeautifulSoup(html, "lxml")  # Using lxml parser

# Initialize arrays
potentialArtists = []
potentialTrackNames = []

listedTrackName = ""  # What the song is listed as (could include name of artist)

# Function for adding data to potential fields
def newPotentialData(type, data):
    print "Potential %s: %s" % (type, data)  # Feedback
    if type is "artist":
        potentialArtists.append(data)
    if type is "trackName":
        potentialTrackNames.append(data)


# Data from page name
pageName = soup.title.string  # Get title of web page
if (len(re.split("by", pageName)) > 2):  # If more than one "by" in title
    print "Artist name likely in track title"
else: # If no "by" in song title
    songData = re.split("by", pageName)  # Split track and artist
    listedTrackName = songData[0].strip()
    newPotentialData("trackName", listedTrackName)  # Trim whitespace and store
    cropArtist = songData[1][0:songData[1].index("| Free Listening on SoundCloud")]  # Crop the string to only have artist name
    newPotentialData("artist", cropArtist.strip())  # Trim whitespace and store

# Data from track name

# Usually artist and track name is split up by these
cutoffKeys = [" - ", " ~ "]
for i in range(0, len(cutoffKeys)):  # Cycle through all cutoff keys
    splitName = re.split(cutoffKeys[i], listedTrackName)  # Split the track name
    if len(splitName) > 1:  # If contains one of the keys
        print splitName
        for j in range(0, len(splitName)):  # Check both sides of the cutoff to determine which is artist and which is name of song
            searchQuery = splitName[j]  # Current search key

            # Search for artist in iTunes Store
            baseURL = "https://itunes.apple.com/search?"
            searchKeys = [
                ["term", searchQuery],
                ["country", "US"],
                ["media", "music"],
                ["attribute", "artistTerm"],
                ["entity", "song"],
                ["limit", "50"],
                ["lang", "en_us"],
                ["explicit", "yes"]
            ]
            finalURL = baseURL
            for i in range(0, len(searchKeys)): # len() returns length of a variable
                # print "Term: %d" % (i)
                currentKey = searchKeys[i]
                criteria = str(currentKey[1])  #Make sure it's a string
                criteria = criteria.replace(" ", "%20")  # %20 represents a space
                appendStr = currentKey[0] + "=" + criteria  # Build url
                # print(appendStr)
                if i < (len(searchKeys) - 1):
                    appendStr += "&"
                finalURL += appendStr

            print("Final URL: " + finalURL)  # Debugging

# *******************   Download Track   *******************
ydl_opts = {  # Set options
    'format': 'bestaudio/best',
    # 'outtmpl': u'%(title)s-%(id)s.%(ext)s',
    'outtmpl': "~/Desktop/song.mp3",
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192'  # 128, 160, 192, 210, 256
    }],
}

# with youtube_dl.YoutubeDL(ydl_opts) as ydl:
#     ydl.download([soundCloudLink])  # Download the song

# *******************   Update ID3 Tags   *******************
# fileName = "song"
# mp3Path = os.path.expanduser("~/Desktop/" + fileName + ".mp3")
#
# audiofile = eyed3.load(mp3Path)  # Load file
#
# # Set data
# audiofile.tag.title = "Name of Song"
#
# audiofile.tag.save();  # Save meta data
