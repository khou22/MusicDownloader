# Modules:
import webbrowser # This module can control the browser
import json # Json encoder/decoder
from bs4 import BeautifulSoup # Module to sort through HTML
import lxml # Module to prepare html for BeautifulSoup
import urllib2 # Gets html

# Prompt User for Keywords for Song
userSearch = raw_input("Search for song: ") # Reads input as a string
# userSearch = input("Search for song (use quotes): ") # Reads input as raw code
print("Searching for " + userSearch)
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

print("Final URL: " + finalURL)
# webbrowser.open(finalURL)

# Retrieve and Save iTunes JSON Data
response = urllib2.urlopen(finalURL) #Get HTML source code
html = response.read() #HTML source code
soup = BeautifulSoup(html, "lxml") # Using lxml parser
print()
print("*********** Found iTunes data ***********")
print()
# print(soup.prettify()) # Feedback

rawJSON = soup.find('p').text # Just the json text
rawJSON.strip() # Trim the white space

# Parse iTunes JSON Data
iTunesObj = json.loads(rawJSON) # Decode JSON
# print(iTunesObj)

# Sample iTunes data for one song
# {
#     u'collectionExplicitness': u'notExplicit',
#     u'releaseDate': u'2014-06-13T07:00:00Z',
#     u'currency': u'USD',
#     u'artistId': 4091218,
#     u'previewUrl': u'http://a1434.phobos.apple.com/us/r1000/029/Music4/v4/90/73/cd/9073cd0b-d672-77d5-e405-0ebf47ecf80e/mzaf_1792261294529959695.plus.aac.p.m4a',
#     u'trackPrice': 1.29,
#     u'isStreamable': True,
#     u'trackViewUrl': u'https://itunes.apple.com/us/album/red-lights/id872899091?i=872899097&uo=4',
#     u'collectionName': u'A Town Called Paradise (Deluxe)',
#     u'collectionId': 872899091,
#     u'trackId': 872899097,
#     u'collectionViewUrl': u'https://itunes.apple.com/us/album/red-lights/id872899091?i=872899097&uo=4',
#     u'trackCount': 17,
#     u'trackNumber': 1,
#     u'discNumber': 1,
#     u'collectionPrice': 12.99,
#     u'trackCensoredName': u'Red Lights',
#     u'trackName': u'Red Lights',
#     u'trackTimeMillis': 262200,
#     u'primaryGenreName': u'Dance',
#     u'artistViewUrl': u'https://itunes.apple.com/us/artist/tiesto/id4091218?uo=4',
#     u'kind': u'song',
#     u'country': u'USA',
#     u'wrapperType': u'track',
#     u'artworkUrl100': u'http://is5.mzstatic.com/image/thumb/Music4/v4/1d/d2/7e/1dd27e62-8296-9468-2131-1d8a8be1de9b/source/100x100bb.jpg',
#     u'collectionCensoredName': u'A Town Called Paradise (Deluxe)',
#     u'radioStationUrl': u'https://itunes.apple.com/station/idra.872899097',
#     u'artistName': u'Ti\xebsto',
#     u'artworkUrl60': u'http://is5.mzstatic.com/image/thumb/Music4/v4/1d/d2/7e/1dd27e62-8296-9468-2131-1d8a8be1de9b/source/60x60bb.jpg',
#     u'trackExplicitness': u'notExplicit',
#     u'artworkUrl30': u'http://is5.mzstatic.com/image/thumb/Music4/v4/1d/d2/7e/1dd27e62-8296-9468-2131-1d8a8be1de9b/source/30x30bb.jpg',
#     u'discCount': 1
# }

print("Track name: " + iTunesObj['results'][0]['trackName'])
print("Artist: " +  iTunesObj['results'][0]['artistName'])
print("Album: " +  iTunesObj['results'][0]['collectionName'])
print("Genre: " +  iTunesObj['results'][0]['primaryGenreName'])
