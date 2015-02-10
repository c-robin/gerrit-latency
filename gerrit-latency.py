#! /usr/bin/python
# -*- coding: UTF-8 -*-

import urllib
import subprocess
import re
from urllib2 import Request, urlopen, URLError, HTTPBasicAuthHandler, HTTPPasswordMgrWithDefaultRealm, build_opener, install_opener
import json
from requests.auth import HTTPDigestAuth
import requests

class Commit():

    def __init__(self, start_date, merge_date):
        self.start= start_date
        self.merge = merge_date

def parseDate(date_string):
    return datetime.strptime(date_string, "%d. %b %I:%M")

config_file = open('passwd', 'r')
gerrit_user = config_file.readline().rstrip()
gerrit_pass = config_file.readline().rstrip()
config_file.close()
print("login: " + gerrit_user)
print("passwd: " + gerrit_pass)

gerrit_ssh_port = "29418"
gerrit_http_port = "8080"
gerrit_url = "localhost"
ssh_public_key = "~/.ssh/id_rsa"
#DO not forget to use status:merged in request
gerrit_request = "owner:self status:merged"

ret = subprocess.Popen(["ssh","-p",gerrit_ssh_port, "-i", ssh_public_key, gerrit_user + "@" + gerrit_url, "gerrit query " + gerrit_request], stdout=subprocess.PIPE);
out, err = ret.communicate()

commits_list = []
changes_list = list(set(re.findall("change (.{40})", out)))

#Call gerrit_REST_API
for change in changes_list:
    try:
        url = "http://" + gerrit_url + ":" + gerrit_http_port + "/a/" + "changes/" + change + "/detail"
        print url
        print "sending request"
        r = requests.get(url, auth = HTTPDigestAuth(gerrit_user, gerrit_pass), timeout=None, proxies = None)
        print "request sent"
    
        print r.url
    except URLError, e:
        print 'REST error:', e