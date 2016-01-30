#!/usr/bin/env python

import urllib2, urllib, json, argparse,re, os
from bs4 import BeautifulSoup

hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
       'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
       'Accept-Encoding': 'none',
       'Accept-Language': 'en-US,en;q=0.8',
       'Connection': 'keep-alive'}

file_name = 'data/lyrics.json'

BASE_URL = 'https://www.google.com/search?'
SEARCH_FILTER = '+site:https://www.musixmatch.com/'

def search_google(song_name):
    song_name+=" lyrics"
    url = BASE_URL + urllib.urlencode({'q' : song_name.encode('utf-8')}) + SEARCH_FILTER
    req = urllib2.Request(url, headers=hdr)
    raw_res = urllib2.urlopen(req).read()
    soup = BeautifulSoup(raw_res)

    providers =[]
    for elm in  soup.find_all('h3',attrs={'class': 'r'}):
        for a_elm in elm.find_all("a"):
            providers.append(a_elm.attrs["href"])
    return providers

def lyricsguru(soup):
    lyrics = soup.find("div", {"class": "thecontent"})
    return lyrics

def azlyrics(soup):
    lyrics = soup.find_all("div")
    return lyrics[22].get_text()


def musixmatch(soup):
    lyrics= soup.find("span", {"id": "lyrics-html"})
    return lyrics.get_text()

def unp(soup):
    lyrics= soup.find("i")
    return lyrics.get_text()


def lyricsmint(soup):
    lyrics = soup.find("div", {"id": 'lyric'})
    p = lyrics.find_all("p")
    l =""
    for q in p:
        l+=q.get_text()+"\n"
    return l

available_providers = {
    'musixmatch': musixmatch,
    'azlyrics': azlyrics,
    'unp': unp,
    'lyricsmint': lyricsmint,
}

lyrics_dict = {}

def save_lyrics(lyrics):
    with open(file_name, "a") as json_file:
        json_file.write("{}\n".format(json.dumps(lyrics)))


def search_database(song_name):
    song_keywords = song_name.split()
    with open(file_name, "r") as json_file:
        for line in json_file:
            data = json.loads(line)
            for k, v in data.items():
                for key in song_keywords:
                    if(k.lower().find(key.lower())!=-1):
                        print v
                        return 1
    return 0


def get_lyrics(song_name):
    path =os.path.dirname(os.path.realpath(__file__))+'/'+file_name
    if not os.path.exists(path):
        os.mkdir("data")
        data_iterable={}
        with open(file_name, "w") as json_file:
            for data in data_iterable:
                json_file.write("{}\n".format(json.dumps(data)))
    if not search_database(song_name):
        providers = search_google(song_name)
        for a in available_providers:
            for provider in providers:
                if(provider.find(a)!=-1):
                    req = urllib2.Request(provider, headers=hdr)
                    raw_res = urllib2.urlopen(req).read()
                    soup = BeautifulSoup(raw_res)
                    lyrics = available_providers[a](soup)
                    print lyrics
                    lyrics_dict[soup.title.string] = lyrics
                    save_lyrics(lyrics_dict)
                    return
        else:
            print "Sorry lyrics not found"
            return

#------------------------------------------------------------------------
parser = argparse.ArgumentParser(description='Fetch lyrics of a song.')
parser.add_argument('song_name',
      help='name of the song'
    )

args = parser.parse_args()

if args.song_name:
  get_lyrics(args.song_name)
