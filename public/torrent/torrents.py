#!/usr/bin/python

from bs4 import BeautifulSoup
import requests
import re
import json
import sys
import shutil

def auth():
    authfile = open('.tlauth')
    authdata = json.load(authfile)
    authurl = 'http://torrentleech.org/user/account/login/'
    username = authdata['name']
    password = authdata['password']

    session = requests.session()
    req_headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    formdata = {
        'username': username,
        'password': password,
        'login': 'submit'
    }

    # Authenticate
    r = session.post(authurl, data=formdata, headers=req_headers, allow_redirects=False)
    if r.status_code == 302:
        gather(session)
    else:
        print('Error: Unable to Authenticate')
        sys.exit(1)

def gather(session):
    targeturl = 'http://torrentleech.org/torrents/browse/index/categories/13%2C14/page/1'

    # Read data
    r = session.get(targeturl)
    data = r.text

    parse(data)

def parse(data):
    soup = BeautifulSoup(data)
    torrent = {}
    torrentList = {}
    tmpFile = open('torrent_list.tmp', 'w')

    for info in soup.find_all(class_="even"):
        name = info.find(class_="title")
        url = info.find(class_="quickdownload").find('a').get('href')
        torrent[name.string] = 'http://torrentleech.org' + url

    for info in soup.find_all(class_="odd"):
        name = info.find(class_="title")
        url = info.find(class_="quickdownload").find('a').get('href')
        torrent[name.string] = 'http://torrentleech.org' + url

    torrentList = [{'name':key,'url':value} for key,value in torrent.items()]
    print >> tmpFile, json.dumps(torrentList, sort_keys=True)

    tmpFile.close()

def validate():
    tmpFile = open('torrent_list.tmp', 'r')

    try:
        tmpJson = json.load(tmpFile)
        return True
    except ValueError:
        return False

    tmpFile.close()

def main():
    auth()
    if validate():
        shutil.move('torrent_list.tmp','torrent_list.json')

if __name__ == "__main__":
    main()
