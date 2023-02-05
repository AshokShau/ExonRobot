"""
MIT License

Copyright (c) 2022 ABISHNOI69 

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import json
import urllib.request as url

VERSION = "1.1.0"
APIURL = "http://api.github.com/repos/"


def vercheck() -> str:
    return str(VERSION)


# Repo-wise stuff


def getData(repoURL):
    try:
        with url.urlopen(APIURL + repoURL + "/releases") as data_raw:
            return json.loads(data_raw.read().decode())
    except:
        return None


def getReleaseData(repoData, index):
    if index < len(repoData):
        return repoData[index]
    return None


# Release-wise stuff


def getAuthor(releaseData):
    if releaseData is None:
        return None
    return releaseData["author"]["login"]


def getAuthorUrl(releaseData):
    if releaseData is None:
        return None
    return releaseData["author"]["html_url"]


def getReleaseName(releaseData):
    if releaseData is None:
        return None
    return releaseData["name"]


def getReleaseDate(releaseData):
    if releaseData is None:
        return None
    return releaseData["published_at"]


def getAssetsSize(releaseData):
    if releaseData is None:
        return None
    return len(releaseData["assets"])


def getAssets(releaseData):
    if releaseData is None:
        return None
    return releaseData["assets"]


def getBody(releaseData):  # changelog stuff
    if releaseData is None:
        return None
    return releaseData["body"]


# Asset-wise stuff


def getReleaseFileName(asset):
    return asset["name"]


def getReleaseFileURL(asset):
    return asset["browser_download_url"]


def getDownloadCount(asset):
    return asset["download_count"]


def getSize(asset):
    return asset["size"]
