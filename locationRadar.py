#!/usr/bin/python
# coding=utf-8

__author__ = "Matan Lachmish"
__copyright__ = "Copyright 2016, Gift"
__version__ = "1.0"
__status__ = "Development"

import sys
import requests
import csv

GOOGLE_PLACES_API_KEY = "AIzaSyAJkYNnUYUzOWmyN1qunzLBeroz5zeTDpE"
SEARCH_RADIUS = 50000
LOCATIONS = {
    "Tel Aviv" : (32.088162,34.782470)
}
SEARCH_KEYWORDS = [u'אולם_אירועים']

def main(argv):
    # Usage check
    if 1 != len(argv):
        print("Usage: python %s" % argv[0])
        return -1

    placesDict = {}
    for location,coordinates in LOCATIONS.items():
        for keyword in SEARCH_KEYWORDS:
            searchResults = radarSearch(location, coordinates, SEARCH_RADIUS, keyword)
            print("Found {} results".format(len(searchResults)))

            for searchResult in searchResults:
                placeId = searchResult['place_id']
                if placeId not in placesDict:
                    placeDetails = getPlaceDetails(placeId)
                    placesDict[placeId] = placeDetails

    writePlacesToFile(placesDict)

def radarSearch(location, coordinates, radius, keyword):
    print("Searching {} in {}".format(keyword, location))
    formatedCoordinates = "{},{}".format(coordinates[0], coordinates[1])
    response = requests.get(
        "https://maps.googleapis.com/maps/api/place/radarsearch/json?location={}&radius={}&keyword={}&key={}".format(
            formatedCoordinates, radius, keyword, GOOGLE_PLACES_API_KEY)).json()

    if response['status'] != 'OK':
        print("Error accrued")
        return

    return response['results']

def getPlaceDetails(placeId):
    response = requests.get("https://maps.googleapis.com/maps/api/place/details/json?placeid={}&key={}".format(placeId, GOOGLE_PLACES_API_KEY)).json()
    if response['status'] != 'OK':
        print("Error accrued")
        return
    return response['result']

def writePlacesToFile(placesDict):
    with open('places.csv', 'w') as file:
        writer = csv.writer(file, delimiter=',')
        for key, value in placesDict.items():
            writer.writerow([key, value])

if __name__ == "__main__":
    main(sys.argv)