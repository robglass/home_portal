#!/usr/bin/python

from bs4 import BeautifulSoup
import requests
import re
import json
import sys
import shutil

def auth():
    # Auth file that contains username and password in json format
    authfile = open('/var/www/home_portal/public/torrent/.tlauth','r')

    try:
        # Grab the username and password and assign to proper variables
        authdata = json.load(authfile)
        username = authdata['name']
        password = authdata['password']
        # This is the URL that you are presented with when you would log into the website via a browser
        authurl = 'http://torrentleech.org/user/account/login/'

        # Set the headers in order to authenticate with the targeturl
        req_headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        # Mimic the form login info that is provided on the website
        formdata = {
            'username': username,
            'password': password,
            'login': 'submit'
        }

        # Authenticate with the site.
        # Successfull authentication provides a http code of 302 as it redirects you to the rest of the site.
        # Catch this 302 and carry on with the rest of the script, otherwise dump out.
        session = requests.session()
        r = session.post(authurl, data=formdata, headers=req_headers, allow_redirects=False)
        if r.status_code == 302:
            gather(session)
        else:
            print('Error: Unable to Authenticate')
            sys.exit(1)
    finally:
        authfile.close()

def parse(info):
    # Initialize the dictionary
    torrent = {}

    # Gather the specific information that we are wanting to get.
    # Get the name, url, date, and size of the torrent.
    name = info.find(class_="title")
    url = info.find(class_="quickdownload").find('a').get('href')
    date = info.find(class_="name")
    dateRegex = re.match("^.*(\d{4}[-]\d{2}[-]\d{2}\s\d{2}[:]\d{2}[:]\d{2}).*$",str(date),re.DOTALL)
    size = info.find_all('td')
    sizeRegex = re.match("^.*[<td>](\d.*)\s(\w\w)[</td>].*$",str(size),re.DOTALL)
    torrent['name'] = name.string
    torrent['url'] = 'http://torrentleech.org' + url
    torrent['date'] = dateRegex.group(1)
    torrent['size'] = sizeRegex.group(1) + ' ' + sizeRegex.group(2)

    # Look for anything in GB size, and convert it to MB as to have everything in one factor.
    # This is then later used to sort size on the website.
    if sizeRegex.group(2) == 'GB':
        sizemb = float(sizeRegex.group(1)) * 1024
    else:
        sizemb = float(sizeRegex.group(1))

    torrent['sizemb'] = sizemb

    return torrent

def getSoup(_class,data):
    torrentList = []
    soup = BeautifulSoup(data)

    # Use BeautifulSoup to get all http information for the specific class we are looking for then
    # add that information to the list.
    for info in soup.find_all(class_=_class):
        torrent = parse(info)
        torrentList.append(torrent)

    # Return the contents of the list back to the code that called this function in the first place.
    return torrentList

def gather(session):
    torrentList = []
    # Open/create a temp file for storage before overwritting the perm file that the website
    # relys on. This way we can save off data and manipulate it, and not break anything.
    tmpFile = open('/var/www/home_portal/public/torrent/torrent_list.tmp', 'w')

    try:
        # Scrape the first 5 pages of the targeturl and store that raw html data into the list and
        # pass it off to getSoup for parsing.
        for x in range(1,6):
            targeturl = 'http://torrentleech.org/torrents/browse/index/categories/13%2C14/page/' + str(x)
            r = session.get(targeturl)
            data = r.text
            torrentList += getSoup('even',data) + getSoup('odd',data)

        # Export all the data to json format and save it to a temp file for later use.
        print >> tmpFile, json.dumps(torrentList, sort_keys=True)
    finally:
        tmpFile.close()

def validate():
    # Reopen the temp file but with readonly rights this time.
    tmpFile = open('/var/www/home_portal/public/torrent/torrent_list.tmp', 'r')

    try:
        try:
            # Attempt to load the temp file up using a json parser.
            # If it passes, we now know the temp file is proper json format.
            # If it fails, we do not have proper json and something else broke upstream.
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
    # If the temp file is confirmed to be proper json, go ahead only at this time, overwrite the perm file.
    # Thus updating the results that show on the website.
    if validate():
        shutil.move('/var/www/home_portal/public/torrent/torrent_list.tmp','/var/www/home_portal/public/torrent/torrent_list.json')
