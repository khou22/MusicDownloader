# Project Started: May 31, 2016

# Modules:
import webbrowser  # This module can control the browser
import json  # Json encoder/decoder
from bs4 import BeautifulSoup  # Module to sort through HTML
import lxml  # Module to prepare html for BeautifulSoup
import urllib, urllib2  # Gets html
import sys  # Allow more control over printing
import string  # More ways to manipulate strings
import unidecode  # Decodes weird characters
import youtube_dl  # For downloading YouTube (and Soundcloud) videos/audio
import eyed3  # For editing ID3 tags for mp3 file
import os  # More control over Mac file system
import re  # More functions for manipulating string types
from PIL import Image  # Python Image Library (PIL)
import requests

# iTunes API Documentation: http://www.apple.com/itunes/affiliates/resources/documentation/itunes-store-web-service-search-api.html

# Prompt user for SoundCloud link
soundCloudLink = raw_input("SoundCloud Link: ")  # Prompt for link (inputs as String type)
# soundCloudLink = "https://soundcloud.com/donnietrumpet/the-first-time"  # For testing
# soundCloudLink = "https://soundcloud.com/descentintonice/justin-timberlake-cant-stop-the-feeling"  # For testing name of song in listed track name

# *******************   Get Track Data   *******************
response = urllib2.urlopen(soundCloudLink)  # Get HTML source code
html = response.read()  # HTML source code
soup = BeautifulSoup(html, "lxml")  # Using lxml parser
# print soup.prettify()  # For debugging

# Initialize variables
trackName = ""
artist = ""
album = ""
albumArtist = ""
year = ""
imageURL = ""
trackNum = ["", ""]
discNumber = ""
discCount = ""
genre = ""

# Initialize arrays
potentialArtists = []
potentialTrackNames = []
potentialGenres = []

listedTrackName = ""  # What the song is listed as (could include name of artist)

# Function for adding data to potential fields
def newPotentialData(type, data):
    print "Potential %s: %s" % (type, data)  # Feedback
    if type is "artist":
        potentialArtists.append(data)
    if type is "trackName":
        potentialTrackNames.append(data)

# *******************   Data From Page Name   *******************
print "Getting data from page name..."
pageName = soup.title.string  # Get title of web page
if (len(re.split("by", pageName)) > 2):  # If more than one "by" in title
    print "Artist name likely in track title"
else: # If no "by" in song title
    songData = re.split("by", pageName)  # Split track and artist
    listedTrackName = songData[0].strip()
    newPotentialData("trackName", listedTrackName)  # Trim whitespace and store
    cropArtist = songData[1][0:songData[1].index("| Free Listening on SoundCloud")]  # Crop the string to only have artist name
    newPotentialData("artist", cropArtist.strip())  # Trim whitespace and store
print ""  # Line break

# *******************   Data From Source Code   *******************
print "Getting data from source code"

# Track year
allDates = soup.findAll("time")  # Find all time markers
uploadDate = allDates[0].string  # The first time tag is the upload time
year = uploadDate[0:4]  # Only include first four digits (the year)
# print year  # Feedback

# Album artwork
albumArtwork = soup.findAll("img")  # Get all images on page
for i in range(0, len(albumArtwork)):  # Cycle through all potential album artworks
    try:
        imageAlt = albumArtwork[i]['alt']
        # print imageAlt  # Should be the same as the track name
        if imageAlt is not listedTrackName:  # The alt text should be the same as the listed track name
            print albumArtwork[i]['src']
            imageURL = albumArtwork[i]['src']
        else:  # This shouldn't ever be triggered
            print imageAlt
            print listedTrackName
        break
    except KeyError:
        print "No 'alt' text detected. Cannot extract"

print ""  # Line break


# *******************   Data From Track Name   *******************
print "Getting data from track name..."

