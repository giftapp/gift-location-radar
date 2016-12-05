#!/usr/bin/python
# coding=utf-8

__author__ = "Matan Lachmish"
__copyright__ = "Copyright 2016, Gift"
__version__ = "1.0"
__status__ = "Development"

import sys
import requests
import json
import pickle
from progressbar import ProgressBar, Percentage, Bar

GOOGLE_PLACES_API_KEY = "AIzaSyAJkYNnUYUzOWmyN1qunzLBeroz5zeTDpE"
SEARCH_RADIUS = 50000
LOCATIONS = {
    'North'         : (32.781457, 35.309147),
    'Tel Aviv'      : (32.088162,34.782470),
    'Beer Sheva'    : (31.251320, 34.793456),
    'South'         : (29.797318, 34.939234),
}
SEARCH_KEYWORDS = [u'אולם_אירועים', u'אולם_חתונות', u'Wedding_Venue', u'Wedding_Hall', u'Event_Venue']

def main(argv):
    # Usage check
    if 2 != len(argv):
        print("Usage: python {} fetch|list".format(argv[0]))
        return -1

    task = argv[1]
    if task == 'fetch':
        fetchPlaces()
    elif task == 'list':
        listPlaces()
    else:
        print("Unknown task {}".format(task))


def fetchPlaces():
    placesDict = loadObj("placesDict")
    print("Loaded {} places".format(len(placesDict)))

    for location, coordinates in LOCATIONS.items():
        for keyword in SEARCH_KEYWORDS:
            searchResults = radarSearch(location, coordinates, SEARCH_RADIUS, keyword)
            if searchResults is None:
                continue

            print("Found {} results".format(len(searchResults)))
            sys.stdout.flush()

            progress = ProgressBar(widgets=[Percentage(), Bar()], max_value=len(searchResults), redirect_stdout=True)
            counter = 0
            for searchResult in searchResults:
                progress.update(counter)
                counter += 1

                placeId = searchResult['place_id']
                if placeId not in placesDict:
                    placeDetails = getPlaceDetails(placeId)
                    if placeDetails is not None:
                        placesDict[placeId] = placeDetails
            progress.finish()

    print("Saving {} places".format(len(placesDict)))
    saveObj(placesDict, "placesDict")

def radarSearch(location, coordinates, radius, keyword):
    print("Searching {} in {}".format(keyword, location))
    sys.stdout.flush()

    formatedCoordinates = "{},{}".format(coordinates[0], coordinates[1])
    response = requests.get(
        "https://maps.googleapis.com/maps/api/place/radarsearch/json?location={}&radius={}&keyword={}&key={}".format(
            formatedCoordinates, radius, keyword, GOOGLE_PLACES_API_KEY)).json()

    if response['status'] != 'OK':
        print("Error accrued: {}".format(response['status']))
        return

    return response['results']

def getPlaceDetails(placeId):
    response = requests.get("https://maps.googleapis.com/maps/api/place/details/json?placeid={}&key={}".format(placeId, GOOGLE_PLACES_API_KEY)).json()
    if response['status'] != 'OK':
        print("Error accrued: {}".format(response['status']))
        return
    return response['result']

def listPlaces():
    placesDict = loadObj("placesDict")
    print("Loaded {} places".format(len(placesDict)))
    print("place_id\t\t\t\t\tname")
    for key,value in placesDict.items():
        print("{}:\t\t{}".format(key, value['name']))

def saveObj(obj, name ):
    with open('dataset/' + name + '.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

    jsonDump = json.dumps(obj, ensure_ascii=False)
    with open('dataset/' + name + '.json', 'wb') as file:
        file.write(jsonDump.encode('utf-8'))

def loadObj(name ):
    with open('dataset/' + name + '.pkl', 'rb') as f:
        return pickle.load(f)

if __name__ == "__main__":
    main(sys.argv)