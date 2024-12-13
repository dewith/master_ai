import requests
import urllib.request
import urllib.parse
import json
from bs4 import BeautifulSoup
import time 
import random

# token source https://genius.com/api-clients
base = "https://api.genius.com"
client_access_token = "DQgv_3-Gtv3fkUaScv0gd3XmGD1X6lRAcz-kO4TxSMngve3VHbo4UIgH3nI0OBQA"

def get_json(path, params=None, headers=None):
    '''Send request and get response in json format.'''
    requrl = '/'.join([base, path])
    token = "Bearer {}".format(client_access_token)
    if headers:
        headers['Authorization'] = token
    else:
        headers = {"Authorization": token}

    # Get response object from querying genius api
    response = requests.get(url=requrl, params=params, headers=headers)
    response.raise_for_status()
    return response.json()


def search_artist(artist_name):
    '''Search Genius API via artist name.'''
    search = "/search?q="
    query = base + search + urllib.parse.quote(artist_name)
    request = urllib.request.Request(query)

    request.add_header("Authorization", "Bearer " + client_access_token)
    request.add_header("User-Agent", "")

    response = urllib.request.urlopen(request, timeout=10)
    raw = response.read()
    data = json.loads(raw)['response']['hits']

    for item in data:
        print(item['result']['primary_artist']['name']
              + ': ' + item['result']['title'])
    return data

def get_artist(artist_id):
    '''Search meta data about artist Genius API via Artist ID.'''
    search = "artists/"
    path = search + str(artist_id)
    request = get_json(path)
    data = request['response']['artist']
    print('Followers:', data["followers_count"])
    return data


def get_songs_ids(artist_id):
    '''Get all the song id from an artist.'''
    current_page = 1
    next_page = True
    songs = [] # to store final song ids

    while next_page:
        path = "artists/{}/songs/".format(artist_id)
        params = {'page': current_page}
        data = get_json(path=path, params=params)

        page_songs = data['response']['songs']
        if page_songs:
            # Add all the songs of current page
            songs += page_songs
            current_page += 1
            print("Page {} finished scraping".format(current_page))
        else:
            next_page = False

    print("Song id were scraped from {} pages".format(current_page))
    songs = [(song["title"], song["id"]) for song in songs]
    return songs


def connect_lyrics(song_id):
    '''Constructs the path of song lyrics.'''
    url = "songs/{}".format(song_id)
    data = get_json(url)

    # Gets the path of song lyrics
    title = data['response']['song']['title']
    path = data['response']['song']['path']

    return title, path


def retrieve_lyrics(song_id):
    '''Retrieves lyrics from html page.'''
    # //section[contains(@ng-hide, "lyrics_ctrl")]
    title, path = connect_lyrics(song_id)
    URL = "http://genius.com" + path
    page = requests.get(URL)
    soup = BeautifulSoup(page.text, "lxml")
    lyrics = soup.find(
        "div", {'class': "Lyrics__Container-sc-1ynbvzw-6 YYrds"}
    ).get_text(separator=" \n").strip().replace("\'", "")
    print(title, '-->', lyrics[:80].replace('\n', ' '))
    time.sleep(random.uniform(1.0, 3.0))
    return lyrics


def get_song_information(song_ids):
    '''Retrieve meta data about a song.'''
    # initialize a dictionary.
    song_list = {}
    print("Scraping song information")
    for i, song_id in enumerate(song_ids):
        print("id:" + str(song_id) + " start. ->")

        path = "songs/{}".format(song_id)
        data = get_json(path=path)["response"]["song"]

        song_list.update({
        i: {
            "title": data["title"],
            "album": data["album"]["name"] if data["album"] else "<single>",
            "release_date": data["release_date"] if data["release_date"] else "unidentified",
            "featured_artists":
                [feat["name"] if data["featured_artists"] else "" for feat in data["featured_artists"]],
            "producer_artists":
                [feat["name"] if data["producer_artists"] else "" for feat in data["producer_artists"]],
            "writer_artists":
                [feat["name"] if data["writer_artists"] else "" for feat in data["writer_artists"]],
            "genius_track_id": song_id,
            "genius_album_id": data["album"]["id"] if data["album"] else "none"}
        })

        print("-> id:" + str(song_id) + " is finished. \n")
    return song_list