# Usually artist and track name is split up by these
cutoffKeys = [" - ", " ~ "]  # Potential deliminators
for i in range(0, len(cutoffKeys)):  # Cycle through all cutoff keys
    splitName = re.split(cutoffKeys[i], listedTrackName)  # Split the track name
    if len(splitName) > 1:  # If contains one of the keys
        print splitName
        for j in range(0, len(splitName)):  # Check both sides of the cutoff to determine which is artist and which is name of song
            searchQuery = splitName[j]  # Current search key
            print "Searching iTunes for query: %s" % searchQuery

            quoted_query = urllib.quote(searchQuery)  # Fixes random bug: http://stackoverflow.com/questions/8840303/urllib2-http-error-400-bad-request
            # Search for artist in iTunes Store
            baseURL = "https://itunes.apple.com/search?"
            searchKeys = [
                ["term", quoted_query],
                ["country", "US"],
                ["media", "music"],
                ["entity", "musicArtist"],
                ["attribute", "artistTerm"],
                ["entity", "song"],
                ["limit", "50"],
                ["lang", "en_us"],
                ["explicit", "yes"]
            ]

            finalURL = baseURL
            for k in range(0, len(searchKeys)): # len() returns length of a variable
                # print "Term: %d" % (k)
                currentKey = searchKeys[k]
                criteria = str(currentKey[1])  #Make sure it's a string
                criteria = criteria.replace(" ", "%20")  # %20 represents a space
                appendStr = currentKey[0] + "=" + criteria  # Build url
                # print(appendStr)
                if k < (len(searchKeys) - 1):
                    appendStr += "&"
                finalURL += appendStr

            # Retrieve and Save iTunes JSON Data
            print "Calling API..."  # Feedback
            # webbrowser.open(finalURL)  # For testing

            req = urllib2.Request(finalURL)
            searchResponse = urllib2.urlopen(req) # Get HTML source code
            searchResults = searchResponse.read() # HTML source code
            rawOutput = BeautifulSoup(searchResults, "lxml") # Using lxml parser
            # print(soup.prettify()) # Feedback

            rawJSON = rawOutput.find('p').text # Just the json text
            rawJSON.strip() # Trim the white space
            iTunesObj = json.loads(rawJSON) # Decode iTunes JSON Data

            numResults = iTunesObj["resultCount"]  # Get number of search results
            # print "Results: %s" % numResults  # Feedback

            if (numResults != 0):  # If there are results
                # print iTunesObj
                newPotentialData("artist", searchQuery)  # Trim whitespace and store
            else:  # if no results
                # Is probably the track name
                print "'%s' is not an artist. Likely the track name" % searchQuery  # Feedback
                newPotentialData("trackName", searchQuery)

            print ""  # Line break
    else:
        print "Doesn't contain '%s'" % cutoffKeys[i]
    print ""  # Line break


# *******************   Select Proper Track Info   *******************
# Select Track Name
print "Potential track names:"
print "0: Custom entry"  # Allow for a custom entry
for i in range(0, len(potentialTrackNames)):  # Cycle through all possibilities
    index = i + 1
    print "%s: %s" % (index, potentialTrackNames[i])
chosenIndex = input("Choose a track name: ")  # Prompt for link (inputs as String type)
if chosenIndex is 0:
    correctInput = False
    while correctInput is False:  # Cycle until correctly type in entry
        customTrackName = raw_input("Track Name: ")  # Allow for custom entry
        correct = raw_input("Done (y/n): ")  # Allow user to undo and go again
        if correct is "y":
            correctInput = True
    trackName = customTrackName  # Set final track name
else:  # If chose a suggested track name
    index = chosenIndex - 1  # Set index
    trackName = potentialTrackNames[index]  # Set final
print ""  # Line break

# Select Artist Name
print "Potential artists:"
print "0: Custom entry"  # Allow for a custom entry
for i in range(0, len(potentialArtists)):  # Cycle through all possibilities
    index = i + 1
    print "%s: %s" % (index, potentialArtists[i])
chosenIndex = input("Choose an artist: ")  # Prompt for link (inputs as String type)
if chosenIndex is 0:
    correctInput = False
    while correctInput is False:  # Cycle until correctly type in entry
        customArtist = raw_input("Artist Name: ")  # Allow for custom entry
        correct = raw_input("Done (y/n): ")  # Allow user to undo and go again
        if correct is "y":
            correctInput = True
    artist = customArtist  # Set final track name
else:  # If chose a suggested track name
    index = chosenIndex - 1  # Set index
    artist = potentialArtists[index]  # Set final
print ""  # Line break


