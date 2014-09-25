#!/usr/bin/python

import json
import re
import requests
import shutil
import sys

def auth():
    authfile = open('/var/www/home_portal/public/grocery/.htauth','r')

    try:
        authdata = json.load(authfile)
        granttype = authdata['granttype']
        username = authdata['username']
        password = authdata['password']
        clientid = authdata['clientid']
        clientsecret = authdata['clientsecret']

        authurl = 'https://api.htebiz.com/oauth/token'

        req_headers = {
                'Content-Type': 'application/x-www-form-urlencoded'
        }

        formdata = {
                'grant_type': granttype,
                'username': username,
                'password': password,
                'client_id': clientid,
                'client_secret': clientsecret,
        }

        session = requests.session()
        r = session.post(authurl, data=formdata, headers=req_headers, allow_redirects=False)
        tokendata = json.loads(r.text)
        gather(session, tokendata)

    finally:
        authfile.close()

def gather(session, tokendata):
    groceryList = []
    tmpFile = open('/var/www/home_portal/public/grocery/grocery_list.tmp','w')

    try:
        token = tokendata['access_token']
        get_headers = {
                "Authorization": "Bearer " + token,
        }

        for x in range(1,17):
            targeturl = 'https://api.htebiz.com/v1/stores/384/departments/' + str(x) + '/weekly_specials'
            r = session.get(targeturl, headers=get_headers)
            data = r.text
            groceryList.append(data)

        print >> tmpFile, json.dumps(groceryList)
    finally:
        tmpFile.close()

def validate():
    tmpFile = open('/var/www/home_portal/public/grocery/grocery_list.tmp','r')

    try:
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
        shutil.move('/var/www/home_portal/public/grocery/grocery_list.tmp','/var/www/home_portal/public/grocery/grocery_list.json')
