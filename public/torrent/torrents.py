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
        parse(session)
    else:
        print('Error: Unable to Authenticate')
        sys.exit(1)

def parse(session):
    torrentList = []
    tmpFile = open('torrent_list.tmp', 'w')
    torrentEven = []
    torrentOdd = []

    for x in range(1,6):
        targeturl = 'http://torrentleech.org/torrents/browse/index/categories/13%2C14/page/' + str(x)
        print(targeturl)
        r = session.get(targeturl)
        data = r.text
        soup = BeautifulSoup(data)

        for info in soup.find_all(class_="even"):
            torrent = {}
            name = info.find(class_="title")
            url = info.find(class_="quickdownload").find('a').get('href')
            date = info.find(class_="name")
            dateRegex = re.match("^.*(\d{4}[-]\d{2}[-]\d{2}\s\d{2}[:]\d{2}[:]\d{2}).*$",str(date),re.DOTALL)
            size = info.find_all('td')
            sizeRegex = re.match("^.*[<td>](\d.*\s\w\w)[</td>].*$",str(size),re.DOTALL)
            torrent['name'] = str(name.string)
            torrent['url'] = 'http://torrentleech.org' + url
            torrent['date'] = dateRegex.group(1)
            torrent['size'] = sizeRegex.group(1)
            torrentEven.append(torrent)

        for info in soup.find_all(class_="odd"):
            torrent = {}
            name = info.find(class_="title")
            url = info.find(class_="quickdownload").find('a').get('href')
            date = info.find(class_="name")
            dateRegex = re.match("^.*(\d{4}[-]\d{2}[-]\d{2}\s\d{2}[:]\d{2}[:]\d{2}).*$",str(date),re.DOTALL)
            size = info.find_all('td')
            sizeRegex = re.match("^.*[<td>](\d.*\s\w\w)[</td>].*$",str(size),re.DOTALL)
            torrent['name'] = str(name.string)
            torrent['url'] = 'http://torrentleech.org' + url
            torrent['date'] = dateRegex.group(1)
            torrent['size'] = sizeRegex.group(1)
            torrentOdd.append(torrent)

    torrentList = torrentEven + torrentOdd

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
