#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Modules:
import webbrowser # This module can control the browser
import json # Json encoder/decoder
from bs4 import BeautifulSoup # Module to sort through HTML
import lxml # Module to prepare html for BeautifulSoup
import urllib2 # Gets html
import sys # Allow more control over printing
import string # More ways to manipulate strings
import unidecode # Decodes weird characters
import youtube_dl # For downloading YouTube videos/audio

# Prompt User for Keywords for Song
userSearch = raw_input("Search for song: ") # Reads input as a string
# userSearch = input("Search for song (use quotes): ") # Reads input as raw code
# print("Searching for " + userSearch)
userSearch = userSearch.strip() # Remove extraneous white space

# Search for song in iTunes Store
# Documentation: http://www.apple.com/itunes/affiliates/resources/documentation/itunes-store-web-service-search-api.html
baseURL = "https://itunes.apple.com/search?"
searchKeys = [
    ["term", userSearch],
    ["country", "US"],
    ["media", "music"],
    ["limit", "50"],
    ["lang", "en_us"],
    ["explicit", "yes"]
]
finalURL = baseURL
for i in range(0, len(searchKeys)): # len() returns length of a variable
    # print "Term: %d" % (i)
    currentKey = searchKeys[i]
    criteria = str(currentKey[1]) #Make sure it's a string
    criteria = criteria.replace(" ", "%20") # %20 represents a space
    appendStr = currentKey[0] + "=" + criteria # Build url
    # print(appendStr)
    if i < (len(searchKeys) - 1):
        appendStr += "&"
    finalURL += appendStr

# print("Final URL: " + finalURL) # Debugging
# webbrowser.open(finalURL)

# Retrieve and Save iTunes JSON Data
response = urllib2.urlopen(finalURL) #Get HTML source code
html = response.read() #HTML source code
soup = BeautifulSoup(html, "lxml") # Using lxml parser
print("")
print("*********** Found iTunes data ***********")
print("")
# print(soup.prettify()) # Feedback

rawJSON = soup.find('p').text # Just the json text
rawJSON.strip() # Trim the white space

# Parse iTunes JSON Data
iTunesObj = json.loads(rawJSON) # Decode JSON
# print(iTunesObj)

numShow = 5

results = iTunesObj['results']
for i in range(0, numShow):
    sys.stdout.write("(%i) Track Name: " % i)
    sys.stdout.flush() # No line break
    print results[i]['trackName'] # Adds a line break after
    print "    Artist: %s" % results[i]['artistName']
    print "    Album: %s" % results[i]['collectionName']
    print "    Genre: %s" % results[i]['primaryGenreName']
    print("")

print("Which song is the one you were looking for?")
iTunesSearchSelection = input("Type the respective index: ")
songData = results[iTunesSearchSelection]
print "" # Line break
print("Selected:")
print "%s by %s" % (songData['trackName'], songData['artistName'])
print "" # Line break


# *******************   Find song on YouTube   *******************

baseURL = "https://www.youtube.com/results?search_query="
YouTubeSearch = songData['trackName'] + " " + songData['artistName']

YouTubeSearch = unidecode.unidecode(YouTubeSearch) # Remove complex unicode characters
print "Searching for '%s' on YouTube" % YouTubeSearch
out = YouTubeSearch.translate(string.maketrans("",""), string.punctuation) # Remove punctuation
YouTubeSearch = YouTubeSearch.replace(" ", "+") # Remove spaces with '+'
finalURL = baseURL + YouTubeSearch

response = urllib2.urlopen(finalURL) #Get HTML source code
html = response.read() #HTML source code
soup = BeautifulSoup(html, "lxml") # Using lxml parser

videoLinks = soup.findAll("a", { "class": "yt-uix-sessionlink yt-uix-tile-link yt-ui-ellipsis yt-ui-ellipsis-2       spf-link " })
videoUploaders = soup.findAll("a", { "class": "yt-uix-sessionlink g-hovercard      spf-link " })
videoTimes = soup.findAll("div", { "class": "yt-lockup-thumbnail" }) # In case there are playlists, find the div

videos = [];
# Stores all the results on the page except for the last 3 hits on the page
upper = len(videoTimes) - 3
for i in range(0, upper):
    time = videoTimes[i].findAll("span", { "class": "video-time" }) # Find within the larger div
    if not time: # If array is empty (ie. no time found for that video)
        print "Found a playlist"
    else: # If not a playlists
        # The video must be a playlist
        time = time[0] # First result

        link = "https://www.youtube.com" + videoLinks[i].get('href')

        print videoLinks[i].contents[0]
        # Structure of array:
        # [name, link, uploader, length]
        videos.append(
            [
                videoLinks[i].contents[0],
                link,
                videoUploaders[i].contents[0],
                time.text
            ]
        )

# Only returns up to specified number
for i in range(0, numShow):
    video = videos[i]
    sys.stdout.write("(%i) Video name: " % i)
    sys.stdout.flush() # No line break
    print video[0] # Adds a line break after
    print "    Link: %s" % video[1]
    print "    Uploader: %s" % video[2]
    print "    Length: %s" % video[3]
    print("")

print("Which video is the one you were looking for?")
print("The iTunes version is: %s" % songData['trackTimeMillis'])
YouTubeSelection = input("Type the respective index: ")
data = videos[YouTubeSelection]

fileName = songData['artistName'] + " - " + songData['trackName']

ydl_opts = {
    'format': 'bestaudio/best',
    # 'outtmpl': u'%(title)s-%(id)s.%(ext)s',
    'outtmpl': fileName + ".%(ext)s",
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
}

with youtube_dl.YoutubeDL(ydl_opts) as ydl:
    ydl.download([data[1]])
