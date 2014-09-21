#!/usr/bin/python

from bs4 import BeautifulSoup
import requests
import re
import json
import sys
import shutil

def auth():
    try:
        authfile = open('/var/www/home_portal/public/torrent/.tlauth','r')
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
    finally:
        authfile.close()

def parse(info):
    torrent = {}

    name = info.find(class_="title")
    url = info.find(class_="quickdownload").find('a').get('href')
    date = info.find(class_="name")
    dateRegex = re.match("^.*(\d{4}[-]\d{2}[-]\d{2}\s\d{2}[:]\d{2}[:]\d{2}).*$",str(date),re.DOTALL)
    size = info.find_all('td')
    sizeRegex = re.match("^.*[<td>](\d.*)\s(\w\w)[</td>].*$",str(size),re.DOTALL)
    torrent['name'] = str(name.string)
    torrent['url'] = 'http://torrentleech.org' + url
    torrent['date'] = dateRegex.group(1)
    torrent['size'] = sizeRegex.group(1) + ' ' + sizeRegex.group(2)

    if sizeRegex.group(2) == 'GB':
        sizemb = float(sizeRegex.group(1)) * 1024
    else:
        sizemb = float(sizeRegex.group(1))

    torrent['sizemb'] = sizemb

    return torrent

def getSoup(_class,data):
    torrentList = []
    soup = BeautifulSoup(data)

    for info in soup.find_all(class_=_class):
        torrent = parse(info)
        torrentList.append(torrent)

    return torrentList

def gather(session):
    torrentList = []

    try:
        tmpFile = open('/var/www/home_portal/public/torrent/torrent_list.tmp', 'w')
        for x in range(1,6):
            targeturl = 'http://torrentleech.org/torrents/browse/index/categories/13%2C14/page/' + str(x)
            r = session.get(targeturl)
            data = r.text
            torrentList += getSoup('even',data) + getSoup('odd',data)

        print >> tmpFile, json.dumps(torrentList, sort_keys=True)
    finally:
        tmpFile.close()

def validate():
    try:
        tmpFile = open('/var/www/home_portal/public/torrent/torrent_list.tmp', 'r')

        try:
            tmpJson = json.load(tmpFile)
            return True
        except ValueError:
            return False
    finally:
        tmpFile.close()

def main():
    auth()

if __name__ == "__main__":
    main()
    if validate():
        shutil.move('/var/www/home_portal/public/torrent/torrent_list.tmp','/var/www/home_portal/public/torrent/torrent_list.json')
