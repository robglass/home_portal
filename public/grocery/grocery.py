#!/usr/bin/python

import json
import re
import requests
import shutil
import sys

def auth():
    with open('/var/www/home_portal/public/grocery/.htauth','r') as authfile:
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

def gather(session, tokendata):
    groceryList = []
    with open('/var/www/home_portal/public/grocery/grocery_list.tmp','w+') as tmpFile:
        token = tokendata['access_token']
        get_headers = {
                "Authorization": "Bearer " + token,
        }

        for x in range(1,17):
            targeturl = 'https://api.htebiz.com/v1/stores/384/departments/' + str(x) + '/weekly_specials'
            r = session.get(targeturl, headers=get_headers)
            data = r.text
            groceryList.append(data)

        for line in groceryList:
            print >> tmpFile, line.encode('ascii', 'ignore') + ','

def fix_format():
    with open('/var/www/home_portal/public/grocery/grocery_list.tmp','r+') as tmpFile:
        content = tmpFile.read()
        tmpFile.seek(0)
        tmpFile.write('[' + content )
        newcontent = re.sub(r',$', ']', content).rstrip('\n')
        print >> tmpFile, newcontent

def validate():
    with open('/var/www/home_portal/public/grocery/grocery_list.tmp','r') as tmpFile:
        try:
            tmpJson = json.load(tmpFile)
            return True
        except ValueError:
            return False

def main():
    auth()
    fix_format()

if __name__ == "__main__":
    main()
    if validate():
        shutil.move('/var/www/home_portal/public/grocery/grocery_list.tmp','/var/www/home_portal/public/grocery/grocery_list.json')
