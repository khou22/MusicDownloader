# SoundCloud Downloader Methodology
#
# Pull data from page title
#
# Pull data from just track name
# Find “ - “ to differentiate artist from song name
# Use iTunes Api to see if the artist exists/which part is the artist name
#
# Select from a list of aggregated data
# Potential artists, track names, etc.
# Type index “0” for custom input
# Type other index for one of the “smart” inputs
#
# Search iTunes for genre’s by that artist
#
# If artist has “ x “ - usually means two artists
# Split and check both artists names with iTunes to see if they’re legit
#
# When adding any data:
# Make sure artist names don’t have “ft.” or “feat.” — create a new array for featured artists