# *******************   Get Genres   *******************
searchQuery = artist  # Search for the artist
quoted_query = urllib.quote(searchQuery)  # Fixes random bug: http://stackoverflow.com/questions/8840303/urllib2-http-error-400-bad-request
# Search for artist in iTunes Store
baseURL = "https://itunes.apple.com/search?"
searchKeys = [
    ["term", quoted_query],
    ["country", "US"],
    ["media", "music"],
    ["entity", "musicArtist"],
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

# Retrieve and Save iTunes JSON Data
print "Calling iTunes API..."  # Feedback
# webbrowser.open(finalURL)  # For testing

req = urllib2.Request(finalURL)
searchResponse = urllib2.urlopen(req) # Get HTML source code
searchResults = searchResponse.read() # HTML source code
rawOutput = BeautifulSoup(searchResults, "lxml") # Using lxml parser
# print(soup.prettify()) # Feedback

rawJSON = rawOutput.find('p').text # Just the json text
rawJSON.strip() # Trim the white space
iTunesObj = json.loads(rawJSON) # Decode iTunes JSON Data

for i in range(0, len(iTunesObj['results'])):  # Cycle through all songs by that artist
    currentSong = iTunesObj['results'][i]
    currentGenre = currentSong['primaryGenreName']
    alreadyAdded = False
    for j in range(0, len(potentialGenres)):  # See if the genre is already added
        if currentGenre == potentialGenres[j]:  # If exists
            alreadyAdded = True
    if alreadyAdded is False:  # If not added to array
        potentialGenres.append(currentGenre)  # Add to list

# Select Genre
print "Potential genre names:"
print "0: Custom entry"  # Allow for a custom entry
for i in range(0, len(potentialGenres)):  # Cycle through all possibilities
    index = i + 1
    print "%s: %s" % (index, potentialGenres[i])
chosenIndex = input("Choose a genre name: ")  # Prompt for link (inputs as String type)

if chosenIndex is 0:
    correctInput = False
    while correctInput is False:  # Cycle until correctly type in entry
        customGenre = raw_input("Genre: ")  # Allow for custom entry
        correct = raw_input("Done (y/n): ")  # Allow user to undo and go again
        if correct is "y":
            correctInput = True
    genre = customGenre  # Set final track name
else:  # If chose a suggested track name
    index = chosenIndex - 1  # Set index
    genre = potentialGenres[index]  # Set final
print ""  # Line break


# *******************   Set Remaining Values   *******************
# Default is a single
album = trackName + " - Single"
albumArtist = artist
trackNum = [1, 1]
discNumber = 1
discCount = 1

print "Track name: %s" % trackName
print "Artist: %s" % artist
print "Year: %s" % year
print "Album Artwork: %s" % imageURL
print "Genre: %s" % genre
print ""  # Line break

# *******************   Download Track   *******************
filePath = "~/Desktop/"
fileName = artist + " - " + trackName

ydl_opts = {  # Set options
    'format': 'bestaudio/best',
    'outtmpl': filePath + fileName + ".%(ext)s",
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192'  # 128, 160, 192, 210, 256
    }],
}

with youtube_dl.YoutubeDL(ydl_opts) as ydl:
    ydl.download([soundCloudLink])  # Download the song

# *******************   Update ID3 Tags   *******************
fullPath = filePath + fileName + ".mp3"
print fullPath
mp3Path = os.path.expanduser(fullPath)  # Define file
audiofile = eyed3.load(mp3Path)  # Load file

# Workaround 'NoneType' error
# https://bitbucket.org/nicfit/eyed3/issues/34/unable-to-save-id3-info-if-song-tag
if audiofile.tag is None:
    audiofile.tag = eyed3.id3.Tag()
    audiofile.tag.file_info = eyed3.id3.FileInfo(mp3Path)

# Set data
audiofile.tag.title = trackName
audiofile.tag.artist = artist
audiofile.tag.album = album
audiofile.tag.album_artist = albumArtist
audiofile.tag.track_num = (trackNum[0], trackNum[1])
audiofile.tag.disc_num = (discNumber, discCount)
audiofile.tag.genre = genre
audiofile.tag.year = year

# Append Image
# Reference: http://tuxpool.blogspot.com/2013/02/how-to-store-images-in-mp3-files-using.html

# Download image file from URL: http://stackoverflow.com/questions/8286352/how-to-save-an-image-locally-using-python-whose-url-address-i-already-know
urllib.urlretrieve(imageURL, "albumArtwork.jpg")  # Will be temporary

# Read image into memory
imagedata = open("albumArtwork.jpg","rb").read()

audiofile.tag.images.set(3, imagedata, "image/jpeg", u"Album Artwork") # Append image
# 3 for front cover, 4 for back cover
# Key: http://eyed3.nicfit.net/api/eyed3.id3.html#eyed3.id3.frames.Frame

os.remove("albumArtwork.jpg")  # Delete local image immediately after appending

audiofile.tag.save();  # Save meta data
