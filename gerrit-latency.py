#! /usr/bin/python
# -*- coding: UTF-8 -*-

import urllib
import subprocess
import re
from urllib2 import Request, urlopen, URLError, HTTPBasicAuthHandler, HTTPPasswordMgrWithDefaultRealm, build_opener, install_opener
import json
from requests.auth import HTTPDigestAuth
import requests
from datetime import datetime

class Commit():

    def __init__(self, start_date, merge_date):
        self.start= start_date
        self.merge = merge_date
    
    def latency(self):
        return (self.merge - self.start).days

    def __str__(self):
        return str(self.start) + " " + str(self.merge)

def parseDate(date_string):
    return datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S")

#Loading config
config = {}
execfile("conf.py", config)
gerrit_user = config["gerrit_user"]
gerrit_pass = config["gerrit_pass"]
gerrit_http_port = config["gerrit_http_port"]
gerrit_url = config["gerrit_url"]
gerrit_request = config["gerrit_request"]

changes_id_list = []
commits_list = []
commit_start_date = None
commit_merge_date = None

try:
    url =  "http://" + gerrit_url + ":" + gerrit_http_port + "/a/" + "changes/?q=" + gerrit_request
    r = requests.get(url, auth = HTTPDigestAuth(gerrit_user, gerrit_pass), timeout=None, proxies = None)
    json_changes = json.loads(r.text[4:]) #We have to remove ")]}'" from the beginning of the response
except URLError, e:
        print 'REST error:', e

for change in json_changes:
    changes_id_list.append(change["id"])

#Call gerrit_REST_API
for change in changes_id_list:
    try:
        url = "http://" + gerrit_url + ":" + gerrit_http_port + "/a/" + "changes/" + change + "/detail"
        r = requests.get(url, auth = HTTPDigestAuth(gerrit_user, gerrit_pass), timeout=None, proxies = None)

        #We have to remove ")]}'" from the beginning of the response
        data = json.loads(r.text[4:])
        # We take the first message as commit_date
        commit_start_date = parseDate(data["messages"][0]["date"][0:19])
        for message in data["messages"]:
            if "successfully merged" in message["message"] or "successfully rebased" in message["message"]:
                commit_merge_date = parseDate(message["date"][0:19])
                commits_list.append(Commit(commit_start_date, commit_merge_date))
    except URLError, e:
        print 'REST error:', e
        
print str(len(commits_list)), str(len(changes_id_list))

for commit in commits_list:
    print commit

latency = [commit.latency() for commit in commits_list]
print latency