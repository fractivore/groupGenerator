import sys, json

def importCacheFile(filename):
    with open(filename) as infile:
        return json.load(infile)


def exportCacheFile(filename,data):
    with open(filename, "w") as outfile:
        json.dump(data, outfile)


