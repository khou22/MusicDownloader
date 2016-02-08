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
print("Found iTunes data")
# print(soup.prettify()) # Feedback

rawJSON = soup.find('p').text # Just the json text
rawJSON.strip() # Trim the white space

# Parse iTunes JSON Data
iTunesObj = json.loads(rawJSON) # Decode JSON
