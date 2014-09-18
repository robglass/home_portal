#!/usr/bin/python

from bs4 import BeautifulSoup
import requests
import re
import json

def auth():
    authfile = open('.tlauth')
    authdata = json.load(authfile)
    USERNAME = authdata['name']
    PASSWORD = authdata['password']
    LOGINURL = 'http://torrentleech.org/user/account/login/'
    DATAURL = 'http://torrentleech.org/torrents/browse/index/categories/13,14'

    session = requests.session()
    req_headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    formdata = {
        'username': USERNAME,
        'password': PASSWORD,
        'login': 'submit'
    }

    # Authenticate
    r = session.post(LOGINURL, data=formdata, headers=req_headers, allow_redirects=False)

    # Read data
    r2 = session.get(DATAURL)
    data = r2.text
    gather(data)

def gather(data):
    soup = BeautifulSoup(data)
    torrent = {}
    torrentList = {}

    for info in soup.find_all(class_="even"):
        name = info.find(class_="title")
        url = info.find(class_="quickdownload").find('a').get('href')
        torrent[name.string] = 'http://torrentleech.org' + url

    torrentList = [{'name':key,'url':value} for key,value in torrent.items()]
    print(json.dumps(torrentList, sort_keys=True))

def main():
    auth()

if __name__ == "__main__":
    main()
